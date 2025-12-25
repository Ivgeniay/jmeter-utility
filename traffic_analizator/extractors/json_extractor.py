from dataclasses import dataclass

from .base import ExtractorHint


@dataclass
class JsonExtractorHint(ExtractorHint):
    json_path: str = ""
    match_nr: int = 1
    default_value: str = "NO_VALUE"
    
    def to_str(self) -> str:
        return f"JSONPath: {self.json_path}"