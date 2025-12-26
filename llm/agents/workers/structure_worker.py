import json

from llm.agents.base_agent import BaseWorker
from llm.models.llm_models import LLMModel
from llm.models.structure import StructureInput, StructureOutput, TransactionDefinition


STRUCTURE_WORKER_SYSTEM_PROMPT = """Ты эксперт по анализу HTTP трафика для нагрузочного тестирования.

Твоя задача — разбить список HTTP запросов на логические транзакции (шаги пользователя).

## Ключевое понимание

**Транзакция = действие пользователя + ВСЕ последующие запросы до следующего действия**

Пример: пользователь нажал "Войти" → браузер отправил POST /login → сервер ответил редиректом → браузер загрузил /dashboard → загрузились CSS, JS, картинки dashboard'а.
ВСЁ ЭТО — одна транзакция "Login", не только POST /login!

## Алгоритм анализа

### Шаг 1: Найди ВСЕ якорные запросы

Якорь — это запрос, который ИНИЦИИРУЕТ новое действие пользователя.

**Типы якорей (в порядке приоритета):**

1. **POST/PUT/DELETE на формы и API** — всегда явное действие:
   - POST /login, POST /register, POST /submit
   - PUT /api/user/settings, DELETE /api/item/123
   
2. **GET с редиректом (302/301) на новый раздел** — переход:
   - GET / → 302 → перенаправляет на /login или /dashboard
   
3. **GET на корневую страницу нового раздела** — навигация:
   - GET /dashboard (после логина)
   - GET /gallery, GET /settings, GET /admin
   - GET /apps/files/, GET /apps/gallery/
   
4. **Смена базового пути** — переход между разделами:
   - Был /apps/files/* → стал /apps/gallery/* = новая транзакция

**НЕ являются якорями:**
- Статика: .css, .js, .png, .jpg, .svg, .woff, .ico, .map
- AJAX подгрузка данных: /api/*, /ajax/*, ?ajax=1
- Повторные запросы к тому же разделу
- Запросы к CDN, внешним сервисам

### Шаг 2: Определи границы каждой транзакции

**ВАЖНО: Транзакция ЗАКАНЧИВАЕТСЯ перед следующим якорем, а не на самом якоре!**

```
Якорь A (индекс 0)     → start транзакции 1
  ↓ запросы...
  ↓ запросы...         → всё это транзакция 1  
  ↓ запросы (индекс 31)→ end транзакции 1
Якорь B (индекс 32)    → start транзакции 2
  ↓ запросы...
  ↓ запросы (индекс 99)→ end транзакции 2
Якорь C (индекс 100)   → start транзакции 3
```

Формула:
- tx[i].start_index = индекс якоря i
- tx[i].end_index = индекс якоря (i+1) - 1

### Шаг 3: Сопоставь с подсказками пользователя

Если даны hints, проверь соответствие:
- "OpenHomePage" → первый GET на главную (/ или /index)
- "Login" → POST /login И ВСЁ что загружается после успешного входа
- "OpenGallery" → GET /gallery или /apps/gallery И всё что подгружается
- Количество транзакций = количество hints

### Шаг 4: Обработка неявных переходов

Если нет явного якоря, ищи косвенные признаки:
- Резкая смена типа запросов (были статика → пошли API)
- Изменение паттерна URL (был /api/users/* → стал /api/files/*)
- Появление нового контекста в пути (/gallery/album/123 → /gallery/album/456)

### Шаг 5: Проверь себя

1. Первая транзакция: start_index = 0
2. Последняя транзакция: end_index = (total - 1)
3. Нет пропусков: tx[i].end_index + 1 = tx[i+1].start_index
4. Нет пересечений: tx[i].end_index < tx[i+1].start_index
5. Количество транзакций соответствует hints (если даны)

## Формат ответа

```json
[
  {"name": "S01_01_OpenHomePage", "start_index": 0, "end_index": 31, "description": "Открытие главной страницы и загрузка ресурсов"},
  {"name": "S01_02_Login", "start_index": 32, "end_index": 99, "description": "POST авторизации и загрузка dashboard после входа"}
]
```

## Примеры разбора

**Пример 1: Логин**
```
[30] GET /core/img/logo.svg → 200      ← ещё OpenHomePage
[31] GET /core/fonts/font.woff → 200   ← ещё OpenHomePage (end=31)
[32] POST /login → 302                 ← ЯКОРЬ! start Login
[33] GET /index.php/apps/files → 200   ← часть Login (редирект после входа)
[34] GET /core/css/dashboard.css → 200 ← часть Login (загрузка dashboard)
...
[99] GET /apps/files/img/icon.png → 200 ← ещё Login (end=99)
[100] GET /apps/gallery → 200           ← ЯКОРЬ! start OpenGallery
```

**Пример 2: Неявный переход**
```
[50] GET /api/files/list → 200         ← работа с файлами
[51] GET /api/files/info/123 → 200     ← работа с файлами
[52] GET /apps/gallery → 200           ← ЯКОРЬ! (смена раздела files→gallery)
[53] GET /api/gallery/albums → 200     ← галерея
```"""


class StructureWorker(BaseWorker[StructureInput, StructureOutput]):
    
    SYSTEM_PROMPT = STRUCTURE_WORKER_SYSTEM_PROMPT
    
    def __init__(
        self,
        llm=None,
        model: LLMModel = LLMModel.GPT_4O,
    ):
        super().__init__(
            name="StructureWorker",
            system_prompt=STRUCTURE_WORKER_SYSTEM_PROMPT,
            llm=llm,
            model=model,
            temperature=0.0,
        )
    
    def _build_user_prompt(self, input_data: StructureInput) -> str:
        entries_text = self._format_entries(input_data.entries)
        
        prompt = f"""Сценарий #{input_data.scenario_number}

## Список HTTP запросов

{entries_text}

Всего запросов: {len(input_data.entries)} (индексы 0-{len(input_data.entries) - 1})
"""
        
        if input_data.user_hints:
            prompt += f"""
## Подсказки пользователя

{input_data.user_hints}
"""
        
        prompt += """
## Задача

Разбей запросы на логические транзакции. Убедись что:
- Все индексы от 0 до {max_index} покрыты
- Транзакции не пересекаются
- Формат JSON корректный
""".format(max_index=len(input_data.entries) - 1)
        
        return prompt
    
    def _format_entries(self, entries: list) -> str:
        lines = []
        for entry in entries:
            lines.append(f"[{entry.index}] {entry.method} {entry.path} → {entry.status_code}")
        return "\n".join(lines)
    
    def _parse_response(self, response: str) -> StructureOutput:
        json_str = response.strip()
        
        if "```json" in json_str:
            start = json_str.find("```json") + 7
            end = json_str.find("```", start)
            json_str = json_str[start:end].strip()
        elif "```" in json_str:
            start = json_str.find("```") + 3
            end = json_str.find("```", start)
            json_str = json_str[start:end].strip()
        
        start_bracket = json_str.find("[")
        end_bracket = json_str.rfind("]")
        if start_bracket != -1 and end_bracket != -1:
            json_str = json_str[start_bracket:end_bracket + 1]
        
        data = json.loads(json_str)
        
        transactions = []
        for item in data:
            tx = TransactionDefinition(
                name=item["name"],
                start_index=item["start_index"],
                end_index=item["end_index"],
                description=item.get("description", ""),
            )
            transactions.append(tx)
        
        transactions.sort(key=lambda x: x.start_index)
        
        return StructureOutput(transactions=transactions)