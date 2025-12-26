from llm.agents.base_agent import BaseValidator, Message, ValidationResult
from llm.models.llm_models import LLMModel
from llm.models.structure import StructureInput, StructureOutput


VALIDATOR_SYSTEM_PROMPT = """Ты старший инженер по нагрузочному тестированию, проверяющий работу младшего коллеги.

Тебе дают:
1. Задачу, которую поставили коллеге (system prompt + user prompt с трафиком)
2. Историю общения (если были итерации исправлений)
3. Последний ответ коллеги — JSON с транзакциями

## Твоя задача

Проверить качество разбиения трафика на транзакции.

## Алгоритм проверки

### Шаг 1: Проверка покрытия
Посчитай: первая транзакция start_index должен быть 0, последняя end_index должен быть (total - 1).
Для каждой пары соседних транзакций: tx[i].end_index + 1 == tx[i+1].start_index
Если есть пропуски — это ОШИБКА.

### Шаг 2: Проверка пересечений  
Для каждой пары: tx[i].end_index < tx[i+1].start_index
Если нет — это ОШИБКА.

### Шаг 3: Проверка логичности границ
Посмотри на start_index каждой транзакции (кроме первой).
Запрос на этом индексе должен быть "якорным" — начало нового действия:
- GET на страницу (HTML, не статика)
- POST формы
- Смена раздела приложения

Если start_index указывает на статику (.css, .js, .png) — это МОЖЕТ БЫТЬ ошибкой.

### Шаг 4: Проверка имён
Имена должны отражать действие. Формат: S{XX}_{YY}_{Action}

## КРИТИЧЕСКИ ВАЖНО

⚠️ НЕ ВЫДУМЫВАЙ ОШИБКИ!

- Если tx.end_index = 32 и это ПРАВИЛЬНО — НЕ пиши "должно быть 32, а не 32"
- Если всё покрыто и логично — отвечай VALID
- Сомневаешься? Значит это НЕ ошибка.
- Перед тем как написать ошибку — убедись что РЕАЛЬНО нашёл проблему с КОНКРЕТНЫМИ индексами

## Формат ответа

VALID (если всё корректно):
```
VALID

Проверка пройдена:
- Покрытие: индексы 0-165 полностью покрыты
- Пересечения: нет
- Границы: логичные (S01_02 начинается с POST /login на индексе 16)
```

INVALID (ТОЛЬКО если нашёл РЕАЛЬНУЮ проблему):
```
INVALID

Ошибки:
- Пропущены индексы 45-50 (между S01_02 end=44 и S01_03 start=51)

Рекомендации:
- Расширить S01_02 до end_index=50 или S01_03 до start_index=45
```

Начни ответ со слова VALID или INVALID."""


class StructureValidator(BaseValidator[StructureOutput]):
    
    def __init__(
        self,
        original_input: StructureInput,
        worker_system_prompt: str,
        worker_history: list[Message] | None = None,
        llm=None,
        model: LLMModel = LLMModel.GPT_4O,
    ):
        super().__init__(
            name="StructureValidator",
            system_prompt=VALIDATOR_SYSTEM_PROMPT,
            llm=llm,
            model=model,
            temperature=0.0,
        )
        self.original_input = original_input
        self.worker_system_prompt = worker_system_prompt
        self.worker_history = worker_history or []
    
    def update_worker_history(self, history: list[Message]):
        self.worker_history = history
    
    def _build_user_prompt(self, input_data: StructureOutput) -> str:
        entries_text = self._format_entries(self.original_input.entries)
        transactions_text = self._format_transactions(input_data)
        
        prompt = f"""## Задача, поставленная коллеге

### System prompt коллеги:
{self.worker_system_prompt}

### User prompt (запрос с трафиком):

Сценарий #{self.original_input.scenario_number}

Список HTTP запросов (всего {len(self.original_input.entries)}, индексы 0-{len(self.original_input.entries) - 1}):

{entries_text}
"""
        
        if self.original_input.user_hints:
            prompt += f"""
Подсказки пользователя:
{self.original_input.user_hints}
"""
        
        if len(self.worker_history) > 2:
            prompt += "\n## История исправлений\n\n"
            for i, msg in enumerate(self.worker_history[:-1]):
                role_name = "Коллега" if msg.role == "assistant" else "Feedback"
                prompt += f"### {role_name} (итерация {(i // 2) + 1}):\n{msg.content[:500]}{'...' if len(msg.content) > 500 else ''}\n\n"
        
        prompt += f"""
## Последний ответ коллеги (требует проверки)

{transactions_text}

## Твоя задача

1. Проанализируй трафик САМОСТОЯТЕЛЬНО
2. Сравни своё понимание с ответом коллеги
3. Укажи конкретные ошибки если есть
4. Дай конкретные рекомендации по исправлению

Начни ответ с VALID или INVALID."""
        
        return prompt
    
    def _format_entries(self, entries: list) -> str:
        lines = []
        for entry in entries:
            lines.append(f"[{entry.index}] {entry.method} {entry.path} → {entry.status_code}")
        return "\n".join(lines)
    
    def _format_transactions(self, output: StructureOutput) -> str:
        lines = ["```json", "["]
        for i, tx in enumerate(output.transactions):
            comma = "," if i < len(output.transactions) - 1 else ""
            lines.append(f'  {{"name": "{tx.name}", "start_index": {tx.start_index}, "end_index": {tx.end_index}, "description": "{tx.description}"}}{comma}')
        lines.append("]")
        lines.append("```")
        return "\n".join(lines)
    
    def _parse_response(self, response: str) -> ValidationResult:
        lines = response.strip().split("\n")
        
        first_line = lines[0].strip().upper() if lines else ""
        is_valid = first_line == "VALID"
        
        errors = []
        suggestions = []
        current_section = None
        
        for line in lines[1:]:
            line_stripped = line.strip()
            if not line_stripped:
                continue
            
            line_lower = line_stripped.lower()
            if "ошибк" in line_lower or "error" in line_lower:
                current_section = "errors"
                continue
            elif "рекомендац" in line_lower or "suggestion" in line_lower or "предложен" in line_lower:
                current_section = "suggestions"
                continue
            
            if line_stripped.startswith("-") or line_stripped.startswith("•") or line_stripped.startswith("*"):
                content = line_stripped.lstrip("-•*").strip()
                if current_section == "errors":
                    errors.append(content)
                elif current_section == "suggestions":
                    suggestions.append(content)
                elif not is_valid:
                    errors.append(content)
        
        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            suggestions=suggestions,
        )
