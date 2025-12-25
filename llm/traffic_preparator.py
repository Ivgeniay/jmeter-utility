from dataclasses import dataclass, field
from urllib.parse import urlparse

from traffic_analizator.models import AnalysisReport, Correlation
from traffic_builder.har_parsers.pydantic_models import Entry, HarFile
from llm.transaction_splitter import TransactionGroup


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
    transaction: str | None = None
    is_anchor: bool = False
    query_params: list[str] | None = None
    form_params: list[str] | None = None
    custom_headers: list[str] | None = None


@dataclass
class ExtractFromInfo:
    entry_index: int
    transaction: str
    path: str
    extractor_type: str
    extractor_expr: str


@dataclass
class UseInInfo:
    entry_index: int
    transaction: str
    path: str
    location: str
    param_name: str


@dataclass
class CorrelationInfo:
    variable: str
    extract_from: ExtractFromInfo
    use_in: list[UseInInfo]


@dataclass
class TransactionInfo:
    name: str
    start_index: int
    end_index: int
    anchor_index: int
    entry_indices: list[int]
    description: str = ""


@dataclass
class FullTrafficContext:
    transactions: list[TransactionInfo]
    correlations: list[CorrelationInfo]
    entries: list[EntryInfo]


def prepare_full_context(
    har: HarFile,
    report: AnalysisReport,
    transactions: list[TransactionGroup] | None = None,
) -> FullTrafficContext:
    entries = har.log.entries
    
    if transactions is None:
        transactions = [TransactionGroup(
            name="S01_01_MainFlow",
            start_index=0,
            end_index=len(entries) - 1,
        )]
    
    transaction_infos = _build_transaction_infos(entries, transactions)
    
    entry_to_transaction = _build_entry_to_transaction_map(transaction_infos)
    
    entries_info = _build_entries_info(entries, entry_to_transaction, transaction_infos)
    
    correlations_info = _build_correlations_info(
        report, entries, entry_to_transaction
    )
    
    return FullTrafficContext(
        transactions=transaction_infos,
        correlations=correlations_info,
        entries=entries_info,
    )


def context_to_dict(context: FullTrafficContext) -> dict:
    return {
        "transactions": [
            {
                "name": t.name,
                "start_index": t.start_index,
                "end_index": t.end_index,
                "anchor_index": t.anchor_index,
                "entry_indices": t.entry_indices,
                "description": t.description,
            }
            for t in context.transactions
        ],
        "correlations": [
            {
                "variable": c.variable,
                "extract_from": {
                    "entry_index": c.extract_from.entry_index,
                    "transaction": c.extract_from.transaction,
                    "path": c.extract_from.path,
                    "extractor_type": c.extract_from.extractor_type,
                    "extractor_expr": c.extract_from.extractor_expr,
                },
                "use_in": [
                    {
                        "entry_index": u.entry_index,
                        "transaction": u.transaction,
                        "path": u.path,
                        "location": u.location,
                        "param_name": u.param_name,
                    }
                    for u in c.use_in
                ],
            }
            for c in context.correlations
        ],
        "entries": [
            {
                "index": e.index,
                "method": e.method,
                "path": e.path,
                "status_code": e.status_code,
                "content_type": e.content_type,
                "transaction": e.transaction,
                "is_anchor": e.is_anchor,
                "query_params": e.query_params,
                "form_params": e.form_params,
                "custom_headers": e.custom_headers,
            }
            for e in context.entries
            if not _is_static_entry(e)
        ],
    }


def _build_transaction_infos(
    entries: list[Entry],
    transactions: list[TransactionGroup],
) -> list[TransactionInfo]:
    result = []
    
    for tx in transactions:
        entry_indices = list(range(tx.start_index, tx.end_index + 1))
        
        result.append(TransactionInfo(
            name=tx.name,
            start_index=tx.start_index,
            end_index=tx.end_index,
            anchor_index=tx.start_index,
            entry_indices=entry_indices,
            description="",
        ))
    
    return result


def _build_entry_to_transaction_map(
    transactions: list[TransactionInfo],
) -> dict[int, str]:
    result = {}
    for tx in transactions:
        for idx in tx.entry_indices:
            result[idx] = tx.name
    return result


def _build_entries_info(
    entries: list[Entry],
    entry_to_transaction: dict[int, str],
    transactions: list[TransactionInfo],
) -> list[EntryInfo]:
    anchor_indices = {tx.anchor_index for tx in transactions}
    
    result = []
    for i, entry in enumerate(entries):
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
            if header.name.lower() not in STANDARD_HEADERS:
                custom_headers.append(header.name)
        
        result.append(EntryInfo(
            index=i,
            method=request.method,
            path=path,
            status_code=entry.response.status,
            content_type=_get_content_type(entry),
            transaction=entry_to_transaction.get(i),
            is_anchor=(i in anchor_indices),
            query_params=query_params if query_params else None,
            form_params=form_params if form_params else None,
            custom_headers=custom_headers if custom_headers else None,
        ))
    
    return result


def _build_correlations_info(
    report: AnalysisReport,
    entries: list[Entry],
    entry_to_transaction: dict[int, str],
) -> list[CorrelationInfo]:
    grouped: dict[str, list[Correlation]] = {}
    for corr in report.correlations:
        var_name = corr.request_point.name
        if var_name not in grouped:
            grouped[var_name] = []
        grouped[var_name].append(corr)
    
    result = []
    for var_name, corrs in grouped.items():
        first_corr = corrs[0]
        source_idx = first_corr.response_point.response_index
        source_entry = entries[source_idx] if source_idx < len(entries) else None
        source_path = urlparse(source_entry.request.url).path if source_entry else ""
        
        hint = first_corr.response_point.extractor_hint
        extractor_type = ""
        extractor_expr = ""
        if hint:
            hint_str = hint.to_str()
            if "JSONPath" in hint_str:
                extractor_type = "JSONPath"
                extractor_expr = hint_str.replace("JSONPath: ", "")
            elif "Regex" in hint_str:
                extractor_type = "Regex"
                extractor_expr = hint_str.replace("Regex: ", "")
            elif "Header" in hint_str:
                extractor_type = "Header"
                extractor_expr = hint_str.replace("Header: ", "")
            elif "Cookie" in hint_str:
                extractor_type = "Cookie"
                extractor_expr = hint_str.replace("Cookie: ", "")
            else:
                extractor_type = "Unknown"
                extractor_expr = hint_str
        
        extract_from = ExtractFromInfo(
            entry_index=source_idx,
            transaction=entry_to_transaction.get(source_idx, "Unknown"),
            path=source_path,
            extractor_type=extractor_type,
            extractor_expr=extractor_expr,
        )
        
        use_in_list = []
        for corr in corrs:
            target_idx = corr.request_point.request_index
            target_entry = entries[target_idx] if target_idx < len(entries) else None
            target_path = urlparse(target_entry.request.url).path if target_entry else ""
            
            use_in_list.append(UseInInfo(
                entry_index=target_idx,
                transaction=entry_to_transaction.get(target_idx, "Unknown"),
                path=target_path,
                location=corr.request_point.location.value,
                param_name=corr.request_point.name,
            ))
        
        result.append(CorrelationInfo(
            variable=var_name,
            extract_from=extract_from,
            use_in=use_in_list,
        ))
    
    return result


def _get_content_type(entry: Entry) -> str:
    for header in entry.response.headers:
        if header.name.lower() == 'content-type':
            return header.value.lower().split(';')[0].strip()
    return ''


def _is_static_entry(entry: EntryInfo) -> bool:
    path_lower = entry.path.lower()
    for ext in SKIP_EXTENSIONS:
        if path_lower.endswith(ext):
            return True
    
    for skip_type in SKIP_CONTENT_TYPES:
        if skip_type in entry.content_type:
            return True
    
    return False