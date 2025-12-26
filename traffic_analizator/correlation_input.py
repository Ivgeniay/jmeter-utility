from dataclasses import dataclass, field
from collections import defaultdict

from llm.models.correlation import CorrelationInput, TargetUsage, UsageType
from traffic_analizator.extractors.json_extractor import JsonExtractorHint
from traffic_analizator.models import AnalysisReport, Correlation, DataLocation, MatchType
from traffic_builder.har_parsers.pydantic_models import HarFile


LOCATION_TO_USAGE_TYPE = {
    DataLocation.QUERY_PARAM: UsageType.QUERY,
    DataLocation.FORM_PARAM: UsageType.BODY,
    DataLocation.BODY_JSON: UsageType.BODY,
    DataLocation.BODY_RAW: UsageType.BODY,
    DataLocation.HEADER: UsageType.HEADER,
    DataLocation.COOKIE: UsageType.HEADER,
}


@dataclass
class SourceKey:
    response_index: int
    location: DataLocation
    json_path_generalized: str | None
    
    def __hash__(self):
        return hash((self.response_index, self.location, self.json_path_generalized))
    
    def __eq__(self, other):
        if not isinstance(other, SourceKey):
            return False
        return (
            self.response_index == other.response_index
            and self.location == other.location
            and self.json_path_generalized == other.json_path_generalized
        )


@dataclass
class TargetKey:
    request_index: int
    location: DataLocation
    parameter_name: str
    
    def __hash__(self):
        return hash((self.request_index, self.location, self.parameter_name))
    
    def __eq__(self, other):
        if not isinstance(other, TargetKey):
            return False
        return (
            self.request_index == other.request_index
            and self.location == other.location
            and self.parameter_name == other.parameter_name
        )


@dataclass
class GroupedCorrelation:
    source_key: SourceKey
    correlations: list[Correlation] = field(default_factory=list)
    target_values: dict[TargetKey, list[str]] = field(default_factory=lambda: defaultdict(list))


class CorrelationGrouper:
    
    def __init__(self, har: HarFile):
        self.har = har
        self.entries = har.log.entries
    
    def group(self, report: AnalysisReport) -> list[CorrelationInput]:
        grouped = self._group_by_source(report.correlations)
        
        correlation_inputs = []
        for source_key, group in grouped.items():
            corr_input = self._build_correlation_input(source_key, group)
            if corr_input:
                correlation_inputs.append(corr_input)
        
        return correlation_inputs
    
    def _group_by_source(
        self, 
        correlations: list[Correlation]
    ) -> dict[SourceKey, GroupedCorrelation]:
        groups: dict[SourceKey, GroupedCorrelation] = {}
        
        for corr in correlations:
            source_key = self._make_source_key(corr)
            target_key = self._make_target_key(corr)
            
            if source_key not in groups:
                groups[source_key] = GroupedCorrelation(source_key=source_key)
            
            groups[source_key].correlations.append(corr)
            groups[source_key].target_values[target_key].append(corr.request_point.value)
        
        return groups
    
    def _make_source_key(self, corr: Correlation) -> SourceKey:
        resp = corr.response_point
        
        json_path_gen = None
        if isinstance(resp.extractor_hint, JsonExtractorHint):
            json_path_gen = self._generalize_json_path(resp.extractor_hint.json_path)
        
        return SourceKey(
            response_index=resp.response_index,
            location=resp.location,
            json_path_generalized=json_path_gen,
        )
    
    def _make_target_key(self, corr: Correlation) -> TargetKey:
        req = corr.request_point
        return TargetKey(
            request_index=req.request_index,
            location=req.location,
            parameter_name=req.name,
        )
    
    def _generalize_json_path(self, path: str) -> str:
        import re
        return re.sub(r'\[\d+\]', '[*]', path)
    
    def _build_correlation_input(
        self, 
        source_key: SourceKey, 
        group: GroupedCorrelation
    ) -> CorrelationInput | None:
        if not group.correlations:
            return None
        
        first_corr = group.correlations[0]
        resp_point = first_corr.response_point
        
        entry = self.entries[source_key.response_index]
        response_body = ""
        if entry.response.content and entry.response.content.text:
            response_body = entry.response.content.text
        
        content_type = ""
        if entry.response.content and entry.response.content.mime_type:
            content_type = entry.response.content.mime_type
        
        all_values = set()
        for corr in group.correlations:
            if corr.match_type == MatchType.COMPOSITE:
                separator = ";" if ";" in corr.request_point.value else "%3B"
                parts = corr.request_point.value.split(separator)
                all_values.update(p for p in parts if len(p) >= 4)
            else:
                all_values.add(corr.response_point.value)
        
        unique_values = set(all_values)
        
        target_usages = []
        for target_key, values in group.target_values.items():
            raw_value = values[0] if values else ""
            
            if ";" in raw_value or "%3B" in raw_value:
                separator = ";" if ";" in raw_value else "%3B"
                values_count = len(raw_value.split(separator))
            else:
                values_count = len(values)
            
            usage_type = LOCATION_TO_USAGE_TYPE.get(target_key.location, UsageType.QUERY)
            
            target_usages.append(TargetUsage(
                entry_index=target_key.request_index,
                parameter_name=target_key.parameter_name,
                usage_type=usage_type,
                values_in_request=values_count,
                raw_value=raw_value,
            ))
        
        target_usages.sort(key=lambda t: t.entry_index)
        
        value_path_hint = ""
        if isinstance(resp_point.extractor_hint, JsonExtractorHint):
            value_path_hint = source_key.json_path_generalized or resp_point.extractor_hint.json_path
        elif hasattr(resp_point.extractor_hint, 'pattern'):
            value_path_hint = f"regex: {resp_point.extractor_hint.pattern}"
        elif hasattr(resp_point.extractor_hint, 'header_name'):
            value_path_hint = f"header: {resp_point.extractor_hint.header_name}"
        elif hasattr(resp_point.extractor_hint, 'cookie_name'):
            value_path_hint = f"cookie: {resp_point.extractor_hint.cookie_name}"
        
        value_sample = resp_point.value
        if value_sample.startswith("[") and "values]" in value_sample:
            for corr in group.correlations:
                if corr.response_point.value and not corr.response_point.value.startswith("["):
                    value_sample = corr.response_point.value
                    break
        
        return CorrelationInput(
            source_entry_index=source_key.response_index,
            source_request_path=f"{entry.request.method} {entry.request.url}",
            source_response_body=response_body,
            source_content_type=content_type,
            target_usages=target_usages,
            value_sample=value_sample[:100],
            value_path_hint=value_path_hint,
            values_total=len(unique_values),
            usage_count=len(target_usages),
        )


def group_correlations(report: AnalysisReport, har: HarFile) -> list[CorrelationInput]:
    grouper = CorrelationGrouper(har)
    return grouper.group(report)