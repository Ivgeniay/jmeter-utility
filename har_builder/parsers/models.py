from dataclasses import dataclass, field


@dataclass
class Cookie:
    name: str
    value: str
    path: str = ""
    domain: str = ""
    expires: str = ""
    http_only: bool = False
    secure: bool = False
    comment: str = ""

@dataclass
class Record:
    name: str
    value: str
    comment: str = ""

@dataclass
class PostData:
    mime_type: str
    text: str = ""
    params: list[Record] = field(default_factory=list)
    comment: str = ""


@dataclass
class Request:
    method: str
    url: str
    http_version: str = ""
    cookies: list[Cookie] = field(default_factory=list)
    headers: list[Record] = field(default_factory=list)
    query_string: list[Record] = field(default_factory=list)
    post_data: PostData | None = None
    headers_size: int = 0
    body_size: int = 0
    comment: str = ""