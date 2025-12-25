from traffic_builder.har_parsers.pydantic_models import HarFile

from .models import AnalysisReport
from .extractor import TrafficExtractor
from .correlator import TrafficCorrelator


class TrafficAnalyzer:
    
    def __init__(
        self,
        min_value_length: int = 4,
        search_window: int | None = None,
        ignore_cookies: bool = False,
    ):
        self.min_value_length = min_value_length
        self.search_window = search_window
        self.ignore_cookies = ignore_cookies
    
    def analyze(self, har: HarFile) -> AnalysisReport:
        extractor = TrafficExtractor(har, ignore_cookies=self.ignore_cookies)
        request_points, response_points = extractor.extract_all()
        
        correlator = TrafficCorrelator(
            min_value_length=self.min_value_length,
            search_window=self.search_window,
        )
        correlations, unresolved = correlator.find_correlations(
            request_points, response_points
        )
        
        report = AnalysisReport(
            request_data_points=request_points,
            response_data_points=response_points,
            correlations=correlations,
            unresolved=unresolved,
        )
        
        return report


def analyze_har(
    har: HarFile,
    min_value_length: int = 4,
    search_window: int | None = None,
    ignore_cookies: bool = False,
) -> AnalysisReport:
    analyzer = TrafficAnalyzer(
        min_value_length=min_value_length,
        search_window=search_window,
        ignore_cookies=ignore_cookies,
    )
    return analyzer.analyze(har)