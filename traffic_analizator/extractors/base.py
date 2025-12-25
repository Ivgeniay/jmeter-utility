from abc import ABC, abstractmethod
from dataclasses import dataclass

from jmx_builder.models.tree import TreeElement


@dataclass
class ExtractorHint(ABC):
    variable_name: str | None = None
    
    @abstractmethod
    def to_str(self) -> TreeElement:
        pass