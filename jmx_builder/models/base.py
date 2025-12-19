from abc import ABC, abstractmethod


class JMXElement(ABC):
    @abstractmethod
    def to_xml(self, indent: int = 0) -> str:
        pass

    @property
    @abstractmethod
    def tag_name(self) -> str:
        pass

    def _indent(self, text: str) -> str:
        lines = text.split("\n")
        return "\n".join("  " + line for line in lines)