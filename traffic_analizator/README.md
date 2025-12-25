# Traffic Analyzer

Анализатор трафика для автоматического поиска корреляций между запросами и ответами.

## Назначение

Модуль решает проблему ручной параметризации скриптов нагрузочного тестирования. Имея записанный трафик (HAR, SAZ, JTL), анализатор автоматически находит:

- Какие данные в запросах пришли из предыдущих ответов
- Откуда именно извлечь эти данные (JSON, HTML, заголовки, cookies)
- Какой экстрактор использовать (JSONPath, Regex)

## Установка

Модуль является частью проекта и не требует отдельной установки.

## Быстрый старт

```python
har = parse_har("recorded_traffic.har")
report = analyze_har(har)

print(report.to_str())
```

## Использование

### Базовый анализ

```python
har = parse_har("traffic.har")
report = analyze_har(har)

# Человекочитаемый отчёт
print(report.to_str())

# Программный доступ к данным
print(f"Найдено корреляций: {len(report.correlations)}")
print(f"Не разрешено: {len(report.unresolved)}")
```

### Параметры анализа

```python
report = analyze_har(
    har,
    min_value_length=4,      # Минимальная длина значения для поиска (по умолчанию 4)
    search_window=50,        # Искать только в N предыдущих ответах (None = все)
    ignore_cookies=True,     # Игнорировать cookies
)
```

### Работа с SAZ (Fiddler)

```python
saz = parse_saz("capture.saz")
har = convert_saz_to_har(saz)
report = analyze_har(har)
```

### Работа с JTL (JMeter)

```python
jtl = parse_jtl("results.jtl")
har = convert_jtl_to_har(jtl)
report = analyze_har(har)
```

## Структура отчёта

### AnalysisReport

| Поле | Тип | Описание |
|------|-----|----------|
| `request_data_points` | `list[RequestDataPoint]` | Все извлечённые данные из запросов |
| `response_data_points` | `list[ResponseDataPoint]` | Все извлечённые данные из ответов |
| `correlations` | `list[Correlation]` | Найденные связи запрос ↔ ответ |
| `unresolved` | `list[RequestDataPoint]` | Данные без найденного источника |

### Correlation

```python
correlation.request_point   # Данные из запроса
correlation.response_point  # Источник данных в ответе
correlation.match_type      # EXACT | CONTAINS | COMPOSITE
```

### ExtractorHint

Каждый `ResponseDataPoint` содержит `extractor_hint` — подсказку какой экстрактор использовать:

| Класс | Описание |
|-------|----------|
| `JsonExtractorHint` | JSONPath выражение |
| `RegexExtractorHint` | Регулярное выражение |
| `HeaderExtractorHint` | Извлечение из заголовка |
| `CookieExtractorHint` | Извлечение из Set-Cookie |

## Пример вывода

```
================================================================================
ОТЧЁТ АНАЛИЗА ТРАФИКА
================================================================================

Всего точек данных в запросах: 245
Всего точек данных в ответах: 892
Найдено корреляций: 12
Не разрешено (статика или генерируется на клиенте): 18

--------------------------------------------------------------------------------
КОРРЕЛЯЦИИ (требуют параметризации)
--------------------------------------------------------------------------------

1. [EXACT] requesttoken
  Запрос #5: POST /index.php/apps/files/ajax/upload.php
    Расположение: header
    Значение: abc123def456...
  Источник #2: GET /index.php
    Расположение: response_html
    Экстрактор: Regex: data-requesttoken="([^"]*)"

2. [EXACT] access_token
  Запрос #8: GET /api/user/profile
    Расположение: header
    Значение: eyJhbGciOiJIUzI1NiIs...
  Источник #4: POST /api/auth/login
    Расположение: response_json
    Экстрактор: JSONPath: $.data.access_token

--------------------------------------------------------------------------------
НЕ РАЗРЕШЕНО (проверьте вручную)
--------------------------------------------------------------------------------

1. [query_param] timestamp
   Запрос #3: GET /api/events
   Значение: 1703505600

================================================================================
```

## Интеграция с JMeter

Для преобразования `ExtractorHint` в JMeter элементы используйте конвертер:

```python
from traffic_analyzer import analyze_har
from jmx_builder.converters import convert_hint

report = analyze_har(har)

for correlation in report.correlations:
    hint = correlation.response_point.extractor_hint
    hint.variable_name = correlation.request_point.name
    
    # Получаем готовый JMeter элемент
    extractor = convert_hint(hint)
    
    # Добавляем к HTTP Sampler
    http_sampler.children.append(extractor)
```

## Алгоритм работы

1. **Извлечение данных из запросов** (`TrafficExtractor`)
   - Headers (кроме стандартных: Host, User-Agent, Accept...)
   - Query параметры
   - Form параметры
   - JSON body (рекурсивно с JSONPath)
   - Cookies (опционально)

2. **Извлечение данных из ответов** (`TrafficExtractor`)
   - Headers (кроме стандартных: Date, Server, Content-Type...)
   - Set-Cookie
   - JSON body (рекурсивно с JSONPath)
   - HTML (input fields, meta tags, data-атрибуты)

3. **Поиск корреляций** (`TrafficCorrelator`)
   - Для каждого значения из запроса N ищем в ответах с индексом < N
   - Типы совпадений: EXACT, CONTAINS, COMPOSITE (для значений вида `123;456;789`)
   - Фильтрация статических значений (true/false, page=1, content-type...)

## Расширение

### Добавление нового ExtractorHint

1. Создать класс в `traffic_analyzer/extractors/`:

```python
# boundary_extractor.py
from dataclasses import dataclass
from traffic_analyzer.extractors.base import ExtractorHint

@dataclass
class BoundaryExtractorHint(ExtractorHint):
    left_boundary: str = ""
    right_boundary: str = ""
    
    def to_str(self) -> str:
        return f"Boundary: {self.left_boundary}...{self.right_boundary}"
```

2. Экспортировать в `__init__.py`

3. Добавить конвертер в `jmx_builder/converters/hint_converter.py`

4. Интегрировать обработку в TrafficExtractor