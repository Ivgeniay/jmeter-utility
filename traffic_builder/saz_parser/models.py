from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


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
    
    gateway_time: int = 0
    dns_time: int = 0
    tcp_connect_time: int = 0
    https_handshake_time: int = 0


@dataclass
class PipeInfo:
    clt_reuse: bool = False
    reused: bool = False


@dataclass
class SessionFlag:
    name: str
    value: str


@dataclass
class SessionMetadata:
    sid: int
    bit_flags: int
    timers: SessionTimers
    pipe_info: PipeInfo
    flags: list[SessionFlag] = field(default_factory=list)


@dataclass
class RequestLine:
    method: str
    url: str
    http_version: str


@dataclass
class Header:
    name: str
    value: str


@dataclass
class Request:
    request_line: RequestLine
    headers: list[Header] = field(default_factory=list)
    body: bytes = b""


@dataclass
class StatusLine:
    http_version: str
    status_code: int
    status_text: str


@dataclass
class Response:
    status_line: StatusLine
    headers: list[Header] = field(default_factory=list)
    body: bytes = b""


@dataclass
class SazSession:
    session_id: int
    metadata: SessionMetadata
    request: Request
    response: Response


@dataclass
class SazArchive:
    sessions: list[SazSession] = field(default_factory=list)