# JTL Parser & JTL-to-HAR Converter

Парсер для файлов JTL (JMeter Test Log) и конвертер в формат HAR (HTTP Archive).

## Возможности

### 1. Парсинг JTL файлов
- Полная поддержка формата JTL XML (Simple Data Writer)
- Парсинг всех атрибутов HTTP запросов
- Поддержка вложенных сэмплов (например, редиректы)
- Извлечение headers, cookies, response data
- Парсинг результатов assertions

### 2. Конвертация JTL → HAR
- Конвертация результатов JMeter в стандартный формат HAR
- Опциональное включение sub-samples (редиректов)
- Сохранение всех timing-данных
- Совместимость с HAR-анализаторами

## Установка

```bash
pip install pydantic>=2.0
```

## Использование

### Базовый парсинг JTL

```python
from traffic_builder.jtl_parser.jtl_parser import parse_jtl, get_all_samples

# Парсинг файла
test_results = parse_jtl('results.jtl')

# Получить все сэмплы
all_samples = get_all_samples(test_results)

# Вывести информацию
for sample in test_results.http_sample:
    print(f"{sample.label}: {sample.response_code} ({sample.elapsed}ms)")
```

### Получение failed запросов

```python
from traffic_builder.jtl_parser.jtl_parser import parse_jtl, get_failed_samples

test_results = parse_jtl('results.jtl')
failed = get_failed_samples(test_results)

for sample in failed:
    print(f"Failed: {sample.label} - {sample.response_code}")
```

### Конвертация в HAR

```python
from traffic_builder.jtl_parser.jtl_parser import parse_jtl
from traffic_builder.jtl_parser.jtl_to_har_converter import convert_jtl_to_har, save_har

# Парсинг JTL
test_results = parse_jtl('results.jtl')

# Конвертация в HAR (без sub-samples)
har_file = convert_jtl_to_har(test_results, include_sub_samples=False)

# Сохранение
save_har(har_file, 'output.har')
```

### Конвертация с редиректами

```python
# Включить sub-samples (редиректы) как отдельные entries
har_file = convert_jtl_to_har(test_results, include_sub_samples=True)
save_har(har_file, 'output_with_redirects.har')
```

### Анализ производительности

```python
from traffic_builder.jtl_parser.jtl_parser import parse_jtl, get_all_samples

test_results = parse_jtl('results.jtl')
samples = get_all_samples(test_results, include_sub_samples=False)

# Статистика
total_time = sum(s.elapsed for s in samples)
avg_time = total_time / len(samples)
success_count = sum(1 for s in samples if s.success)
success_rate = (success_count / len(samples)) * 100

print(f"Average response time: {avg_time:.2f}ms")
print(f"Success rate: {success_rate:.2f}%")

# Самый медленный запрос
slowest = max(samples, key=lambda s: s.elapsed)
print(f"Slowest: {slowest.label} ({slowest.elapsed}ms)")
```

### Фильтрация запросов

```python
from traffic_builder.jtl_parser.jtl_parser import parse_jtl, get_all_samples

test_results = parse_jtl('results.jtl')
all_samples = get_all_samples(test_results)

# Только GET запросы
get_requests = [s for s in all_samples if s.method == 'GET']

# Только редиректы (3xx)
redirects = [s for s in all_samples if s.response_code.startswith('3')]

# Медленные запросы (>1 секунды)
slow_requests = [s for s in all_samples if s.elapsed > 1000]

# Ошибки (5xx)
server_errors = [s for s in all_samples if s.response_code.startswith('5')]
```

## Структура данных

### HttpSample

Основная модель для HTTP запроса/ответа из JTL:

```python
class HttpSample:
    # Timing
    timestamp: int          # ts - Unix timestamp в миллисекундах
    elapsed: int           # t - общее время выполнения (ms)
    latency: int           # lt - latency (ms)
    connect_time: int      # ct - время соединения (ms)
    idle_time: int         # it - idle time (ms)
    
    # Identification
    label: str             # lb - название запроса
    thread_name: str       # tn - имя потока
    
    # Response
    response_code: str     # rc - HTTP status code
    response_message: str  # rm - HTTP status message
    success: bool          # s - успешность запроса
    
    # Data
    bytes_received: int    # by - полученные байты
    sent_bytes: int        # sby - отправленные байты
    data_type: str         # dt - MIME type
    data_encoding: str     # de - кодировка
    
    # Request details
    url: str               # java.net.URL
    method: str            # GET, POST, etc.
    query_string: str      # queryString
    
    # Headers & data
    request_header: str    # requestHeader
    response_header: str   # responseHeader
    response_data: str     # responseData
    
    # Redirect
    redirect_location: str # redirectLocation
    
    # Nested
    http_sample: list[HttpSample]  # вложенные сэмплы (редиректы)
    assertion_results: list[AssertionResult]  # результаты assertions
```

### TestResults

Корневая модель JTL файла:

```python
class TestResults:
    version: str                    # версия формата (обычно "1.2")
    http_sample: list[HttpSample]   # список всех HTTP сэмплов
```

## Интеграция с существующим кодом

Парсер можно легко интегрировать в ваш существующий код для сравнения трафика:

```python
from traffic_builder.har_parsers.har_parser import parse_har
from traffic_builder.jtl_parser.jtl_parser import parse_jtl
from traffic_builder.jtl_parser.jtl_to_har_converter import convert_jtl_to_har

# Парсинг HAR из браузера
har_browser = parse_har('browser_traffic.har')

# Парсинг JTL из JMeter
jtl_results = parse_jtl('jmeter_results.jtl')

# Конвертация JTL в HAR для сравнения
har_jmeter = convert_jtl_to_har(jtl_results)

# Теперь можно сравнивать оба HAR файла
browser_requests = [e.request for e in har_browser.log.entries]
jmeter_requests = [e.request for e in har_jmeter.log.entries]

```

## API Reference

### jtl_parser.py

#### `parse_jtl(filepath: str | Path) -> TestResults`
Парсит JTL XML файл.

#### `parse_jtl_from_string(content: str) -> TestResults`
Парсит JTL из строки.

#### `get_all_samples(test_results: TestResults, include_sub_samples: bool = True) -> list[HttpSample]`
Получает все сэмплы, включая вложенные (опционально).

#### `get_top_level_samples(test_results: TestResults) -> list[HttpSample]`
Получает только top-level сэмплы.

#### `get_failed_samples(test_results: TestResults) -> list[HttpSample]`
Получает только failed сэмплы.

### jtl_to_har_converter.py

#### `convert_jtl_to_har(test_results: TestResults, creator_name: str = "JMeter", creator_version: str = "5.6", include_sub_samples: bool = False) -> HarFile`
Конвертирует JTL в HAR формат.

Параметры:
- `test_results`: Распарсенные JTL результаты
- `creator_name`: Название creator tool
- `creator_version`: Версия creator tool
- `include_sub_samples`: Включать ли sub-samples как отдельные entries

#### `save_har(har_file: HarFile, output_path: str)`
Сохраняет HAR файл на диск.

## Примеры использования для вашего проекта

### 1. Сравнение трафика HAR vs JTL

```python
def compare_traffic(jmx_file: str, jtl_file: str, har_file: str):
    har_browser = parse_har(har_file)
    jtl_results = parse_jtl(jtl_file)
    
    browser_requests = [e.request.url for e in har_browser.log.entries]
    jmeter_samples = get_all_samples(jtl_results, include_sub_samples=False)
    jmeter_urls = [s.url for s in jmeter_samples if s.url]
    
    missing_in_jmeter = set(browser_requests) - set(jmeter_urls)
    extra_in_jmeter = set(jmeter_urls) - set(browser_requests)
    
    print(f"Missing in JMeter: {len(missing_in_jmeter)}")
    for url in missing_in_jmeter:
        print(f"  - {url}")
    
    print(f"\nExtra in JMeter: {len(extra_in_jmeter)}")
    for url in extra_in_jmeter:
        print(f"  + {url}")
```

### 2. Запуск JMeter и анализ результатов

```python
import subprocess

def run_jmeter_and_analyze(jmx_file: str, output_jtl: str):

    
    cmd = [
        'jmeter',
        '-n', 
        '-t', jmx_file,  
        '-l', output_jtl  
    ]
    
    subprocess.run(cmd, check=True)
    
    results = parse_jtl(output_jtl)
    
    all_samples = get_all_samples(results)
    failed = get_failed_samples(results)
    
    print(f"Total requests: {len(all_samples)}")
    print(f"Failed requests: {len(failed)}")
    
    if failed:
        print("\nFailed requests:")
        for sample in failed:
            print(f"  {sample.label}: {sample.response_code}")
    
    har = convert_jtl_to_har(results)
    save_har(har, output_jtl.replace('.jtl', '.har'))
```

## Поддерживаемые форматы

### JTL XML (Simple Data Writer)
✅ Полностью поддерживается

### JTL CSV
❌ Не поддерживается 

## Требования

- Python 3.10+
- pydantic >= 2.0

## Лицензия

MIT