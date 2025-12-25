from dataclasses import dataclass

from .base import ExtractorHint


@dataclass
class RegexExtractorHint(ExtractorHint):
    pattern: str = ""
    group: int = 1
    match_nr: int = 1
    default_value: str = "NO_VALUE"
    
    def to_str(self) -> str:
        return f"Regex: {self.pattern}"