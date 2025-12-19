from abc import abstractmethod
from jmx_builder.models.base import JMXElement


class PropElement(JMXElement):
    _allow_self_closing: bool = False
    
    def __init__(self, name: str):
        self.name = name


class StringProp(PropElement):
    def __init__(self, name: str, value: str = ""):
        super().__init__(name)
        self.value = value
    
    @property
    def tag_name(self) -> str:
        return "stringProp"
    
    def to_xml(self) -> str:
        return f'<{self.tag_name} name="{self.name}">{self.value}</{self.tag_name}>'


class BoolProp(PropElement):
    def __init__(self, name: str, value: bool = False):
        super().__init__(name)
        self.value = value
    
    @property
    def tag_name(self) -> str:
        return "boolProp"
    
    def to_xml(self) -> str:
        value_str = "true" if self.value else "false"
        return f'<{self.tag_name} name="{self.name}">{value_str}</{self.tag_name}>'


class IntProp(PropElement):
    def __init__(self, name: str, value: int = 0):
        super().__init__(name)
        self.value = value
    
    @property
    def tag_name(self) -> str:
        return "intProp"
    
    def to_xml(self) -> str:
        return f'<{self.tag_name} name="{self.name}">{self.value}</{self.tag_name}>'


class LongProp(PropElement):
    def __init__(self, name: str, value: int = 0):
        super().__init__(name)
        self.value = value
    
    @property
    def tag_name(self) -> str:
        return "longProp"
    
    def to_xml(self) -> str:
        return f'<{self.tag_name} name="{self.name}">{self.value}</{self.tag_name}>'


class CollectionProp(PropElement):
    _allow_self_closing: bool = True
    
    def __init__(self, name: str, items: list[PropElement] | None = None):
        super().__init__(name)
        self.items = items if items is not None else []
    
    @property
    def tag_name(self) -> str:
        return "collectionProp"
    
    def to_xml(self) -> str:
        if not self.items and self._allow_self_closing:
            return f'<{self.tag_name} name="{self.name}"/>'
        
        if not self.items:
            return f'<{self.tag_name} name="{self.name}"></{self.tag_name}>'
        
        parts = [self._indent(item.to_xml()) for item in self.items]
        inner = "\n".join(parts)
        return f'<{self.tag_name} name="{self.name}">\n{inner}\n</{self.tag_name}>'


class ElementProp(PropElement):
    _allow_self_closing: bool = True
    
    def __init__(
        self,
        name: str,
        element_type: str,
        guiclass: str | None = None,
        testclass: str | None = None,
        testname: str | None = None,
        properties: list[PropElement] | None = None
    ):
        super().__init__(name)
        self.element_type = element_type
        self.guiclass = guiclass
        self.testclass = testclass
        self.testname = testname
        self.properties = properties if properties is not None else []
    
    @property
    def tag_name(self) -> str:
        return "elementProp"
    
    def to_xml(self) -> str:
        attrs = [f'name="{self.name}"', f'elementType="{self.element_type}"']
        if self.guiclass:
            attrs.append(f'guiclass="{self.guiclass}"')
        if self.testclass:
            attrs.append(f'testclass="{self.testclass}"')
        if self.testname:
            attrs.append(f'testname="{self.testname}"')
        
        attr_str = " ".join(attrs)
        
        if not self.properties and self._allow_self_closing:
            return f'<{self.tag_name} {attr_str}/>'
        
        if not self.properties:
            return f'<{self.tag_name} {attr_str}></{self.tag_name}>'
        
        parts = [self._indent(prop.to_xml()) for prop in self.properties]
        inner = "\n".join(parts)
        return f'<{self.tag_name} {attr_str}>\n{inner}\n</{self.tag_name}>'
    

class UserDefinedVariablesProp(CollectionProp):
    def __init__(self, name: str = "Arguments.arguments"):
        super().__init__(name)
    
    def add_variable(self, name: str, value: str) -> None:
        variable = ElementProp(
            name=name,
            element_type="Argument",
            properties=[
                StringProp("Argument.name", name),
                StringProp("Argument.value", value),
                StringProp("Argument.metadata", "=")
            ]
        )
        self.items.append(variable)
    
    def remove_variable(self, name: str) -> None:
        self.items = [item for item in self.items if item.name != name]
    
    def get_variable(self, name: str) -> ElementProp | None:
        for item in self.items:
            if item.name == name:
                return item
        return None
    
    def change_variable(self, name: str, new_name: str | None = None, new_value: str | None = None) -> bool:
        variable = self.get_variable(name)
        if variable is None:
            return False
        
        for prop in variable.properties:
            if isinstance(prop, StringProp):
                if prop.name == "Argument.name" and new_name is not None:
                    prop.value = new_name
                    variable.name = new_name
                elif prop.name == "Argument.value" and new_value is not None:
                    prop.value = new_value
        
        return True


class UserDefinedVariablesWithDescProp(UserDefinedVariablesProp):
    def add_variable(self, name: str, value: str, description: str = "") -> None:
        variable = ElementProp(
            name=name,
            element_type="Argument",
            properties=[
                StringProp("Argument.name", name),
                StringProp("Argument.value", value),
                StringProp("Argument.desc", description),
                StringProp("Argument.metadata", "=")
            ]
        )
        self.items.append(variable)
    
    def change_variable(self, name: str, new_name: str | None = None, new_value: str | None = None, new_description: str | None = None) -> bool:
        variable = self.get_variable(name)
        if variable is None:
            return False
        
        for prop in variable.properties:
            if isinstance(prop, StringProp):
                if prop.name == "Argument.name" and new_name is not None:
                    prop.value = new_name
                    variable.name = new_name
                elif prop.name == "Argument.value" and new_value is not None:
                    prop.value = new_value
                elif prop.name == "Argument.desc" and new_description is not None:
                    prop.value = new_description
        
        return True