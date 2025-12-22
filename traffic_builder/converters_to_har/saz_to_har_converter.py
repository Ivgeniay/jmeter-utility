import json
from datetime import datetime
from urllib.parse import urlparse, parse_qs
from typing import Optional

from traffic_builder.saz_parser.models import SazArchive, SazSession
from traffic_builder.har_parsers.pydantic_models import (
    HarFile, Log, Entry, Request, Response, Content,
    Cache, Timings, Creator, Browser, Record, Cookie
)


def _parse_cookies_from_headers(headers: list) -> list[Cookie]:
    cookies = []
    for header in headers:
        if header.name.lower() == 'set-cookie':
            cookie_parts = header.value.split(';')
            if cookie_parts:
                name_value = cookie_parts[0].strip()
                if '=' in name_value:
                    name, value = name_value.split('=', 1)
                    
                    cookie_attrs = {
                        'name': name.strip(),
                        'value': value.strip(),
                        'path': '/',
                        'domain': '',
                        'http_only': False,
                        'secure': False
                    }
                    
                    for part in cookie_parts[1:]:
                        part = part.strip().lower()
                        if part == 'httponly':
                            cookie_attrs['http_only'] = True
                        elif part == 'secure':
                            cookie_attrs['secure'] = True
                        elif part.startswith('path='):
                            cookie_attrs['path'] = part.split('=', 1)[1]
                        elif part.startswith('domain='):
                            cookie_attrs['domain'] = part.split('=', 1)[1]
                    
                    cookies.append(Cookie(**cookie_attrs))
    return cookies


def _parse_query_string(url: str) -> list[Record]:
    parsed = urlparse(url)
    if not parsed.query:
        return []
    
    query_params = parse_qs(parsed.query)
    records = []
    
    for name, values in query_params.items():
        for value in values:
            records.append(Record(name=name, value=value))
    
    return records


def _convert_headers(saz_headers: list) -> list[Record]:
    return [Record(name=h.name, value=h.value) for h in saz_headers]


def _calculate_timings(session: SazSession) -> Timings:
    timers = session.metadata.timers
    
    blocked = (timers.fiddler_begin_request - timers.client_begin_request).total_seconds() * 1000
    dns = float(timers.dns_time)
    connect = float(timers.tcp_connect_time)
    ssl = float(timers.https_handshake_time)
    send = (timers.server_got_request - timers.fiddler_begin_request).total_seconds() * 1000
    wait = (timers.server_begin_response - timers.server_got_request).total_seconds() * 1000
    receive = (timers.client_done_response - timers.server_begin_response).total_seconds() * 1000
    
    return Timings(
        blocked=blocked,
        dns=dns,
        connect=connect,
        ssl=ssl,
        send=send,
        wait=wait,
        receive=receive
    )


def _convert_session_to_entry(session: SazSession) -> Entry:
    url = session.request.request_line.url
    
    request_headers = _convert_headers(session.request.headers)
    response_headers = _convert_headers(session.response.headers)
    
    response_cookies = _parse_cookies_from_headers(session.response.headers)
    
    request = Request(
        method=session.request.request_line.method,
        url=url,
        http_version=session.request.request_line.http_version,
        headers=request_headers,
        query_string=_parse_query_string(url),
        cookies=[],
        headers_size=-1,
        body_size=len(session.request.body)
    )
    
    content_type = ""
    for header in session.response.headers:
        if header.name.lower() == 'content-type':
            content_type = header.value
            break
    
    content = Content(
        size=len(session.response.body),
        mime_type=content_type,
        text=session.response.body.decode('utf-8', errors='ignore'),
        encoding=""
    )
    
    response = Response(
        status=session.response.status_line.status_code,
        status_text=session.response.status_line.status_text,
        http_version=session.response.status_line.http_version,
        headers=response_headers,
        cookies=response_cookies,
        content=content,
        redirect_url="",
        headers_size=-1,
        body_size=len(session.response.body)
    )
    
    timings = _calculate_timings(session)
    
    cache = Cache()
    
    started_date_time = session.metadata.timers.client_begin_request.isoformat() + "Z"
    
    total_time = (session.metadata.timers.client_done_response - 
                  session.metadata.timers.client_begin_request).total_seconds() * 1000
    
    entry = Entry(
        started_date_time=started_date_time,
        time=total_time,
        request=request,
        response=response,
        cache=cache,
        timings=timings,
        server_ip_address="",
        connection=""
    )
    
    return entry


def convert_saz_to_har(
    archive: SazArchive,
    creator_name: str = "Fiddler",
    creator_version: str = "5.0"
) -> HarFile:
    entries = []
    
    for session in archive.sessions:
        entry = _convert_session_to_entry(session)
        entries.append(entry)
    
    creator = Creator(name=creator_name, version=creator_version)
    browser = Browser(name="Firefox", version="146.0")
    
    log = Log(
        version="1.2",
        creator=creator,
        browser=browser,
        entries=entries,
        pages=[]
    )
    
    har_file = HarFile(log=log)
    
    return har_file


def save_har(har_file: HarFile, output_path: str):
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(har_file.model_dump(by_alias=True, exclude_none=True), f, indent=2)