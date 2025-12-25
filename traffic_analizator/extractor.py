import json
import re
from urllib.parse import parse_qs, urlparse

from traffic_builder.har_parsers.pydantic_models import Entry, HarFile

from .models import (
    DataLocation,
    RequestDataPoint,
    ResponseDataPoint,
)
from .extractors import (
    JsonExtractorHint,
    RegexExtractorHint,
    HeaderExtractorHint,
    CookieExtractorHint,
)




class TrafficExtractor:
    
    def __init__(self, har: HarFile, ignore_cookies: bool = False):
        self.har = har
        self.entries = har.log.entries
        self.ignore_cookies = ignore_cookies
    
    def extract_all(self) -> tuple[list[RequestDataPoint], list[ResponseDataPoint]]:
        request_points: list[RequestDataPoint] = []
        response_points: list[ResponseDataPoint] = []
        
        for index, entry in enumerate(self.entries):
            request_points.extend(self._extract_from_request(entry, index))
            response_points.extend(self._extract_from_response(entry, index))
        
        return request_points, response_points
    
    def _extract_from_request(self, entry: Entry, index: int) -> list[RequestDataPoint]:
        points: list[RequestDataPoint] = []
        request = entry.request
        url = request.url
        method = request.method
        
        for header in request.headers:
            if self._is_skippable_header(header.name):
                continue
            points.append(RequestDataPoint(
                request_index=index,
                url=url,
                method=method,
                location=DataLocation.HEADER,
                name=header.name,
                value=header.value,
            ))
        
        for param in request.query_string:
            points.append(RequestDataPoint(
                request_index=index,
                url=url,
                method=method,
                location=DataLocation.QUERY_PARAM,
                name=param.name,
                value=param.value,
            ))
        
        if not self.ignore_cookies:
            for cookie in request.cookies:
                points.append(RequestDataPoint(
                    request_index=index,
                    url=url,
                    method=method,
                    location=DataLocation.COOKIE,
                    name=cookie.name,
                    value=cookie.value,
                ))
        
        if request.post_data:
            if request.post_data.params:
                for param in request.post_data.params:
                    points.append(RequestDataPoint(
                        request_index=index,
                        url=url,
                        method=method,
                        location=DataLocation.FORM_PARAM,
                        name=param.name,
                        value=param.value,
                    ))
            
            if request.post_data.text:
                text = request.post_data.text
                json_points = self._try_extract_json(
                    text, index, url, method, is_request=True
                )
                if json_points:
                    points.extend(json_points)
                else:
                    points.append(RequestDataPoint(
                        request_index=index,
                        url=url,
                        method=method,
                        location=DataLocation.BODY_RAW,
                        name="body",
                        value=text,
                    ))
        
        return points
    
    def _extract_from_response(self, entry: Entry, index: int) -> list[ResponseDataPoint]:
        points: list[ResponseDataPoint] = []
        response = entry.response
        url = entry.request.url
        status_code = response.status
        
        for header in response.headers:
            if self._is_skippable_response_header(header.name):
                continue
            points.append(ResponseDataPoint(
                response_index=index,
                url=url,
                status_code=status_code,
                location=DataLocation.RESPONSE_HEADER,
                name=header.name,
                value=header.value,
                extractor_hint=HeaderExtractorHint(header_name=header.name),
            ))
        
        if not self.ignore_cookies:
            for cookie in response.cookies:
                points.append(ResponseDataPoint(
                    response_index=index,
                    url=url,
                    status_code=status_code,
                    location=DataLocation.SET_COOKIE,
                    name=cookie.name,
                    value=cookie.value,
                    extractor_hint=CookieExtractorHint(cookie_name=cookie.name),
                ))
        
        if response.content and response.content.text:
            content_type = response.content.mime_type.lower() if response.content.mime_type else ""
            text = response.content.text
            
            if "json" in content_type or self._looks_like_json(text):
                json_points = self._try_extract_json_response(text, index, url, status_code)
                points.extend(json_points)
            
            elif "html" in content_type or text.strip().startswith("<"):
                html_points = self._extract_from_html(text, index, url, status_code)
                points.extend(html_points)
            
            else:
                if len(text) < 10000:
                    points.append(ResponseDataPoint(
                        response_index=index,
                        url=url,
                        status_code=status_code,
                        location=DataLocation.RESPONSE_RAW,
                        name=None,
                        value=text,
                        extractor_hint=RegexExtractorHint(pattern="(.+)"),
                    ))
        
        return points
    
    def _try_extract_json(
        self, 
        text: str, 
        index: int, 
        url: str, 
        method: str,
        is_request: bool
    ) -> list[RequestDataPoint]:
        try:
            data = json.loads(text)
        except (json.JSONDecodeError, ValueError):
            return []
        
        points: list[RequestDataPoint] = []
        self._flatten_json(data, "$", points, index, url, method)
        return points
    
    def _flatten_json(
        self,
        data,
        path: str,
        points: list[RequestDataPoint],
        index: int,
        url: str,
        method: str
    ) -> None:
        if isinstance(data, dict):
            for key, value in data.items():
                new_path = f"{path}.{key}"
                self._flatten_json(value, new_path, points, index, url, method)
        elif isinstance(data, list):
            for i, item in enumerate(data):
                new_path = f"{path}[{i}]"
                self._flatten_json(item, new_path, points, index, url, method)
        else:
            if data is not None:
                points.append(RequestDataPoint(
                    request_index=index,
                    url=url,
                    method=method,
                    location=DataLocation.BODY_JSON,
                    name=path.split(".")[-1].split("[")[0],
                    value=str(data),
                    json_path=path,
                ))
    
    def _try_extract_json_response(
        self,
        text: str,
        index: int,
        url: str,
        status_code: int
    ) -> list[ResponseDataPoint]:
        try:
            data = json.loads(text)
        except (json.JSONDecodeError, ValueError):
            return []
        
        points: list[ResponseDataPoint] = []
        self._flatten_json_response(data, "$", points, index, url, status_code)
        return points
    
    def _flatten_json_response(
        self,
        data,
        path: str,
        points: list[ResponseDataPoint],
        index: int,
        url: str,
        status_code: int
    ) -> None:
        if isinstance(data, dict):
            for key, value in data.items():
                new_path = f"{path}.{key}"
                self._flatten_json_response(value, new_path, points, index, url, status_code)
        elif isinstance(data, list):
            for i, item in enumerate(data):
                new_path = f"{path}[{i}]"
                self._flatten_json_response(item, new_path, points, index, url, status_code)
        else:
            if data is not None:
                str_value = str(data)
                points.append(ResponseDataPoint(
                    response_index=index,
                    url=url,
                    status_code=status_code,
                    location=DataLocation.RESPONSE_JSON,
                    name=path.split(".")[-1].split("[")[0],
                    value=str_value,
                    extractor_hint=JsonExtractorHint(json_path=path),
                ))
    
    def _extract_from_html(
        self,
        text: str,
        index: int,
        url: str,
        status_code: int
    ) -> list[ResponseDataPoint]:
        points: list[ResponseDataPoint] = []
        
        input_pattern = re.compile(
            r'<input[^>]*name=["\']([^"\']+)["\'][^>]*value=["\']([^"\']*)["\'][^>]*/?>',
            re.IGNORECASE
        )
        for match in input_pattern.finditer(text):
            name, value = match.groups()
            if value:
                points.append(ResponseDataPoint(
                    response_index=index,
                    url=url,
                    status_code=status_code,
                    location=DataLocation.RESPONSE_HTML,
                    name=name,
                    value=value,
                    extractor_hint=RegexExtractorHint(
                        pattern=f'name="{name}"[^>]*value="([^"]*)"'
                    ),
                ))
        
        input_pattern_reverse = re.compile(
            r'<input[^>]*value=["\']([^"\']+)["\'][^>]*name=["\']([^"\']+)["\'][^>]*/?>',
            re.IGNORECASE
        )
        for match in input_pattern_reverse.finditer(text):
            value, name = match.groups()
            if value and not any(p.name == name and p.value == value for p in points):
                points.append(ResponseDataPoint(
                    response_index=index,
                    url=url,
                    status_code=status_code,
                    location=DataLocation.RESPONSE_HTML,
                    name=name,
                    value=value,
                    extractor_hint=RegexExtractorHint(
                        pattern=f'name="{name}"[^>]*value="([^"]*)"'
                    ),
                ))
        
        meta_pattern = re.compile(
            r'<meta[^>]*name=["\']([^"\']+)["\'][^>]*content=["\']([^"\']+)["\'][^>]*/?>',
            re.IGNORECASE
        )
        for match in meta_pattern.finditer(text):
            name, content = match.groups()
            if "csrf" in name.lower() or "token" in name.lower():
                points.append(ResponseDataPoint(
                    response_index=index,
                    url=url,
                    status_code=status_code,
                    location=DataLocation.RESPONSE_HTML,
                    name=name,
                    value=content,
                    extractor_hint=RegexExtractorHint(
                        pattern=f'<meta[^>]*name="{name}"[^>]*content="([^"]*)"'
                    ),
                ))
        
        data_attr_pattern = re.compile(
            r'data-(token|csrf|requesttoken|session)=["\']([^"\']+)["\']',
            re.IGNORECASE
        )
        for match in data_attr_pattern.finditer(text):
            name, value = match.groups()
            points.append(ResponseDataPoint(
                response_index=index,
                url=url,
                status_code=status_code,
                location=DataLocation.RESPONSE_HTML,
                name=f"data-{name}",
                value=value,
                extractor_hint=RegexExtractorHint(pattern=f'data-{name}="([^"]*)"'),
            ))
        
        return points
    
    def _is_skippable_header(self, name: str) -> bool:
        skip = {
            "host", "connection", "accept", "accept-language", 
            "accept-encoding", "user-agent", "content-type",
            "content-length", "origin", "referer", "sec-fetch-dest",
            "sec-fetch-mode", "sec-fetch-site", "sec-ch-ua",
            "sec-ch-ua-mobile", "sec-ch-ua-platform", "cache-control",
            "pragma", "upgrade-insecure-requests", "dnt",
        }
        return name.lower() in skip
    
    def _is_skippable_response_header(self, name: str) -> bool:
        skip = {
            "date", "server", "content-type", "content-length",
            "connection", "keep-alive", "cache-control", "expires",
            "pragma", "vary", "etag", "last-modified", "age",
            "x-powered-by", "x-content-type-options", "x-frame-options",
            "x-xss-protection", "strict-transport-security",
            "content-encoding", "transfer-encoding", "access-control-allow-origin",
            "access-control-allow-methods", "access-control-allow-headers",
        }
        return name.lower() in skip
    
    def _looks_like_json(self, text: str) -> bool:
        stripped = text.strip()
        return (stripped.startswith("{") and stripped.endswith("}")) or (stripped.startswith("[") and stripped.endswith("]"))