from abc import ABC, abstractmethod


class JMXElement(ABC):
    @abstractmethod
    def to_xml(self) -> str:
        pass

    @property
    @abstractmethod
    def tag_name(self) -> str:
        pass

    def _indent(self, text: str) -> str:
        lines = text.split("\n")
        return "\n".join("  " + line for line in lines)
    

class IHierarchable(ABC):
    children: list
    
    @abstractmethod
    def add_child(self, element, index: int | None = None) -> None:
        pass
    
    @abstractmethod
    def remove_child(self, element) -> None:
        pass
    
    @abstractmethod
    def reindex(self, element, new_index: int) -> None:
        pass