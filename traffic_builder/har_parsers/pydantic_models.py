from pydantic import BaseModel, Field, field_validator


class Record(BaseModel):
    name: str | None = None
    value: str
    comment: str = ""
    
    @field_validator("name", "value", mode="before")
    @classmethod
    def none_to_empty(cls, v):
        return v if v is not None else ""


class Param(BaseModel):
    name: str
    value: str = ""
    file_name: str = Field(default="", alias="fileName")
    content_type: str = Field(default="", alias="contentType")
    comment: str = ""

    model_config = {"populate_by_name": True}


class Cookie(BaseModel):
    name: str
    value: str
    path: str = ""
    domain: str = ""
    expires: str = ""
    http_only: bool = Field(default=False, alias="httpOnly")
    secure: bool = False
    same_site: str = Field(default="", alias="sameSite")
    comment: str = ""

    model_config = {"populate_by_name": True}


class PostData(BaseModel):
    mime_type: str = Field(alias="mimeType")
    text: str = ""
    params: list[Param] = Field(default_factory=list)
    comment: str = ""

    model_config = {"populate_by_name": True}


class Request(BaseModel):
    method: str
    url: str
    http_version: str = Field(default="", alias="httpVersion")
    cookies: list[Cookie] = Field(default_factory=list)
    headers: list[Record] = Field(default_factory=list)
    query_string: list[Record] = Field(default_factory=list, alias="queryString")
    post_data: PostData | None = Field(default=None, alias="postData")
    headers_size: int = Field(default=-1, alias="headersSize")
    body_size: int = Field(default=-1, alias="bodySize")
    comment: str = ""

    model_config = {"populate_by_name": True}


class Content(BaseModel):
    size: int
    mime_type: str = Field(alias="mimeType")
    compression: int = 0
    text: str = ""
    encoding: str = ""
    comment: str = ""

    model_config = {"populate_by_name": True}


class Response(BaseModel):
    status: int
    status_text: str = Field(alias="statusText")
    http_version: str = Field(default="", alias="httpVersion")
    cookies: list[Cookie] = Field(default_factory=list)
    headers: list[Record] = Field(default_factory=list)
    content: Content | None = None
    redirect_url: str = Field(default="", alias="redirectURL")
    headers_size: int = Field(default=-1, alias="headersSize")
    body_size: int = Field(default=-1, alias="bodySize")
    comment: str = ""

    model_config = {"populate_by_name": True}


class Timings(BaseModel):
    send: float
    wait: float
    receive: float
    blocked: float = -1
    dns: float = -1
    connect: float = -1
    ssl: float = -1
    comment: str = ""


class CacheEntry(BaseModel):
    last_access: str = Field(alias="lastAccess")
    e_tag: str = Field(alias="eTag")
    hit_count: int = Field(alias="hitCount")
    expires: str = ""
    comment: str = ""

    model_config = {"populate_by_name": True}


class Cache(BaseModel):
    before_request: CacheEntry | None = Field(default=None, alias="beforeRequest")
    after_request: CacheEntry | None = Field(default=None, alias="afterRequest")
    comment: str = ""

    model_config = {"populate_by_name": True}


class Entry(BaseModel):
    started_date_time: str = Field(alias="startedDateTime")
    time: float
    request: Request
    response: Response
    cache: Cache
    timings: Timings
    pageref: str = ""
    server_ip_address: str = Field(default="", alias="serverIPAddress")
    connection: str = ""
    comment: str = ""

    model_config = {"populate_by_name": True}


class PageTimings(BaseModel):
    on_content_load: float = Field(default=-1, alias="onContentLoad")
    on_load: float = Field(default=-1, alias="onLoad")
    comment: str = ""

    model_config = {"populate_by_name": True}


class Page(BaseModel):
    started_date_time: str = Field(alias="startedDateTime")
    id: str
    title: str
    page_timings: PageTimings = Field(alias="pageTimings")
    comment: str = ""

    model_config = {"populate_by_name": True}


class Creator(BaseModel):
    name: str
    version: str
    comment: str = ""


class Browser(BaseModel):
    name: str
    version: str
    comment: str = ""


class Log(BaseModel):
    version: str
    creator: Creator
    entries: list[Entry]
    browser: Browser | None = None
    pages: list[Page] = Field(default_factory=list)
    comment: str = ""


class HarFile(BaseModel):
    log: Log