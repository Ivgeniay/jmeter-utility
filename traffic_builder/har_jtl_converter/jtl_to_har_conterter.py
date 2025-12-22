"""
Converter from JMeter JTL format to HAR (HTTP Archive) format.
"""
from datetime import datetime
from urllib.parse import urlparse, parse_qs
from typing import Optional

from traffic_builder.jtl_parser.models import TestResults, HttpSample
from traffic_builder.har_parsers.pydantic_models import (
    HarFile, Log, Entry, Request, Response, Content,
    Cache, Timings, Creator, Browser, Record, Cookie
)


def _parse_headers(header_text: str) -> list[Record]:
    if not header_text:
        return []
    
    headers = []
    lines = header_text.strip().split('\n')
    
    for line in lines[1:] if lines and lines[0].startswith('HTTP/') else lines:
        if ':' in line:
            name, value = line.split(':', 1)
            headers.append(Record(name=name.strip(), value=value.strip()))
    
    return headers


def _parse_cookies_from_headers(headers: list[Record]) -> list[Cookie]:
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


def _convert_sample_to_entry(sample: HttpSample, index: int) -> Entry:
    url = sample.url or sample.label
    
    request_headers = _parse_headers(sample.request_header)
    response_headers = _parse_headers(sample.response_header)
    
    response_cookies = _parse_cookies_from_headers(response_headers)
    
    request = Request(
        method=sample.method or "GET",
        url=url,
        http_version="HTTP/1.1",
        headers=request_headers,
        query_string=_parse_query_string(url),
        cookies=[],
        headers_size=sample.sent_bytes,
        body_size=0
    )
    
    content = Content(
        size=sample.bytes_received,
        mime_type=sample.data_type or "text/html",
        text=sample.response_data,
        encoding=sample.data_encoding or "utf-8"
    )
    
    response = Response(
        status=int(sample.response_code) if sample.response_code.isdigit() else 0,
        status_text=sample.response_message,
        http_version="HTTP/1.1",
        headers=response_headers,
        cookies=response_cookies,
        content=content,
        redirect_url=sample.redirect_location,
        headers_size=0,
        body_size=sample.bytes_received
    )

    timings = Timings(
        send=0,  # JTL doesn't track send time separately
        wait=float(sample.latency),
        receive=float(sample.elapsed - sample.latency),
        connect=float(sample.connect_time),
        dns=-1,
        blocked=-1,
        ssl=-1
    )
    
    cache = Cache()
    
    timestamp_ms = sample.timestamp
    dt = datetime.fromtimestamp(timestamp_ms / 1000.0)
    started_date_time = dt.isoformat() + "Z"
    
    entry = Entry(
        started_date_time=started_date_time,
        time=float(sample.elapsed),
        request=request,
        response=response,
        cache=cache,
        timings=timings,
        server_ip_address="",
        connection=""
    )
    
    return entry


def convert_jtl_to_har(
    test_results: TestResults,
    creator_name: str = "JMeter",
    creator_version: str = "5.6",
    include_sub_samples: bool = False
) -> HarFile:
    entries = []
    
    def process_sample(sample: HttpSample, index: int) -> int:
        """Process a sample and its sub-samples recursively."""
        entry = _convert_sample_to_entry(sample, index)
        entries.append(entry)
        current_index = index + 1
        
        if include_sub_samples:
            for sub_sample in sample.http_sample:
                current_index = process_sample(sub_sample, current_index)
        
        return current_index
    
    index = 0
    for sample in test_results.http_sample:
        index = process_sample(sample, index)
    
    creator = Creator(name=creator_name, version=creator_version)
    browser = Browser(name="JMeter", version=creator_version)
    
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
    import json
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(har_file.model_dump(by_alias=True, exclude_none=True), f, indent=2)