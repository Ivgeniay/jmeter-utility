import json
import re

from llm.agents.base_agent import BaseValidator, BaseWorker, Message, ValidationResult
from llm.models.correlation import *
from llm.models.llm_models import LLMModel


CORRELATION_WORKER_SYSTEM_PROMPT = """Ты эксперт по корреляции данных в JMeter скриптах для нагрузочного тестирования.

## Твоя задача

Проанализировать ситуацию с динамическими данными и предложить решение для JMeter:
1. Как извлечь данные из ответа (JSONPath, Regex, XPath)
2. Нужна ли пост-обработка (разбивка на чанки, объединение)
3. Нужен ли контроллер (Loop, ForEach)
4. Как параметризовать целевые запросы

## Контекст JMeter

### Элементы извлечения

**JSON Extractor:**
- match_nr="1" → одно значение в `${var}`
- match_nr="-1" → все значения в `${var_1}`, `${var_2}`, ..., `${var_matchNr}` содержит количество

**Regular Expression Extractor:** аналогично JSON Extractor

### Переменные JMeter
- `${var}` — значение переменной
- `${var_1}`, `${var_2}` — при match_nr=-1
- `${var_matchNr}` — количество найденных значений
- `${__intSum(${__jm__LoopName__idx},1)}` — индекс Loop + 1 (Loop начинается с 0!)
- `${__V(var_${index})}` — динамическое имя переменной

### Контроллеры

**Loop Controller:**
- Повторяет содержимое N раз
- `${__jm__LoopControllerName__idx}` — текущий индекс (НАЧИНАЕТСЯ С 0!)
- Для доступа к var_1, var_2 нужен `${__intSum(${__jm__Loop__idx},1)}`

**ForEach Controller:**
- Итерирует по `${inputVar_1}`, `${inputVar_2}`, ...
- Выдаёт текущее значение в `${outputVar}`
- Имя входной переменной БЕЗ суффикса _1, _2

## КРИТИЧЕСКИ ВАЖНО: Логика контроллеров

### При использовании Loop/ForEach:
1. **ОДИН sampler выполняется N раз** — не N разных sampler'ов!
2. **parameter_replacements содержит ОДИН entry** — первый из группы одинаковых
3. Остальные одинаковые запросы УДАЛЯЮТСЯ из скрипта
4. Поле `entries_to_remove` указывает какие entry удалить

### Пример:
Было: entry 55, 60, 65 — три одинаковых GET /thumbnails?ids=...
Стало: entry 55 в Loop Controller (выполнится 3 раза), entry 60 и 65 удаляются

## Алгоритм анализа

### Шаг 1: Определи тип извлечения
- JSON ответ → JSONPath
- HTML/XML → XPath или Regex
- Произвольный текст → Regex

### Шаг 2: Определи сложность сценария

**Simple (простой):** 
- 1 значение извлекается, 1 раз используется
- Решение: Extractor с match_nr="1", один replacement
- Пример: токен авторизации в одном запросе

**Simple_reused (простой, многократное использование):**
- 1 значение извлекается, используется в НЕСКОЛЬКИХ РАЗНЫХ запросах
- Решение: Extractor с match_nr="1", НЕСКОЛЬКО replacements, БЕЗ контроллера
- НЕ нужен Loop/ForEach! Каждый запрос уникальный, просто использует ту же переменную
- entries_to_remove = [] (ничего не удаляем!)
- Пример: CSRF токен используется в 7 разных POST запросах

**Multiple (множественный):**
- N значений извлекается, ВСЕ используются в ОДНОМ запросе
- Решение: Extractor с match_nr="-1" + JSR223 для конкатенации
- Пример: ids=1;2;3;4;5 все сразу

**Chunked (чанками):**
- N значений извлекается, используются ПОРЦИЯМИ в НЕСКОЛЬКИХ ОДИНАКОВЫХ запросах
- Решение: Extractor + JSR223 chunk + Loop Controller + ОДИН sampler
- Пример: 21 id → 3 запроса по 7 штук

**Iterated (итеративный):**
- N значений извлекается, КАЖДОЕ в ОТДЕЛЬНОМ ОДИНАКОВОМ запросе
- Решение: Extractor + ForEach Controller + ОДИН sampler
- Пример: 3 id → 3 запроса по 1 штуке

### ВАЖНО: Как отличить simple_reused от iterated?

**simple_reused:**
- values_total = 1 (ОДНО значение)
- usage_count = N (много запросов)
- Все запросы РАЗНЫЕ (разные URL, разные действия)
- Пример: requesttoken используется в POST /upload, POST /delete, POST /move

**iterated:**
- values_total = N (много значений)
- usage_count = N (много запросов)
- Все запросы ОДИНАКОВЫЕ (один URL, одно действие, разные данные)
- Пример: id=123, id=456, id=789 в GET /item/{id}

### Шаг 3: Сгенерируй уникальное имя переменной
Формат: `{смысловое_имя}_{короткий_хеш}`
Примеры: `nodeids_gallery_0xA1`, `token_auth_0xF3`

### Шаг 4: Напиши Groovy скрипт (если нужен)

**Для chunk_split (ПРАВИЛЬНЫЙ способ):**
```groovy
def matchNr = vars.get("varName_matchNr")?.toInteger() ?: 0
def values = []
for (int i = 1; i <= matchNr; i++) {
    values.add(vars.get("varName_" + i))
}
def chunkSize = 7
def chunks = values.collate(chunkSize).collect { it.join(";") }
vars.put("varName_chunks_count", chunks.size().toString())
chunks.eachWithIndex { chunk, idx ->
    vars.put("varName_chunk_" + (idx + 1), chunk)
}
```

**Для join_values:**
```groovy
def matchNr = vars.get("varName_matchNr")?.toInteger() ?: 0
def values = []
for (int i = 1; i <= matchNr; i++) {
    values.add(vars.get("varName_" + i))
}
vars.put("varName_joined", values.join(";"))
```

## Формат ответа

```json
{
  "extractor": {
    "type": "jsonpath",
    "variable_name": "nodeids_gallery_0xA1",
    "expression": "$.files[*].nodeid",
    "match_nr": "-1",
    "default_value": "NOT_FOUND"
  },
  "post_processing": {
    "type": "chunk_split",
    "script_language": "groovy",
    "script_code": "... правильный groovy код ...",
    "chunk_size": 7,
    "delimiter": ";",
    "input_variable": "nodeids_gallery_0xA1",
    "output_variable": "nodeids_gallery_chunk"
  },
  "controller": {
    "type": "loop",
    "loop_count_variable": "nodeids_gallery_0xA1_chunks_count",
    "controller_name": "Loop_thumbnails"
  },
  "parameter_replacements": [
    {
      "entry_index": 55,
      "parameter_name": "ids",
      "usage_type": "query",
      "variable_reference": "${__V(nodeids_gallery_chunk_${__intSum(${__jm__Loop_thumbnails__idx},1)})}"
    }
  ],
  "entries_to_remove": [60, 65],
  "reasoning": "21 nodeid разбиваем на 3 чанка по 7. Loop выполняет один sampler 3 раза.",
  "complexity": "chunked"
}
```

## Примеры

### Пример 1: Простое извлечение токена
```json
{
  "extractor": {"type": "jsonpath", "variable_name": "auth_token_0xF1", "expression": "$.token", "match_nr": "1", "default_value": ""},
  "post_processing": null,
  "controller": null,
  "parameter_replacements": [{"entry_index": 5, "parameter_name": "Authorization", "usage_type": "header", "variable_reference": "Bearer ${auth_token_0xF1}"}],
  "entries_to_remove": [],
  "reasoning": "Простое извлечение одного токена",
  "complexity": "simple"
}
```

### Пример 2: CSRF токен в нескольких разных запросах (simple_reused)
Входные данные: 1 токен (values_total=1), используется в 7 РАЗНЫХ запросах

```json
{
  "extractor": {"type": "regex", "variable_name": "requesttoken_0xA1", "expression": "data-requesttoken=\"([^\"]*)\"", "match_nr": "1", "default_value": ""},
  "post_processing": null,
  "controller": null,
  "parameter_replacements": [
    {"entry_index": 102, "parameter_name": "requesttoken", "usage_type": "header", "variable_reference": "${requesttoken_0xA1}"},
    {"entry_index": 103, "parameter_name": "requesttoken", "usage_type": "header", "variable_reference": "${requesttoken_0xA1}"},
    {"entry_index": 104, "parameter_name": "requesttoken", "usage_type": "header", "variable_reference": "${requesttoken_0xA1}"},
    {"entry_index": 105, "parameter_name": "requesttoken", "usage_type": "header", "variable_reference": "${requesttoken_0xA1}"},
    {"entry_index": 106, "parameter_name": "requesttoken", "usage_type": "header", "variable_reference": "${requesttoken_0xA1}"},
    {"entry_index": 107, "parameter_name": "requesttoken", "usage_type": "header", "variable_reference": "${requesttoken_0xA1}"},
    {"entry_index": 108, "parameter_name": "requesttoken", "usage_type": "header", "variable_reference": "${requesttoken_0xA1}"}
  ],
  "entries_to_remove": [],
  "reasoning": "Один CSRF токен используется в 7 разных запросах. Контроллер НЕ нужен — запросы разные!",
  "complexity": "simple_reused"
}
```

### Пример 3: ForEach — каждый ID отдельно
Входные данные: 3 запроса (entry 21, 22, 23) с разными id, values_total=3

```json
{
  "extractor": {"type": "jsonpath", "variable_name": "item_ids_0xB2", "expression": "$.items[*].id", "match_nr": "-1", "default_value": ""},
  "post_processing": null,
  "controller": {
    "type": "foreach",
    "foreach_input_variable": "item_ids_0xB2",
    "foreach_output_variable": "current_item_id",
    "controller_name": "ForEach_items"
  },
  "parameter_replacements": [{"entry_index": 21, "parameter_name": "id", "usage_type": "path", "variable_reference": "${current_item_id}"}],
  "entries_to_remove": [22, 23],
  "reasoning": "3 id используются в 3 одинаковых запросах. ForEach выполняет один sampler 3 раза.",
  "complexity": "iterated"
}
```

### Пример 3: Чанки по 7 штук
Входные данные: 3 запроса (entry 55, 60, 65) с ids по 7 штук каждый

```json
{
  "extractor": {"type": "jsonpath", "variable_name": "nodeids_0xC3", "expression": "$.files[*].nodeid", "match_nr": "-1", "default_value": ""},
  "post_processing": {
    "type": "chunk_split",
    "script_language": "groovy",
    "script_code": "def matchNr = vars.get('nodeids_0xC3_matchNr')?.toInteger() ?: 0\\ndef values = []\\nfor (int i = 1; i <= matchNr; i++) { values.add(vars.get('nodeids_0xC3_' + i)) }\\ndef chunks = values.collate(7).collect { it.join(';') }\\nvars.put('nodeids_0xC3_chunks_count', chunks.size().toString())\\nchunks.eachWithIndex { chunk, idx -> vars.put('nodeids_0xC3_chunk_' + (idx + 1), chunk) }",
    "chunk_size": 7,
    "delimiter": ";",
    "input_variable": "nodeids_0xC3",
    "output_variable": "nodeids_0xC3_chunk"
  },
  "controller": {
    "type": "loop",
    "loop_count_variable": "nodeids_0xC3_chunks_count",
    "controller_name": "Loop_thumbnails"
  },
  "parameter_replacements": [{"entry_index": 55, "parameter_name": "ids", "usage_type": "query", "variable_reference": "${__V(nodeids_0xC3_chunk_${__intSum(${__jm__Loop_thumbnails__idx},1)})}"}],
  "entries_to_remove": [60, 65],
  "reasoning": "21 nodeid → 3 чанка по 7. Один sampler в Loop выполнится 3 раза.",
  "complexity": "chunked"
}
```
"""


class CorrelationWorker(BaseWorker[CorrelationInput, CorrelationOutput]):
    
    SYSTEM_PROMPT = CORRELATION_WORKER_SYSTEM_PROMPT
    
    def __init__(
        self,
        llm=None,
        model: LLMModel = LLMModel.GPT_4O,
    ):
        super().__init__(
            name="CorrelationWorker",
            system_prompt=CORRELATION_WORKER_SYSTEM_PROMPT,
            llm=llm,
            model=model,
            temperature=0.0,
        )
    
    def _build_user_prompt(self, input_data: CorrelationInput) -> str:
        target_info = self._format_targets(input_data.target_usages)
        response_preview = input_data.source_response_body[:2000]
        if len(input_data.source_response_body) > 2000:
            response_preview += "\n... (обрезано)"
        
        prompt = f"""## Ситуация для анализа

### Источник данных (откуда извлекаем)

Entry index: {input_data.source_entry_index}
Request: {input_data.source_request_path}
Content-Type: {input_data.source_content_type}

Response body:
```
{response_preview}
```

### Данные для извлечения

Пример значения: `{input_data.value_sample}`
Подсказка пути: `{input_data.value_path_hint}`
Всего значений: {input_data.values_total}

### Целевые запросы (куда используется)

{target_info}

Количество использований: {input_data.usage_count}
"""
        
        if input_data.transaction_name:
            prompt += f"\nТранзакция: {input_data.transaction_name}\n"
        
        prompt += """
### Задача

Проанализируй ситуацию и предложи решение:
1. Как извлечь данные (JSONPath/Regex/XPath)
2. Нужна ли пост-обработка
3. Нужен ли контроллер
4. Как параметризовать запросы

Ответь JSON в формате из инструкции."""
        
        return prompt
    
    def _format_targets(self, targets: list) -> str:
        lines = []
        for t in targets:
            lines.append(f"- Entry #{t.entry_index}: параметр `{t.parameter_name}` ({t.usage_type.value}), значений в запросе: {t.values_in_request}")
            if t.raw_value:
                preview = t.raw_value[:100] + "..." if len(t.raw_value) > 100 else t.raw_value
                lines.append(f"  Значение: `{preview}`")
        return "\n".join(lines)
    
    def _parse_response(self, response: str) -> CorrelationOutput:
        json_str = response.strip()
        
        if "```json" in json_str:
            start = json_str.find("```json") + 7
            end = json_str.find("```", start)
            json_str = json_str[start:end].strip()
        elif "```" in json_str:
            start = json_str.find("```") + 3
            end = json_str.find("```", start)
            json_str = json_str[start:end].strip()
        
        start_brace = json_str.find("{")
        end_brace = json_str.rfind("}")
        if start_brace != -1 and end_brace != -1:
            json_str = json_str[start_brace:end_brace + 1]
        
        data = json.loads(json_str)
        
        ext_data = data["extractor"]
        extractor = JMeterExtractor(
            type=ExtractionMethod(ext_data["type"]),
            variable_name=ext_data["variable_name"],
            expression=ext_data["expression"],
            match_nr=ext_data.get("match_nr", "1"),
            default_value=ext_data.get("default_value", ""),
        )
        
        post_processing = None
        if data.get("post_processing"):
            pp = data["post_processing"]
            post_processing = PostProcessingStep(
                type=PostProcessingType(pp["type"]),
                script_language=pp.get("script_language", "groovy"),
                script_code=pp.get("script_code", ""),
                description=pp.get("description", ""),
                chunk_size=pp.get("chunk_size", 0),
                delimiter=pp.get("delimiter", ";"),
                input_variable=pp.get("input_variable", ""),
                output_variable=pp.get("output_variable", ""),
            )
        
        controller = None
        if data.get("controller"):
            ctrl = data["controller"]
            controller = ControllerStep(
                type=ControllerType(ctrl["type"]),
                controller_name=ctrl.get("controller_name", ""),
                loop_count_variable=ctrl.get("loop_count_variable", ""),
                foreach_input_variable=ctrl.get("foreach_input_variable", ""),
                foreach_output_variable=ctrl.get("foreach_output_variable", ""),
                description=ctrl.get("description", ""),
            )
        
        replacements = []
        for rep in data.get("parameter_replacements", []):
            replacements.append(ParameterReplacement(
                entry_index=rep["entry_index"],
                parameter_name=rep.get("parameter_name", ""),
                usage_type=UsageType(rep.get("usage_type", "query")),
                variable_reference=rep["variable_reference"],
            ))
        
        entries_to_remove = data.get("entries_to_remove", [])
        
        return CorrelationOutput(
            extractor=extractor,
            post_processing=post_processing,
            controller=controller,
            parameter_replacements=replacements,
            entries_to_remove=entries_to_remove,
            reasoning=data.get("reasoning", ""),
            complexity=data.get("complexity", "simple"),
        )