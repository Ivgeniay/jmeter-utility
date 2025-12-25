from dataclasses import dataclass

from .base import ExtractorHint


@dataclass
class CookieExtractorHint(ExtractorHint):
    cookie_name: str = ""
    
    def to_str(self) -> str:
        return f"Cookie: {self.cookie_name}"