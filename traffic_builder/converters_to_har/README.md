# Converters

Конвертеры для преобразования моделей между модулями.

## ExtractorHintConverter

Конвертирует `ExtractorHint` из `traffic_analyzer` в JMeter `TreeElement`.

### Поддерживаемые преобразования

| ExtractorHint | JMeter Element |
|---------------|----------------|
| `JsonExtractorHint` | `JSONPostProcessor` |
| `RegexExtractorHint` | `RegexExtractor` |
| `HeaderExtractorHint` | `RegexExtractor` (field: Response Headers) |
| `CookieExtractorHint` | `RegexExtractor` (field: Response Headers) |

### Использование

```python
from traffic_builder.har_parsers.har_parser import parse_har
from traffic_analyzer import analyze_har
from jmx_builder.converters import convert_hint

har = parse_har("traffic.har")
report = analyze_har(har)

for correlation in report.correlations:
    hint = correlation.response_point.extractor_hint
    
    # Устанавливаем имя переменной
    hint.variable_name = "auth_token"
    
    # Конвертируем в JMeter элемент
    extractor = convert_hint(hint)
    
    # Добавляем к HTTP Sampler
    http_sampler.children.append(extractor)
```

### Расширение

Для добавления нового типа экстрактора:

1. Создать класс в `traffic_analyzer/extractors/`:

```python
# traffic_analyzer/extractors/boundary_extractor.py
from dataclasses import dataclass
from traffic_analyzer.extractors.base import ExtractorHint

@dataclass
class BoundaryExtractorHint(ExtractorHint):
    left_boundary: str = ""
    right_boundary: str = ""
    
    def to_str(self) -> str:
        return f"Boundary: {self.left_boundary}...{self.right_boundary}"
```

2. Добавить обработку в `hint_converter.py`:

```python
from traffic_analyzer.extractors import BoundaryExtractorHint
from jmx_builder.models.tree import BoundaryExtractor

# В методе convert()
elif isinstance(hint, BoundaryExtractorHint):
    return ExtractorHintConverter._convert_boundary(hint)

@staticmethod
def _convert_boundary(hint: BoundaryExtractorHint) -> BoundaryExtractor:
    variable_name = hint.variable_name or "extracted_boundary"
    
    extractor = BoundaryExtractor.create_default(testname=f"Extract {variable_name}")
    extractor.set_refname(variable_name)
    extractor.set_lboundary(hint.left_boundary)
    extractor.set_rboundary(hint.right_boundary)
    
    return extractor
```