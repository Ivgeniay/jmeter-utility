import json
import re
from llm.agents.base_agent import BaseValidator, Message, ValidationResult
from llm.models.correlation import ControllerType, CorrelationInput, CorrelationOutput, ExtractionMethod
from llm.models.llm_models import LLMModel


CORRELATION_VALIDATOR_SYSTEM_PROMPT = """Ты эксперт по валидации JMeter корреляций.

## Твоя задача

Проверить предложенное решение для корреляции данных в JMeter.

## Критерии проверки

### 1. Выражение извлечения
- JSONPath начинается с `$`
- Regex синтаксически корректен
- Выражение извлечёт ожидаемые данные из response

### 2. Groovy скрипт (если есть)
- Использует `vars.get("varName_matchNr")` для получения количества
- Использует цикл `for (int i = 1; i <= matchNr; i++)` для сбора значений
- НЕ использует несуществующий `varName_ALL`
- Переменные чанков нумеруются с 1: `chunk_1`, `chunk_2`, ...

### 3. Логика контроллеров (КРИТИЧЕСКИ ВАЖНО!)

**При Loop/ForEach Controller:**
- `parameter_replacements` должен содержать ОДИН entry (первый из группы)
- `entries_to_remove` должен содержать остальные entry из группы
- Количество replacements = 1, количество entries_to_remove = (всего - 1)

**Loop Controller:**
- `controller_name` задан (для формирования `__jm__ControllerName__idx`)
- `loop_count_variable` указывает на переменную с количеством чанков
- `variable_reference` использует `${__intSum(${__jm__NAME__idx},1)}` т.к. индекс с 0

**ForEach Controller:**
- `foreach_input_variable` задан (без суффиксов _1, _2)
- `foreach_output_variable` задан
- `variable_reference` использует `${foreach_output_variable}`

### 4. Соответствие паттерну использования
- chunk_size соответствует количеству значений в одном запросе
- Количество чанков = количество целевых запросов

### 5. Консистентность имён переменных
- Имя в extractor = имя в post_processing.input_variable
- Имя в post_processing.output_variable используется в variable_reference
- Имя контроллера в controller_name = имя в `__jm__NAME__idx`

## Частые ошибки

1. **Несколько replacements при Loop/ForEach** — должен быть ОДИН
2. **Пустой entries_to_remove** — должен содержать удаляемые entry
3. **Использование varName_ALL** — такой переменной нет, нужен цикл по _1, _2, ...
4. **Индекс без +1** — Loop idx начинается с 0, переменные с 1
5. **Несоответствие имён** — controller_name не совпадает с именем в __jm__

## Формат ответа

VALID:
```
VALID

Проверка пройдена:
- JSONPath корректен
- Groovy скрипт правильно собирает значения через _matchNr
- Один replacement (entry 55), entries_to_remove содержит [60, 65]
- Loop Controller с правильным индексированием
```

INVALID:
```
INVALID

Ошибки:
- parameter_replacements содержит 3 entry, должен быть 1 (первый из группы)
- entries_to_remove пуст, должен содержать [60, 65]
- Groovy использует несуществующий varName_ALL, нужен цикл по _matchNr
- variable_reference использует ${__jm__Loop__idx} без +1

Рекомендации:
- Оставить только entry 55 в parameter_replacements
- Добавить [60, 65] в entries_to_remove
- Исправить Groovy: собирать через цикл for (int i = 1; i <= matchNr; i++)
- Использовать ${__intSum(${__jm__Loop_thumbnails__idx},1)} для индекса
```

Начни ответ с VALID или INVALID."""


class CorrelationValidator(BaseValidator[CorrelationOutput]):
    
    def __init__(
        self,
        original_input: CorrelationInput,
        worker_system_prompt: str,
        worker_history: list[Message] | None = None,
        llm=None,
        model: LLMModel = LLMModel.GPT_4O,
    ):
        super().__init__(
            name="CorrelationValidator",
            system_prompt=CORRELATION_VALIDATOR_SYSTEM_PROMPT,
            llm=llm,
            model=model,
            temperature=0.0,
        )
        self.original_input = original_input
        self.worker_system_prompt = worker_system_prompt
        self.worker_history = worker_history or []
    
    def update_worker_history(self, history: list[Message]):
        self.worker_history = history
    
    def run(self, input_data: CorrelationOutput) -> ValidationResult:
        deterministic_result = self._deterministic_validation(input_data)
        
        if not deterministic_result.is_valid:
            return deterministic_result
        
        return super().run(input_data)
    
    def _deterministic_validation(self, output: CorrelationOutput) -> ValidationResult:
        errors = []
        suggestions = []
        
        if output.extractor.type == ExtractionMethod.JSONPATH:
            expr = output.extractor.expression
            if not expr.startswith("$"):
                errors.append(f"JSONPath должен начинаться с $, получено: {expr}")
        
        elif output.extractor.type == ExtractionMethod.REGEX:
            expr = output.extractor.expression
            try:
                re.compile(expr)
            except re.error as e:
                errors.append(f"Некорректный regex: {expr}, ошибка: {e}")
        
        if not output.extractor.variable_name:
            errors.append("variable_name не может быть пустым")
        elif not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', output.extractor.variable_name):
            errors.append(f"variable_name содержит недопустимые символы: {output.extractor.variable_name}")
        
        if output.post_processing:
            script = output.post_processing.script_code
            var_name = output.extractor.variable_name
            
            if "_ALL" in script:
                errors.append(f"Groovy использует несуществующий {var_name}_ALL. JMeter создаёт {var_name}_1, {var_name}_2, ... и {var_name}_matchNr")
                suggestions.append(f"Используй цикл: for (int i = 1; i <= vars.get('{var_name}_matchNr')?.toInteger(); i++) {{ values.add(vars.get('{var_name}_' + i)) }}")
            
            if output.post_processing.type.value == "chunk_split":
                if output.post_processing.chunk_size <= 0:
                    errors.append("chunk_size должен быть > 0")
                
                expected_chunk_size = self._get_expected_chunk_size()
                if expected_chunk_size and output.post_processing.chunk_size != expected_chunk_size:
                    errors.append(f"chunk_size={output.post_processing.chunk_size} не соответствует паттерну использования (по {expected_chunk_size} значений в запросе)")
                    suggestions.append(f"Установи chunk_size={expected_chunk_size}")
        
        if output.controller:
            ctrl = output.controller
            
            if ctrl.type == ControllerType.LOOP:
                if not ctrl.loop_count_variable:
                    errors.append("Loop Controller требует loop_count_variable")
                
                if not ctrl.controller_name:
                    errors.append("Loop Controller требует controller_name для формирования __jm__NAME__idx")
                    suggestions.append("Добавь controller_name, например 'Loop_thumbnails'")
                
                for rep in output.parameter_replacements:
                    ref = rep.variable_reference
                    if "__jm__" in ref and "__idx" in ref:
                        if "__intSum" not in ref and "+1" not in ref:
                            errors.append(f"Loop индекс начинается с 0, но переменные с 1. variable_reference '{ref}' не содержит +1")
                            suggestions.append("Используй ${__intSum(${__jm__NAME__idx},1)} или ${__V(var_${__intSum(${__jm__NAME__idx},1)})}")
            
            elif ctrl.type == ControllerType.FOREACH:
                if not ctrl.foreach_input_variable:
                    errors.append("ForEach Controller требует foreach_input_variable")
                if not ctrl.foreach_output_variable:
                    errors.append("ForEach Controller требует foreach_output_variable")
                    suggestions.append("Добавь foreach_output_variable, например 'current_item_id'")
                
                if ctrl.foreach_output_variable:
                    expected_ref = "${" + ctrl.foreach_output_variable + "}"
                    for rep in output.parameter_replacements:
                        if ctrl.foreach_output_variable not in rep.variable_reference:
                            errors.append(f"variable_reference '{rep.variable_reference}' не использует foreach_output_variable '{ctrl.foreach_output_variable}'")
                            suggestions.append(f"Используй {expected_ref} в variable_reference")
            
            target_count = len(self.original_input.target_usages)
            replacement_count = len(output.parameter_replacements)
            remove_count = len(output.entries_to_remove)
            
            if replacement_count > 1:
                errors.append(f"При использовании {ctrl.type.value} Controller parameter_replacements должен содержать 1 entry, получено {replacement_count}")
                first_entry = self.original_input.target_usages[0].entry_index if self.original_input.target_usages else "?"
                suggestions.append(f"Оставь только entry {first_entry} в parameter_replacements")
            
            if target_count > 1 and remove_count == 0:
                errors.append(f"entries_to_remove пуст, но есть {target_count} одинаковых запросов. Нужно удалить {target_count - 1} entry")
                entries_to_remove = [t.entry_index for t in self.original_input.target_usages[1:]]
                suggestions.append(f"Добавь entries_to_remove: {entries_to_remove}")
            
            if target_count > 1 and remove_count != target_count - 1:
                if remove_count > 0:
                    errors.append(f"entries_to_remove содержит {remove_count} entry, ожидается {target_count - 1}")
        
        if not output.parameter_replacements:
            errors.append("Нет parameter_replacements — данные извлекаются но не используются")
        
        if errors:
            return ValidationResult(is_valid=False, errors=errors, suggestions=suggestions)
        
        return ValidationResult(is_valid=True)
    
    def _get_expected_chunk_size(self) -> int | None:
        if self.original_input.target_usages:
            return self.original_input.target_usages[0].values_in_request
        return None
    
    def _build_user_prompt(self, input_data: CorrelationOutput) -> str:
        response_preview = self.original_input.source_response_body[:1500]
        if len(self.original_input.source_response_body) > 1500:
            response_preview += "\n... (обрезано)"
        
        target_info = self._format_targets(self.original_input.target_usages)
        
        prompt = f"""## Исходная задача

### Источник данных
Entry: {self.original_input.source_entry_index}
Request: {self.original_input.source_request_path}
Content-Type: {self.original_input.source_content_type}

Response:
```
{response_preview}
```

### Данные для извлечения
Пример: `{self.original_input.value_sample}`
Путь: `{self.original_input.value_path_hint}`
Всего значений: {self.original_input.values_total}

### Целевые запросы (всего {len(self.original_input.target_usages)})
{target_info}

## Предложенное решение

```json
{json.dumps(input_data.to_dict(), indent=2, ensure_ascii=False)}
```

## Задача

Проверь решение:
1. Выражение `{input_data.extractor.expression}` корректно?
2. Groovy скрипт правильно работает с переменными JMeter?
3. При Loop/ForEach: один replacement + entries_to_remove?
4. Индексирование учитывает что Loop idx начинается с 0?
5. Имена переменных консистентны?

Начни ответ с VALID или INVALID."""
        
        return prompt
    
    def _format_targets(self, targets: list) -> str:
        lines = []
        for t in targets:
            lines.append(f"- Entry #{t.entry_index}: `{t.parameter_name}` ({t.usage_type.value}), значений: {t.values_in_request}")
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