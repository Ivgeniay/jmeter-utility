from dataclasses import dataclass, field
from enum import Enum

from traffic_analizator.extractors.base import ExtractorHint


class DataLocation(Enum):
    HEADER = "header"
    QUERY_PARAM = "query_param"
    FORM_PARAM = "form_param"
    BODY_JSON = "body_json"
    BODY_RAW = "body_raw"
    COOKIE = "cookie"
    SET_COOKIE = "set_cookie"
    RESPONSE_HEADER = "response_header"
    RESPONSE_JSON = "response_json"
    RESPONSE_HTML = "response_html"
    RESPONSE_RAW = "response_raw"


class MatchType(Enum):
    EXACT = "exact"
    CONTAINS = "contains"
    COMPOSITE = "composite"


@dataclass
class RequestDataPoint:
    request_index: int
    url: str
    method: str
    location: DataLocation
    name: str
    value: str
    json_path: str | None = None


@dataclass
class ResponseDataPoint:
    response_index: int
    url: str
    status_code: int
    location: DataLocation
    name: str | None
    value: str
    extractor_hint: ExtractorHint


@dataclass
class Correlation:
    request_point: RequestDataPoint
    response_point: ResponseDataPoint
    match_type: MatchType

    def to_str(self) -> str:
        req = self.request_point
        resp = self.response_point
        
        lines = [
            f"[{self.match_type.value.upper()}] {req.name}",
            f"  Запрос #{req.request_index}: {req.method} {req.url}",
            f"    Расположение: {req.location.value}",
            f"    Значение: {req.value[:80]}{'...' if len(req.value) > 80 else ''}",
            f"  Источник #{resp.response_index}: {resp.url}",
            f"    Расположение: {resp.location.value}",
            f"    Экстрактор: {resp.extractor_hint.to_str()}",
        ]
        
        return "\n".join(lines)


@dataclass
class AnalysisReport:
    request_data_points: list[RequestDataPoint] = field(default_factory=list)
    response_data_points: list[ResponseDataPoint] = field(default_factory=list)
    correlations: list[Correlation] = field(default_factory=list)
    unresolved: list[RequestDataPoint] = field(default_factory=list)

    def to_str(self) -> str:
        lines = [
            "=" * 80,
            "ОТЧЁТ АНАЛИЗА ТРАФИКА",
            "=" * 80,
            "",
            f"Всего точек данных в запросах: {len(self.request_data_points)}",
            f"Всего точек данных в ответах: {len(self.response_data_points)}",
            f"Найдено корреляций: {len(self.correlations)}",
            f"Не разрешено (статика или генерируется на клиенте): {len(self.unresolved)}",
            "",
        ]
        
        if self.correlations:
            lines.append("-" * 80)
            lines.append("КОРРЕЛЯЦИИ (требуют параметризации)")
            lines.append("-" * 80)
            lines.append("")
            
            for i, corr in enumerate(self.correlations, 1):
                lines.append(f"{i}. {corr.to_str()}")
                lines.append("")
        
        if self.unresolved:
            lines.append("-" * 80)
            lines.append("НЕ РАЗРЕШЕНО (проверьте вручную)")
            lines.append("-" * 80)
            lines.append("")
            
            for i, req in enumerate(self.unresolved, 1):
                lines.append(f"{i}. [{req.location.value}] {req.name}")
                lines.append(f"   Запрос #{req.request_index}: {req.method} {req.url}")
                lines.append(f"   Значение: {req.value[:80]}{'...' if len(req.value) > 80 else ''}")
                lines.append("")
        
        lines.append("=" * 80)
        
        return "\n".join(lines)