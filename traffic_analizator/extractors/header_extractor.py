from dataclasses import dataclass

from .base import ExtractorHint


@dataclass
class HeaderExtractorHint(ExtractorHint):
    header_name: str = ""
    
    def to_str(self) -> str:
        return f"Header: {self.header_name}"