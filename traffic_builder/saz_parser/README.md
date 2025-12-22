# SAZ Parser & SAZ-to-HAR Converter

Парсер для файлов SAZ (Fiddler Session Archive Zip) и конвертер в формат HAR (HTTP Archive).

## Возможности

### 1. Парсинг SAZ файлов
- Полная поддержка формата SAZ (Fiddler)
- Парсинг HTTP запросов и ответов
- Извлечение всех метаданных (timings, flags)
- Поддержка UI флагов Fiddler
- Информация о переиспользовании соединений

### 2. Конвертация SAZ → HAR
- Конвертация Fiddler сессий в стандартный формат HAR
- Расчет всех timing метрик из метаданных Fiddler
- Сохранение headers, cookies, body
- Совместимость с HAR-анализаторами

## Установка

```bash
pip install pydantic>=2.0
```

## Использование

### Базовый парсинг SAZ

```python
from traffic_builder.saz_parser.saz_parser import parse_saz, get_sessions

archive = parse_saz('capture.saz')

sessions = get_sessions(archive)

for session in sessions:
    print(f"{session.request.request_line.method} {session.request.request_line.url}")
    print(f"Status: {session.response.status_line.status_code}")
```

### Фильтрация сессий

```python
from traffic_builder.saz_parser.saz_parser import (
    parse_saz,
    get_sessions_by_status,
    get_sessions_by_method,
    get_sessions_by_flag
)

archive = parse_saz('capture.saz')

errors = get_sessions_by_status(archive, 500)

post_requests = get_sessions_by_method(archive, 'POST')

marked_sessions = get_sessions_by_flag(archive, 'ui-bold', 'user-marked')
```

### Конвертация в HAR

```python
from traffic_builder.saz_parser.saz_parser import parse_saz
from traffic_builder.saz_parser.saz_to_har_converter import convert_saz_to_har, save_har

archive = parse_saz('capture.saz')

har_file = convert_saz_to_har(archive)

save_har(har_file, 'output.har')
```

### Работа с метаданными

```python
from traffic_builder.saz_parser.saz_parser import parse_saz

archive = parse_saz('capture.saz')

for session in archive.sessions:
    metadata = session.metadata
    
    print(f"Session ID: {metadata.sid}")
    print(f"BitFlags: {metadata.bit_flags}")
    
    timers = metadata.timers
    total_time = (timers.client_done_response - timers.client_begin_request).total_seconds() * 1000
    print(f"Total time: {total_time:.2f}ms")
    
    for flag in metadata.flags:
        print(f"  {flag.name}: {flag.value}")
```

### Анализ производительности

```python
from traffic_builder.saz_parser.saz_parser import parse_saz

archive = parse_saz('capture.saz')

for session in archive.sessions:
    timers = session.metadata.timers
    
    dns = timers.dns_time
    connect = timers.tcp_connect_time
    ssl = timers.https_handshake_time
    
    wait = (timers.server_begin_response - timers.server_got_request).total_seconds() * 1000
    
    print(f"{session.request.request_line.url}")
    print(f"  DNS: {dns}ms, Connect: {connect}ms, SSL: {ssl}ms, Wait: {wait:.2f}ms")
```

### Работа с UI флагами

```python
from traffic_builder.saz_parser.saz_parser import parse_saz, get_sessions_by_flag

archive = parse_saz('capture.saz')

red_sessions = get_sessions_by_flag(archive, 'ui-color', 'Red')
print(f"Red marked sessions: {len(red_sessions)}")

blue_sessions = get_sessions_by_flag(archive, 'ui-color', 'Blue')
print(f"Blue marked sessions: {len(blue_sessions)}")

bold_sessions = get_sessions_by_flag(archive, 'ui-bold')
print(f"Bold sessions: {len(bold_sessions)}")
```

### Анализ переиспользования соединений

```python
from traffic_builder.saz_parser.saz_parser import parse_saz

archive = parse_saz('capture.saz')

reused = [s for s in archive.sessions if s.metadata.pipe_info.reused]
print(f"Reused connections: {len(reused)}/{len(archive.sessions)}")
```

## Структура данных

### SazSession

Основная модель для HTTP сессии из SAZ:

```python
@dataclass
class SazSession:
    session_id: int
    metadata: SessionMetadata
    request: Request
    response: Response
```

### SessionMetadata

Метаданные сессии из _m.xml:

```python
@dataclass
class SessionMetadata:
    sid: int
    bit_flags: int
    timers: SessionTimers
    pipe_info: PipeInfo
    flags: list[SessionFlag]
```

### SessionTimers

Все временные метки Fiddler:

```python
@dataclass
class SessionTimers:
    client_connected: datetime
    client_begin_request: datetime
    got_request_headers: datetime
    client_done_request: datetime
    
    server_connected: datetime
    fiddler_begin_request: datetime
    server_got_request: datetime
    
    server_begin_response: datetime
    got_response_headers: datetime
    server_done_response: datetime
    
    client_begin_response: datetime
    client_done_response: datetime
    
    gateway_time: int
    dns_time: int
    tcp_connect_time: int
    https_handshake_time: int
```

### PipeInfo

Информация о переиспользовании соединений:

```python
@dataclass
class PipeInfo:
    clt_reuse: bool
    reused: bool
```

### SessionFlag

UI и технические флаги:

```python
@dataclass
class SessionFlag:
    name: str
    value: str
```

Типичные флаги:
- `ui-color` - цвет в Fiddler (Red, Blue, Green, Purple, etc)
- `ui-bold` - выделение жирным
- `ui-oldcolor` - предыдущий цвет
- `x-clientip` - IP клиента
- `x-clientport` - порт клиента
- `x-hostip` - IP хоста
- `x-egressport` - порт egress
- `x-processinfo` - информация о процессе
- `x-serversocket` - информация о серверном сокете
- `x-responsebodytransferlength` - размер тела ответа
- `x-retryonfailedreceive` - флаг retry

### Request

HTTP запрос:

```python
@dataclass
class Request:
    request_line: RequestLine
    headers: list[Header]
    body: bytes
```

### Response

HTTP ответ:

```python
@dataclass
class Response:
    status_line: StatusLine
    headers: list[Header]
    body: bytes
```

### SazArchive

Корневая модель:

```python
@dataclass
class SazArchive:
    sessions: list[SazSession]
```

## Интеграция с существующим кодом

### Сравнение SAZ с HAR

```python
from traffic_builder.har_parsers.har_parser import parse_har
from traffic_builder.saz_parser.saz_parser import parse_saz
from traffic_builder.saz_parser.saz_to_har_converter import convert_saz_to_har

har_original = parse_har('browser.har')

saz_archive = parse_saz('fiddler.saz')
har_from_saz = convert_saz_to_har(saz_archive)

original_urls = [e.request.url for e in har_original.log.entries]
saz_urls = [e.request.url for e in har_from_saz.log.entries]

missing = set(original_urls) - set(saz_urls)
```

### Сравнение SAZ с JTL

```python
from traffic_builder.jtl_parser.jtl_parser import parse_jtl
from traffic_builder.jtl_parser.jtl_to_har_converter import convert_jtl_to_har
from traffic_builder.saz_parser.saz_parser import parse_saz
from traffic_builder.saz_parser.saz_to_har_converter import convert_saz_to_har

saz_archive = parse_saz('fiddler.saz')
har_saz = convert_saz_to_har(saz_archive)

jtl_results = parse_jtl('jmeter.jtl')
har_jtl = convert_jtl_to_har(jtl_results)

saz_urls = [e.request.url for e in har_saz.log.entries]
jtl_urls = [e.request.url for e in har_jtl.log.entries]
```

## API Reference

### saz_parser.py

#### `parse_saz(filepath: str | Path) -> SazArchive`
Парсит SAZ файл (ZIP архив Fiddler).

#### `get_sessions(archive: SazArchive) -> list[SazSession]`
Получает все сессии из архива.

#### `get_sessions_by_status(archive: SazArchive, status_code: int) -> list[SazSession]`
Фильтрует сессии по HTTP статус коду.

#### `get_sessions_by_method(archive: SazArchive, method: str) -> list[SazSession]`
Фильтрует сессии по HTTP методу.

#### `get_sessions_by_flag(archive: SazArchive, flag_name: str, flag_value: Optional[str] = None) -> list[SazSession]`
Фильтрует сессии по флагу.

Параметры:
- `flag_name`: Имя флага (например, "ui-color")
- `flag_value`: Значение флага (опционально, если None - любое значение)

### saz_to_har_converter.py

#### `convert_saz_to_har(archive: SazArchive, creator_name: str = "Fiddler", creator_version: str = "5.0") -> HarFile`
Конвертирует SAZ в HAR формат.

Параметры:
- `archive`: Распарсенный SAZ архив
- `creator_name`: Название creator tool
- `creator_version`: Версия creator tool

#### `save_har(har_file: HarFile, output_path: str)`
Сохраняет HAR файл на диск.

## Примеры использования

### 1. Экспорт отмеченных запросов

```python
archive = parse_saz('capture.saz')

marked = get_sessions_by_flag(archive, 'ui-bold', 'user-marked')

har = convert_saz_to_har(SazArchive(sessions=marked))
save_har(har, 'marked_only.har')
```

### 2. Анализ ошибок

```python
archive = parse_saz('capture.saz')

errors_4xx = get_sessions_by_status(archive, 400) + \
             get_sessions_by_status(archive, 404)

errors_5xx = get_sessions_by_status(archive, 500) + \
             get_sessions_by_status(archive, 502)

print(f"Client errors (4xx): {len(errors_4xx)}")
print(f"Server errors (5xx): {len(errors_5xx)}")

for session in errors_5xx:
    print(f"  {session.request.request_line.url}")
    print(f"  Status: {session.response.status_line.status_code}")
```

### 3. Группировка по хосту

```python
from collections import defaultdict
from urllib.parse import urlparse

archive = parse_saz('capture.saz')

by_host = defaultdict(list)
for session in archive.sessions:
    url = session.request.request_line.url
    host = urlparse(url).netloc
    by_host[host].append(session)

for host, sessions in by_host.items():
    print(f"{host}: {len(sessions)} requests")
```

### 4. Экспорт по цвету

```python
archive = parse_saz('capture.saz')

colors = ['Red', 'Blue', 'Green', 'Purple']

for color in colors:
    sessions = get_sessions_by_flag(archive, 'ui-color', color)
    if sessions:
        har = convert_saz_to_har(SazArchive(sessions=sessions))
        save_har(har, f'{color.lower()}_requests.har')
        print(f"Exported {len(sessions)} {color} requests")
```

### 5. Статистика по процессам

```python
from collections import defaultdict

archive = parse_saz('capture.saz')

by_process = defaultdict(int)
for session in archive.sessions:
    for flag in session.metadata.flags:
        if flag.name == 'x-processinfo':
            by_process[flag.value] += 1
            break

for process, count in by_process.items():
    print(f"{process}: {count} requests")
```

### 6. Поиск медленных запросов

```python
archive = parse_saz('capture.saz')

slow_sessions = []
for session in archive.sessions:
    timers = session.metadata.timers
    total_time = (timers.client_done_response - timers.client_begin_request).total_seconds() * 1000
    
    if total_time > 1000:
        slow_sessions.append((session, total_time))

slow_sessions.sort(key=lambda x: x[1], reverse=True)

print(f"Slow requests (>1s): {len(slow_sessions)}")
for session, time in slow_sessions[:10]:
    print(f"  {time:.2f}ms - {session.request.request_line.url}")
```

## Особенности формата SAZ

### Структура архива

```
capture.saz (ZIP)
├── [Content_Types].xml
├── _index.htm
└── raw/
    ├── 001_c.txt    (client request)
    ├── 001_s.txt    (server response)
    ├── 001_m.xml    (metadata)
    ├── 002_c.txt
    ├── 002_s.txt
    ├── 002_m.xml
    └── ...
```

### Формат файлов

**_c.txt** (request):
```
GET http://example.com/ HTTP/1.1
Host: example.com
User-Agent: Mozilla/5.0
...

[request body]
```

**_s.txt** (response):
```
HTTP/1.1 200 OK
Content-Type: text/html
...

[response body]
```

**_m.xml** (metadata):
```xml
<Session SID="1" BitFlags="0">
  <SessionTimers ClientConnected="..." ... />
  <PipeInfo CltReuse="true" Reused="true" />
  <SessionFlags>
    <SessionFlag N="ui-color" V="Red" />
    ...
  </SessionFlags>
</Session>
```

## Timezone и DateTime

Все datetime поля конвертируются в UTC без timezone информации:

```python
archive = parse_saz('capture.saz')

for session in archive.sessions:
    dt = session.metadata.timers.client_begin_request
    print(dt.isoformat())
```

## Требования

- Python 3.10+
- pydantic >= 2.0

## Поддерживаемые форматы

### SAZ (Fiddler)
✅ Полностью поддерживается

## Лицензия

MIT