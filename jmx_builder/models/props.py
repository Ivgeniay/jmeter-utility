from abc import abstractmethod
from jmx_builder.models.base import JMXElement
from jmx_builder.parsers.const import *


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
        return STRING_PROP
    
    def to_xml(self) -> str:
        return f'<{self.tag_name} name="{self.name}">{self.value}</{self.tag_name}>'


class BoolProp(PropElement):
    def __init__(self, name: str, value: bool = False):
        super().__init__(name)
        self.value = value
    
    @property
    def tag_name(self) -> str:
        return BOOL_PROP
    
    def to_xml(self) -> str:
        value_str = "true" if self.value else "false"
        return f'<{self.tag_name} name="{self.name}">{value_str}</{self.tag_name}>'


class IntProp(PropElement):
    def __init__(self, name: str, value: int = 0):
        super().__init__(name)
        self.value = value
    
    @property
    def tag_name(self) -> str:
        return INT_PROP
    
    def to_xml(self) -> str:
        return f'<{self.tag_name} name="{self.name}">{self.value}</{self.tag_name}>'


class LongProp(PropElement):
    def __init__(self, name: str, value: int = 0):
        super().__init__(name)
        self.value = value
    
    @property
    def tag_name(self) -> str:
        return LONG_PROP
    
    def to_xml(self) -> str:
        return f'<{self.tag_name} name="{self.name}">{self.value}</{self.tag_name}>'


class CollectionProp(PropElement):
    _allow_self_closing: bool = True
    
    def __init__(self, name: str, items: list[PropElement] | None = None):
        super().__init__(name)
        self.items = items if items is not None else []
    
    @property
    def tag_name(self) -> str:
        return COLLECTION_PROP
    
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
        return ELEMENT_PROP
    
    def to_xml(self) -> str:
        attrs = [f'name="{self.name}"', f'{ATTR_ELEMENT_TYPE}="{self.element_type}"']
        if self.guiclass:
            attrs.append(f'{ATTR_GUICLASS}="{self.guiclass}"')
        if self.testclass:
            attrs.append(f'{ATTR_TESTCLASS}="{self.testclass}"')
        if self.testname:
            attrs.append(f'{ATTR_TESTNAME}="{self.testname}"')
        
        attr_str = " ".join(attrs)
        
        if not self.properties and self._allow_self_closing:
            return f'<{self.tag_name} {attr_str}/>'
        
        if not self.properties:
            return f'<{self.tag_name} {attr_str}></{self.tag_name}>'
        
        parts = [self._indent(prop.to_xml()) for prop in self.properties]
        inner = "\n".join(parts)
        return f'<{self.tag_name} {attr_str}>\n{inner}\n</{self.tag_name}>'


class UserDefinedVariablesProp(CollectionProp):
    def __init__(self, name: str = ARGUMENTS_ARGUMENTS):
        super().__init__(name)
    
    def add_variable(self, name: str, value: str) -> None:
        variable = ElementProp(
            name=name,
            element_type=ARGUMENT,
            properties=[
                StringProp(ARGUMENT_NAME, name),
                StringProp(ARGUMENT_VALUE, value),
                StringProp(ARGUMENT_METADATA, "=")
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
                if prop.name == ARGUMENT_NAME and new_name is not None:
                    prop.value = new_name
                    variable.name = new_name
                elif prop.name == ARGUMENT_VALUE and new_value is not None:
                    prop.value = new_value
        
        return True


class UserDefinedVariablesWithDescProp(UserDefinedVariablesProp):
    def add_variable(self, name: str, value: str, description: str = "") -> None:
        variable = ElementProp(
            name=name,
            element_type=ARGUMENT,
            properties=[
                StringProp(ARGUMENT_NAME, name),
                StringProp(ARGUMENT_VALUE, value),
                StringProp(ARGUMENT_DESC, description),
                StringProp(ARGUMENT_METADATA, "=")
            ]
        )
        self.items.append(variable)
    
    def change_variable(self, name: str, new_name: str | None = None, new_value: str | None = None, new_description: str | None = None) -> bool:
        variable = self.get_variable(name)
        if variable is None:
            return False
        
        for prop in variable.properties:
            if isinstance(prop, StringProp):
                if prop.name == ARGUMENT_NAME and new_name is not None:
                    prop.value = new_name
                    variable.name = new_name
                elif prop.name == ARGUMENT_VALUE and new_value is not None:
                    prop.value = new_value
                elif prop.name == ARGUMENT_DESC and new_description is not None:
                    prop.value = new_description
        
        return True


class HTTPArgumentsProp(CollectionProp):
    def __init__(self, name: str = ARGUMENTS_ARGUMENTS):
        super().__init__(name)
    
    def add_argument(
        self,
        name: str,
        value: str,
        always_encode: bool = False,
        use_equals: bool = True
    ) -> None:
        argument = ElementProp(
            name=name,
            element_type=HTTP_ARGUMENT,
            properties=[
                BoolProp(HTTPARGUMENT_ALWAYS_ENCODE, always_encode),
                StringProp(ARGUMENT_VALUE, value),
                StringProp(ARGUMENT_METADATA, "="),
                BoolProp(HTTPARGUMENT_USE_EQUALS, use_equals),
                StringProp(ARGUMENT_NAME, name)
            ]
        )
        self.items.append(argument)
    
    def remove_argument(self, name: str) -> None:
        self.items = [item for item in self.items if item.name != name]
    
    def get_argument(self, name: str) -> ElementProp | None:
        for item in self.items:
            if item.name == name:
                return item
        return None
    
    def change_argument(
        self,
        name: str,
        new_name: str | None = None,
        new_value: str | None = None,
        new_always_encode: bool | None = None,
        new_use_equals: bool | None = None
    ) -> bool:
        argument = self.get_argument(name)
        if argument is None:
            return False
        
        for prop in argument.properties:
            if isinstance(prop, StringProp):
                if prop.name == ARGUMENT_NAME and new_name is not None:
                    prop.value = new_name
                    argument.name = new_name
                elif prop.name == ARGUMENT_VALUE and new_value is not None:
                    prop.value = new_value
            elif isinstance(prop, BoolProp):
                if prop.name == HTTPARGUMENT_ALWAYS_ENCODE and new_always_encode is not None:
                    prop.value = new_always_encode
                elif prop.name == HTTPARGUMENT_USE_EQUALS and new_use_equals is not None:
                    prop.value = new_use_equals
        
        return True
    
    def clear(self) -> None:
        self.items = []


class HTTPFileArgsProp(CollectionProp):
    def __init__(self, name: str = HTTPFILEARGS_FILES):
        super().__init__(name)
    
    def add_file(
        self,
        path: str,
        param_name: str = "",
        mime_type: str = "application/octet-stream"
    ) -> None:
        file_arg = ElementProp(
            name=path,
            element_type="HTTPFileArg",
            properties=[
                StringProp(HTTPFILEARG_MIMETYPE, mime_type),
                StringProp(HTTPFILEARG_PATH, path),
                StringProp(HTTPFILEARG_PARAMNAME, param_name)
            ]
        )
        self.items.append(file_arg)
    
    def remove_file(self, path: str) -> None:
        self.items = [item for item in self.items if item.name != path]
    
    def get_file(self, path: str) -> ElementProp | None:
        for item in self.items:
            if item.name == path:
                return item
        return None
    
    def change_file(
        self,
        path: str,
        new_path: str | None = None,
        new_param_name: str | None = None,
        new_mime_type: str | None = None
    ) -> bool:
        file_arg = self.get_file(path)
        if file_arg is None:
            return False
        
        for prop in file_arg.properties:
            if isinstance(prop, StringProp):
                if prop.name == HTTPFILEARG_PATH and new_path is not None:
                    prop.value = new_path
                    file_arg.name = new_path
                elif prop.name == HTTPFILEARG_PARAMNAME and new_param_name is not None:
                    prop.value = new_param_name
                elif prop.name == HTTPFILEARG_MIMETYPE and new_mime_type is not None:
                    prop.value = new_mime_type
        
        return True
    
    def clear(self) -> None:
        self.items = []


class CookiesProp(CollectionProp):
    def __init__(self, name: str = "CookieManager.cookies"):
        super().__init__(name)
    
    def add_cookie(
        self,
        name: str,
        value: str,
        domain: str,
        path: str = "/",
        secure: bool = False,
        expires: int = 0,
        path_specified: bool = True,
        domain_specified: bool = True
    ) -> None:
        cookie = ElementProp(
            name=name,
            element_type="Cookie",
            testname=name,
            properties=[
                StringProp(COOKIE_VALUE, value),
                StringProp(COOKIE_DOMAIN, domain),
                StringProp(COOKIE_PATH, path),
                BoolProp(COOKIE_SECURE, secure),
                LongProp(COOKIE_EXPIRES, expires),
                BoolProp(COOKIE_PATH_SPECIFIED, path_specified),
                BoolProp(COOKIE_DOMAIN_SPECIFIED, domain_specified)
            ]
        )
        self.items.append(cookie)
    
    def remove_cookie(self, name: str) -> None:
        self.items = [item for item in self.items if item.name != name]
    
    def get_cookie(self, name: str) -> ElementProp | None:
        for item in self.items:
            if item.name == name:
                return item
        return None
    
    def change_cookie(
        self,
        name: str,
        new_name: str | None = None,
        new_value: str | None = None,
        new_domain: str | None = None,
        new_path: str | None = None,
        new_secure: bool | None = None,
        new_expires: int | None = None,
        new_path_specified: bool | None = None,
        new_domain_specified: bool | None = None
    ) -> bool:
        cookie = self.get_cookie(name)
        if cookie is None:
            return False
        
        if new_name is not None:
            cookie.name = new_name
            cookie.testname = new_name
        
        for prop in cookie.properties:
            if isinstance(prop, StringProp):
                if prop.name == COOKIE_VALUE and new_value is not None:
                    prop.value = new_value
                elif prop.name == COOKIE_DOMAIN and new_domain is not None:
                    prop.value = new_domain
                elif prop.name == COOKIE_PATH and new_path is not None:
                    prop.value = new_path
            elif isinstance(prop, BoolProp):
                if prop.name == COOKIE_SECURE and new_secure is not None:
                    prop.value = new_secure
                elif prop.name == COOKIE_PATH_SPECIFIED and new_path_specified is not None:
                    prop.value = new_path_specified
                elif prop.name == COOKIE_DOMAIN_SPECIFIED and new_domain_specified is not None:
                    prop.value = new_domain_specified
            elif isinstance(prop, LongProp):
                if prop.name == COOKIE_EXPIRES and new_expires is not None:
                    prop.value = new_expires
        
        return True
    
    def clear(self) -> None:
        self.items = []


class HeadersProp(CollectionProp):
    def __init__(self, name: str = "HeaderManager.headers"):
        super().__init__(name)
    
    def add_header(self, name: str, value: str) -> None:
        header = ElementProp(
            name="",
            element_type="Header",
            properties=[
                StringProp(HEADER_NAME, name),
                StringProp(HEADER_VALUE, value)
            ]
        )
        self.items.append(header)
    
    def remove_header(self, name: str) -> None:
        self.items = [
            item for item in self.items
            if not any(
                isinstance(p, StringProp) and p.name == HEADER_NAME and p.value == name
                for p in item.properties
            )
        ]
    
    def get_header(self, name: str) -> ElementProp | None:
        for item in self.items:
            for prop in item.properties:
                if isinstance(prop, StringProp) and prop.name == HEADER_NAME and prop.value == name:
                    return item
        return None
    
    def change_header(
        self,
        name: str,
        new_name: str | None = None,
        new_value: str | None = None
    ) -> bool:
        header = self.get_header(name)
        if header is None:
            return False
        
        for prop in header.properties:
            if isinstance(prop, StringProp):
                if prop.name == HEADER_NAME and new_name is not None:
                    prop.value = new_name
                elif prop.name == HEADER_VALUE and new_value is not None:
                    prop.value = new_value
        
        return True
    
    def clear(self) -> None:
        self.items = []


class DoubleProp(JMXElement):
    def __init__(self, name: str, value: float = 0.0, saved_value: float = 0.0):
        self.name = name
        self.value = value
        self.saved_value = saved_value
    
    @property
    def tag_name(self) -> str:
        return "doubleProp"
    
    def to_xml(self) -> str:
        parts = [
            f"<name>{self.name}</name>",
            f"<value>{self.value}</value>",
            f"<savedValue>{self.saved_value}</savedValue>"
        ]
        inner = "\n".join([self._indent(p) for p in parts])
        return f"<{self.tag_name}>\n{inner}\n</{self.tag_name}>"


class FloatProperty(JMXElement):
    def __init__(self, name: str, value: float = 0.0, saved_value: float = 0.0):
        self.name = name
        self.value = value
        self.saved_value = saved_value
    
    @property
    def tag_name(self) -> str:
        return "FloatProperty"
    
    def to_xml(self) -> str:
        parts = [
            f"<name>{self.name}</name>",
            f"<value>{self.value}</value>",
            f"<savedValue>{self.saved_value}</savedValue>"
        ]
        inner = "\n".join([self._indent(p) for p in parts])
        return f"<{self.tag_name}>\n{inner}\n</{self.tag_name}>"


