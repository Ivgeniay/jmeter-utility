from .models import (
    Correlation,
    MatchType,
    RequestDataPoint,
    ResponseDataPoint,
)


class TrafficCorrelator:
    
    def __init__(
        self,
        min_value_length: int = 4,
        search_window: int | None = None,
    ):
        self.min_value_length = min_value_length
        self.search_window = search_window
    
    def find_correlations(
        self,
        request_points: list[RequestDataPoint],
        response_points: list[ResponseDataPoint],
    ) -> tuple[list[Correlation], list[RequestDataPoint]]:
        correlations: list[Correlation] = []
        unresolved: list[RequestDataPoint] = []
        
        response_index = self._build_response_index(response_points)
        
        for req_point in request_points:
            if len(req_point.value) < self.min_value_length:
                continue
            
            if self._is_static_value(req_point):
                continue
            
            correlation = self._find_source(req_point, response_points, response_index)
            
            if correlation:
                correlations.append(correlation)
            else:
                unresolved.append(req_point)
        
        return correlations, unresolved
    
    def _build_response_index(
        self, 
        response_points: list[ResponseDataPoint]
    ) -> dict[str, list[ResponseDataPoint]]:
        index: dict[str, list[ResponseDataPoint]] = {}
        
        for point in response_points:
            value = point.value
            if len(value) < self.min_value_length:
                continue
            
            if value not in index:
                index[value] = []
            index[value].append(point)
        
        return index
    
    def _find_source(
        self,
        req_point: RequestDataPoint,
        response_points: list[ResponseDataPoint],
        response_index: dict[str, list[ResponseDataPoint]],
    ) -> Correlation | None:
        req_value = req_point.value
        req_index = req_point.request_index
        
        if req_value in response_index:
            candidates = response_index[req_value]
            for resp_point in candidates:
                if resp_point.response_index < req_index:
                    if self._within_search_window(req_index, resp_point.response_index):
                        return Correlation(
                            request_point=req_point,
                            response_point=resp_point,
                            match_type=MatchType.EXACT,
                        )
        
        if ";" in req_value or "%3B" in req_value:
            correlation = self._find_composite_source(
                req_point, response_points, response_index
            )
            if correlation:
                return correlation
        
        correlation = self._find_contains_source(
            req_point, response_points, response_index
        )
        if correlation:
            return correlation
        
        return None
    
    def _find_composite_source(
        self,
        req_point: RequestDataPoint,
        response_points: list[ResponseDataPoint],
        response_index: dict[str, list[ResponseDataPoint]],
    ) -> Correlation | None:
        req_value = req_point.value
        req_index = req_point.request_index
        
        separator = ";" if ";" in req_value else "%3B"
        parts = req_value.split(separator)
        
        if len(parts) < 2:
            return None
        
        valid_parts = [p for p in parts if len(p) >= self.min_value_length]
        if not valid_parts:
            return None
        
        found_points: list[ResponseDataPoint] = []
        
        for part in valid_parts:
            if part in response_index:
                candidates = response_index[part]
                for resp_point in candidates:
                    if resp_point.response_index < req_index:
                        if self._within_search_window(req_index, resp_point.response_index):
                            found_points.append(resp_point)
                            break
        
        if not found_points:
            return None
        
        first_point = found_points[0]
        
        if len(found_points) > 1:
            generalized_point = self._generalize_composite_points(found_points)
            if generalized_point:
                first_point = generalized_point
        
        return Correlation(
            request_point=req_point,
            response_point=first_point,
            match_type=MatchType.COMPOSITE,
        )
    
    def _generalize_composite_points(
        self,
        points: list[ResponseDataPoint]
    ) -> ResponseDataPoint | None:
        from .extractors import JsonExtractorHint
        import re
        
        json_points = [
            p for p in points 
            if isinstance(p.extractor_hint, JsonExtractorHint)
        ]
        
        if len(json_points) < 2:
            return None
        
        paths = [p.extractor_hint.json_path for p in json_points]
        
        generalized_path = self._generalize_json_paths(paths)
        
        if generalized_path and generalized_path != paths[0]:
            first = json_points[0]
            return ResponseDataPoint(
                response_index=first.response_index,
                url=first.url,
                status_code=first.status_code,
                location=first.location,
                name=first.name,
                value=f"[{len(json_points)} values]",
                extractor_hint=JsonExtractorHint(
                    json_path=generalized_path,
                    match_nr=-1,
                ),
            )
        
        return None
    
    def _generalize_json_paths(self, paths: list[str]) -> str | None:
        import re
        
        if not paths:
            return None
        
        pattern = re.compile(r'\[(\d+)\]')
        
        normalized = []
        for path in paths:
            normalized.append(pattern.sub('[*]', path))
        
        if len(set(normalized)) == 1:
            return normalized[0]
        
        return None
    
    def _find_contains_source(
        self,
        req_point: RequestDataPoint,
        response_points: list[ResponseDataPoint],
        response_index: dict[str, list[ResponseDataPoint]],
    ) -> Correlation | None:
        req_value = req_point.value
        req_index = req_point.request_index
        
        min_search_index = 0
        if self.search_window is not None:
            min_search_index = max(0, req_index - self.search_window)
        
        for resp_point in response_points:
            if resp_point.response_index >= req_index:
                continue
            
            if resp_point.response_index < min_search_index:
                continue
            
            resp_value = resp_point.value
            if len(resp_value) < self.min_value_length:
                continue
            
            if resp_value in req_value and resp_value != req_value:
                return Correlation(
                    request_point=req_point,
                    response_point=resp_point,
                    match_type=MatchType.CONTAINS,
                )
        
        return None
    
    def _within_search_window(self, req_index: int, resp_index: int) -> bool:
        if self.search_window is None:
            return True
        return (req_index - resp_index) <= self.search_window
    
    def _is_static_value(self, req_point: RequestDataPoint) -> bool:
        value = req_point.value.lower()
        name = req_point.name.lower()
        
        static_values = {
            "true", "false", "null", "none", "undefined",
            "yes", "no", "on", "off",
            "get", "post", "put", "delete", "patch",
            "application/json", "application/x-www-form-urlencoded",
            "text/html", "text/plain", "multipart/form-data",
            "utf-8", "utf8", "iso-8859-1",
            "en", "en-us", "ru", "ru-ru",
            "gzip", "deflate", "br",
            "keep-alive", "close",
            "no-cache", "no-store", "max-age=0",
            "cors", "same-origin", "navigate",
            "document", "empty", "script", "style",
        }
        
        if value in static_values:
            return True
        
        if value.isdigit() and len(value) <= 2:
            return True
        
        if name in {"page", "limit", "offset", "size", "count", "per_page", "perpage"}:
            if value.isdigit():
                return True
        
        return False