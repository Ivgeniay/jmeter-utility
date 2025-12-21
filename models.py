from dataclasses import dataclass, field
from har_builder.parsers.models import Cookie, Record, Request

@dataclass
class Content:
    size: int
    mime_type: str
    compression: int = 0
    text: str = ""
    encoding: str = ""
    comment: str = ""

@dataclass
class Response:
    status: int
    status_text: str
    http_version: str = ""
    cookies: list[Cookie] = field(default_factory=list)
    headers: list[Record] = field(default_factory=list)
    content: Content | None = None
    redirect_url: str = ""
    headers_size: int = 0
    body_size: int = 0
    comment: str = ""

@dataclass
class Timings:
    send: float
    wait: float
    receive: float
    dns: float = -1
    connect: float = -1
    blocked: float = -1
    ssl: float = -1
    comment: str = ""

@dataclass
class CacheEntry:
    last_access: str
    e_tag: str
    hit_count: int
    expires: str = ""
    comment: str = ""

@dataclass
class Cache:
    before_request: CacheEntry | None = None
    after_request: CacheEntry | None = None
    comment: str = ""

@dataclass
class Entry:
    started_date_time: str
    time: float
    request: Request
    response: Response
    cache: Cache
    timings: Timings
    pageref: str = ""
    server_ip_address: str = ""
    connection: str = ""
    comment: str = ""

@dataclass
class PageTimings:
    on_content_load: float = -1
    on_load: float = -1
    comment: str = ""

@dataclass
class Page:
    started_date_time: str
    id: str
    title: str
    page_timings: PageTimings
    comment: str = ""

@dataclass
class Creator:
    name: str
    version: str
    comment: str = ""

@dataclass
class Browser:
    name: str
    version: str
    comment: str = ""

@dataclass
class Log:
    version: str
    creator: Creator
    entries: list[Entry]
    browser: Browser | None = None
    pages: list[Page] = field(default_factory=list)
    comment: str = ""

@dataclass
class HarFile:
    log: Log


@dataclass
class TransactionGroup:
    name: str
    requests: list[Request] = field(default_factory=list)


@dataclass
class JMeterResult:
    all_requests: list[Request] = field(default_factory=list)
    transactions: list[TransactionGroup] = field(default_factory=list)