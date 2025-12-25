from dataclasses import dataclass, asdict
from urllib.parse import urlparse

from traffic_analizator.models import AnalysisReport, Correlation
from traffic_builder.har_parsers.pydantic_models import Entry, HarFile



SKIP_CONTENT_TYPES = {
    'image/png', 'image/jpeg', 'image/gif', 'image/svg+xml', 'image/webp',
    'image/x-icon', 'image/bmp', 'image/tiff',
    'font/woff', 'font/woff2', 'font/ttf', 'font/otf',
    'application/font-woff', 'application/font-woff2',
    'application/x-font-ttf', 'application/x-font-otf',
    'text/css',
    'application/javascript', 'text/javascript', 'application/x-javascript',
    'audio/mpeg', 'audio/wav', 'audio/ogg',
    'video/mp4', 'video/webm', 'video/ogg',
}

SKIP_EXTENSIONS = {
    '.js', '.css', '.map',
    '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.webp', '.bmp',
    '.woff', '.woff2', '.ttf', '.eot', '.otf',
    '.mp3', '.mp4', '.wav', '.ogg', '.webm',
    '.pdf', '.zip', '.gz', '.tar',
}

STANDARD_HEADERS = {
    'host', 'user-agent', 'accept', 'accept-language', 'accept-encoding',
    'connection', 'content-type', 'content-length', 'origin', 'referer',
    'sec-fetch-dest', 'sec-fetch-mode', 'sec-fetch-site', 'sec-fetch-user',
    'sec-ch-ua', 'sec-ch-ua-mobile', 'sec-ch-ua-platform',
    'upgrade-insecure-requests', 'cache-control', 'pragma',
    'dnt', 'te', 'priority',
}


@dataclass
class EntryInfo:
    index: int
    method: str
    path: str
    status_code: int
    content_type: str
    query_params: list[str] | None = None
    form_params: list[str] | None = None
    custom_headers: list[str] | None = None


@dataclass
class CorrelationInfo:
    variable: str
    source_index: int
    target_index: int
    extractor: str
    location: str


@dataclass
class TrafficContext:
    entries: list[EntryInfo]
    correlations: list[CorrelationInfo]
    entry_index_mapping: dict[int, int]


def prepare_traffic_for_llm(har: HarFile) -> tuple[list[EntryInfo], dict[int, int]]:
    entries_info = []
    index_mapping = {}
    
    for original_index, entry in enumerate(har.log.entries):
        if _should_skip_entry(entry):
            continue
        
        entry_info = _extract_entry_info(entry, original_index)
        
        index_mapping[len(entries_info)] = original_index
        entries_info.append(entry_info)
    
    return entries_info, index_mapping


def prepare_correlations_for_llm(
    report: AnalysisReport,
    index_mapping: dict[int, int] | None = None
) -> list[CorrelationInfo]:
    reverse_mapping = {}
    if index_mapping:
        reverse_mapping = {v: k for k, v in index_mapping.items()}
    
    correlations_info = []
    
    for corr in report.correlations:
        source_idx = corr.response_point.response_index
        target_idx = corr.request_point.request_index
        
        if reverse_mapping:
            if source_idx not in reverse_mapping or target_idx not in reverse_mapping:
                continue
            source_idx = reverse_mapping[source_idx]
            target_idx = reverse_mapping[target_idx]
        
        correlation_info = CorrelationInfo(
            variable=corr.request_point.name,
            source_index=source_idx,
            target_index=target_idx,
            extractor=corr.response_point.extractor_hint.to_str() if corr.response_point.extractor_hint else "",
            location=corr.request_point.location.value,
        )
        correlations_info.append(correlation_info)
    
    return correlations_info


def prepare_full_context(har: HarFile, report: AnalysisReport) -> TrafficContext:
    entries_info, index_mapping = prepare_traffic_for_llm(har)
    correlations_info = prepare_correlations_for_llm(report, index_mapping)
    
    return TrafficContext(
        entries=entries_info,
        correlations=correlations_info,
        entry_index_mapping=index_mapping,
    )


def context_to_dict(context: TrafficContext) -> dict:
    return {
        "entries": [asdict(e) for e in context.entries],
        "correlations": [asdict(c) for c in context.correlations],
    }


def _should_skip_entry(entry: Entry) -> bool:
    path = urlparse(entry.request.url).path.lower()
    
    for ext in SKIP_EXTENSIONS:
        if path.endswith(ext):
            return True
    
    content_type = _get_content_type(entry)
    
    for skip_type in SKIP_CONTENT_TYPES:
        if skip_type in content_type:
            return True
    
    return False


def _get_content_type(entry: Entry) -> str:
    for header in entry.response.headers:
        if header.name.lower() == 'content-type':
            return header.value.lower().split(';')[0].strip()
    return ''


def _extract_entry_info(entry: Entry, index: int) -> EntryInfo:
    request = entry.request
    parsed_url = urlparse(request.url)
    
    path = parsed_url.path
    if len(path) > 100:
        path = path[:97] + "..."
    
    query_params = None
    if request.query_string:
        query_params = [q.name for q in request.query_string if q.name]
    
    form_params = None
    if request.post_data and request.post_data.params:
        form_params = [p.name for p in request.post_data.params if p.name]
    
    custom_headers = []
    for header in request.headers:
        header_name_lower = header.name.lower()
        if header_name_lower not in STANDARD_HEADERS:
            custom_headers.append(header.name)
    
    return EntryInfo(
        index=index,
        method=request.method,
        path=path,
        status_code=entry.response.status,
        content_type=_get_content_type(entry),
        query_params=query_params if query_params else None,
        form_params=form_params if form_params else None,
        custom_headers=custom_headers if custom_headers else None,
    )


