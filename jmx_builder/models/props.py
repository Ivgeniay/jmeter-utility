from abc import abstractmethod
from jmx_builder.models.base import JMXElement
from jmx_builder.models.dto import ArgumentData, ArgumentWithDescData, AuthorizationData, CookieData, DNSHostData, HTTPArgumentData, HTTPFileData, HeaderData
from jmx_builder.parsers.const import *


class PropElement(JMXElement):
    _allow_self_closing: bool = False
    
    def __init__(self, name: str):
        self.name = name

    @staticmethod
    def _escape_xml(value: str) -> str:
        if not value:
            return value
        return (value
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )


class StringProp(PropElement):
    def __init__(self, name: str, value: str = ""):
        super().__init__(name)
        self.value = value
    
    @property
    def tag_name(self) -> str:
        return STRING_PROP

    def to_xml(self) -> str:
        escaped_value = self._escape_xml(self.value)
        return f'<{self.tag_name} name="{self.name}">{escaped_value}</{self.tag_name}>'


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
    
    def get_variable_value(self, name: str) -> str | None:
        variable = self.get_variable(name)
        if variable is None:
            return None
        for prop in variable.properties:
            if isinstance(prop, StringProp) and prop.name == ARGUMENT_VALUE:
                return prop.value
        return None

    def has_variable(self, name: str, value: str | None = None) -> bool:
        if value is None:
            return self.get_variable(name) is not None
        return self.get_variable_value(name) == value
    
    def to_data(self) -> list[ArgumentData]:
        result = []
        for item in self.items:
            name = None
            value = None
            for prop in item.properties:
                if isinstance(prop, StringProp):
                    if prop.name == ARGUMENT_NAME:
                        name = prop.value
                    elif prop.name == ARGUMENT_VALUE:
                        value = prop.value
            if name is not None and value is not None:
                result.append(ArgumentData(name=name, value=value))
        return result

    def from_data(self, data: list[ArgumentData]) -> None:
        self.items = []
        for item in data:
            self.add_variable(item.name, item.value)
    
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
    
    def get_variable_description(self, name: str) -> str | None:
        variable = self.get_variable(name)
        if variable is None:
            return None
        for prop in variable.properties:
            if isinstance(prop, StringProp) and prop.name == ARGUMENT_DESC:
                return prop.value
        return None

    def to_data(self) -> list[ArgumentWithDescData]:
        result = []
        for item in self.items:
            name = None
            value = None
            description = ""
            for prop in item.properties:
                if isinstance(prop, StringProp):
                    if prop.name == ARGUMENT_NAME:
                        name = prop.value
                    elif prop.name == ARGUMENT_VALUE:
                        value = prop.value
                    elif prop.name == ARGUMENT_DESC:
                        description = prop.value
            if name is not None and value is not None:
                result.append(ArgumentWithDescData(name=name, value=value, description=description))
        return result

    def from_data(self, data: list[ArgumentWithDescData]) -> None:
        self.items = []
        for item in data:
            self.add_variable(item.name, item.value, item.description)
    
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
    
    def get_argument_value(self, name: str) -> str | None:
        argument = self.get_argument(name)
        if argument is None:
            return None
        for prop in argument.properties:
            if isinstance(prop, StringProp) and prop.name == ARGUMENT_VALUE:
                return prop.value
        return None

    def has_argument(self, name: str, value: str | None = None) -> bool:
        if value is None:
            return self.get_argument(name) is not None
        return self.get_argument_value(name) == value
    
    def to_data(self) -> list[HTTPArgumentData]:
        result = []
        for item in self.items:
            name = ""
            value = ""
            always_encode = False
            use_equals = True
            for prop in item.properties:
                if isinstance(prop, StringProp):
                    if prop.name == ARGUMENT_NAME:
                        name = prop.value
                    elif prop.name == ARGUMENT_VALUE:
                        value = prop.value
                elif isinstance(prop, BoolProp):
                    if prop.name == HTTPARGUMENT_ALWAYS_ENCODE:
                        always_encode = prop.value
                    elif prop.name == HTTPARGUMENT_USE_EQUALS:
                        use_equals = prop.value
            result.append(HTTPArgumentData(
                name=name,
                value=value,
                always_encode=always_encode,
                use_equals=use_equals
            ))
        return result

    def from_data(self, data: list[HTTPArgumentData]) -> None:
        self.clear()
        for item in data:
            self.add_argument(item.name, item.value, item.always_encode, item.use_equals)
    
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
    
    def get_file_mime_type(self, path: str) -> str | None:
        file_arg = self.get_file(path)
        if file_arg is None:
            return None
        for prop in file_arg.properties:
            if isinstance(prop, StringProp) and prop.name == HTTPFILEARG_MIMETYPE:
                return prop.value
        return None

    def get_file_param_name(self, path: str) -> str | None:
        file_arg = self.get_file(path)
        if file_arg is None:
            return None
        for prop in file_arg.properties:
            if isinstance(prop, StringProp) and prop.name == HTTPFILEARG_PARAMNAME:
                return prop.value
        return None

    def has_file(self, path: str) -> bool:
        return self.get_file(path) is not None
    
    def to_data(self) -> list[HTTPFileData]:
        result = []
        for item in self.items:
            path = ""
            param_name = ""
            mime_type = "application/octet-stream"
            for prop in item.properties:
                if isinstance(prop, StringProp):
                    if prop.name == HTTPFILEARG_PATH:
                        path = prop.value
                    elif prop.name == HTTPFILEARG_PARAMNAME:
                        param_name = prop.value
                    elif prop.name == HTTPFILEARG_MIMETYPE:
                        mime_type = prop.value
            if path:
                result.append(HTTPFileData(path=path, param_name=param_name, mime_type=mime_type))
        return result

    def from_data(self, data: list[HTTPFileData]) -> None:
        self.clear()
        for item in data:
            self.add_file(item.path, item.param_name, item.mime_type)
    
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
    
    def get_cookie_value(self, name: str) -> str | None:
        cookie = self.get_cookie(name)
        if cookie is None:
            return None
        for prop in cookie.properties:
            if isinstance(prop, StringProp) and prop.name == COOKIE_VALUE:
                return prop.value
        return None

    def get_cookie_domain(self, name: str) -> str | None:
        cookie = self.get_cookie(name)
        if cookie is None:
            return None
        for prop in cookie.properties:
            if isinstance(prop, StringProp) and prop.name == COOKIE_DOMAIN:
                return prop.value
        return None

    def has_cookie(self, name: str, value: str | None = None) -> bool:
        if value is None:
            return self.get_cookie(name) is not None
        return self.get_cookie_value(name) == value
    
    def to_data(self) -> list[CookieData]:
        result = []
        for item in self.items:
            name = item.name
            value = ""
            domain = ""
            path = "/"
            secure = False
            expires = 0
            path_specified = True
            domain_specified = True
            for prop in item.properties:
                if isinstance(prop, StringProp):
                    if prop.name == COOKIE_VALUE:
                        value = prop.value
                    elif prop.name == COOKIE_DOMAIN:
                        domain = prop.value
                    elif prop.name == COOKIE_PATH:
                        path = prop.value
                elif isinstance(prop, BoolProp):
                    if prop.name == COOKIE_SECURE:
                        secure = prop.value
                    elif prop.name == COOKIE_PATH_SPECIFIED:
                        path_specified = prop.value
                    elif prop.name == COOKIE_DOMAIN_SPECIFIED:
                        domain_specified = prop.value
                elif isinstance(prop, LongProp):
                    if prop.name == COOKIE_EXPIRES:
                        expires = prop.value
            result.append(CookieData(
                name=name,
                value=value,
                domain=domain,
                path=path,
                secure=secure,
                expires=expires,
                path_specified=path_specified,
                domain_specified=domain_specified
            ))
        return result

    def from_data(self, data: list[CookieData]) -> None:
        self.clear()
        for item in data:
            self.add_cookie(
                item.name, item.value, item.domain, item.path,
                item.secure, item.expires, item.path_specified, item.domain_specified
            )
    
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
    
    def get_header_value(self, name: str) -> str | None:
        header = self.get_header(name)
        if header is None:
            return None
        for prop in header.properties:
            if isinstance(prop, StringProp) and prop.name == HEADER_VALUE:
                return prop.value
        return None

    def has_header(self, name: str, value: str | None = None) -> bool:
        if value is None:
            return self.get_header(name) is not None
        return self.get_header_value(name) == value
    
    def to_data(self) -> list[HeaderData]:
        result = []
        for item in self.items:
            name = None
            value = None
            for prop in item.properties:
                if isinstance(prop, StringProp):
                    if prop.name == HEADER_NAME:
                        name = prop.value
                    elif prop.name == HEADER_VALUE:
                        value = prop.value
            if name is not None and value is not None:
                result.append(HeaderData(name=name, value=value))
        return result

    def from_data(self, data: list[HeaderData]) -> None:
        self.clear()
        for item in data:
            self.add_header(item.name, item.value)
    
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


class SampleSaveConfiguration(JMXElement):
    def __init__(self):
        self.time: bool = True
        self.latency: bool = True
        self.timestamp: bool = True
        self.success: bool = True
        self.label: bool = True
        self.code: bool = True
        self.message: bool = True
        self.thread_name: bool = True
        self.data_type: bool = True
        self.encoding: bool = False
        self.assertions: bool = True
        self.subresults: bool = True
        self.response_data: bool = False
        self.sampler_data: bool = False
        self.xml: bool = False
        self.field_names: bool = True
        self.response_headers: bool = False
        self.request_headers: bool = False
        self.response_data_on_error: bool = False
        self.save_assertion_results_failure_message: bool = True
        self.assertions_results_to_save: int = 0
        self.bytes: bool = True
        self.sent_bytes: bool = True
        self.url: bool = True
        self.file_name: bool = False
        self.hostname: bool = False
        self.thread_counts: bool = True
        self.sample_count: bool = False
        self.idle_time: bool = True
        self.connect_time: bool = True
    
    @property
    def tag_name(self) -> str:
        return "objProp"
    
    def _bool_to_str(self, value: bool) -> str:
        return "true" if value else "false"
    
    def to_xml(self) -> str:
        config_parts = [
            f"<time>{self._bool_to_str(self.time)}</time>",
            f"<latency>{self._bool_to_str(self.latency)}</latency>",
            f"<timestamp>{self._bool_to_str(self.timestamp)}</timestamp>",
            f"<success>{self._bool_to_str(self.success)}</success>",
            f"<label>{self._bool_to_str(self.label)}</label>",
            f"<code>{self._bool_to_str(self.code)}</code>",
            f"<message>{self._bool_to_str(self.message)}</message>",
            f"<threadName>{self._bool_to_str(self.thread_name)}</threadName>",
            f"<dataType>{self._bool_to_str(self.data_type)}</dataType>",
            f"<encoding>{self._bool_to_str(self.encoding)}</encoding>",
            f"<assertions>{self._bool_to_str(self.assertions)}</assertions>",
            f"<subresults>{self._bool_to_str(self.subresults)}</subresults>",
            f"<responseData>{self._bool_to_str(self.response_data)}</responseData>",
            f"<samplerData>{self._bool_to_str(self.sampler_data)}</samplerData>",
            f"<xml>{self._bool_to_str(self.xml)}</xml>",
            f"<fieldNames>{self._bool_to_str(self.field_names)}</fieldNames>",
            f"<responseHeaders>{self._bool_to_str(self.response_headers)}</responseHeaders>",
            f"<requestHeaders>{self._bool_to_str(self.request_headers)}</requestHeaders>",
            f"<responseDataOnError>{self._bool_to_str(self.response_data_on_error)}</responseDataOnError>",
            f"<saveAssertionResultsFailureMessage>{self._bool_to_str(self.save_assertion_results_failure_message)}</saveAssertionResultsFailureMessage>",
            f"<assertionsResultsToSave>{self.assertions_results_to_save}</assertionsResultsToSave>",
            f"<bytes>{self._bool_to_str(self.bytes)}</bytes>",
            f"<sentBytes>{self._bool_to_str(self.sent_bytes)}</sentBytes>",
            f"<url>{self._bool_to_str(self.url)}</url>",
            f"<fileName>{self._bool_to_str(self.file_name)}</fileName>",
            f"<hostname>{self._bool_to_str(self.hostname)}</hostname>",
            f"<threadCounts>{self._bool_to_str(self.thread_counts)}</threadCounts>",
            f"<sampleCount>{self._bool_to_str(self.sample_count)}</sampleCount>",
            f"<idleTime>{self._bool_to_str(self.idle_time)}</idleTime>",
            f"<connectTime>{self._bool_to_str(self.connect_time)}</connectTime>",
        ]
        
        config_inner = "\n".join([self._indent(self._indent(p)) for p in config_parts])
        value_content = f'<value class="SampleSaveConfiguration">\n{config_inner}\n  </value>'
        
        parts = [
            "<name>saveConfig</name>",
            value_content
        ]
        inner = "\n".join([self._indent(p) for p in parts])
        return f"<{self.tag_name}>\n{inner}\n</{self.tag_name}>"


class AuthorizationsProp(CollectionProp):
    def __init__(self, name: str = "AuthManager.auth_list"):
        super().__init__(name)
    
    def add_authorization(
        self,
        url: str,
        username: str,
        password: str,
        domain: str = "",
        realm: str = "",
        mechanism: str = "BASIC"
    ) -> None:
        auth = ElementProp(
            name="",
            element_type="Authorization",
            properties=[
                StringProp(AUTHORIZATION_URL, url),
                StringProp(AUTHORIZATION_USERNAME, username),
                StringProp(AUTHORIZATION_PASSWORD, password),
                StringProp(AUTHORIZATION_DOMAIN, domain),
                StringProp(AUTHORIZATION_REALM, realm),
                StringProp(AUTHORIZATION_MECHANISM, mechanism)
            ]
        )
        self.items.append(auth)
    
    def remove_authorization(self, url: str) -> None:
        self.items = [
            item for item in self.items
            if not any(
                isinstance(p, StringProp) and p.name == AUTHORIZATION_URL and p.value == url
                for p in item.properties
            )
        ]
    
    def get_authorization_username(self, url: str) -> str | None:
        auth = self.get_authorization(url)
        if auth is None:
            return None
        for prop in auth.properties:
            if isinstance(prop, StringProp) and prop.name == AUTHORIZATION_USERNAME:
                return prop.value
        return None

    def get_authorization_mechanism(self, url: str) -> str | None:
        auth = self.get_authorization(url)
        if auth is None:
            return None
        for prop in auth.properties:
            if isinstance(prop, StringProp) and prop.name == AUTHORIZATION_MECHANISM:
                return prop.value
        return None

    def has_authorization(self, url: str) -> bool:
        return self.get_authorization(url) is not None
    
    def get_authorization(self, url: str) -> ElementProp | None:
        for item in self.items:
            for prop in item.properties:
                if isinstance(prop, StringProp) and prop.name == AUTHORIZATION_URL and prop.value == url:
                    return item
        return None
    
    def to_data(self) -> list[AuthorizationData]:
        result = []
        for item in self.items:
            url = ""
            username = ""
            password = ""
            domain = ""
            realm = ""
            mechanism = "BASIC"
            for prop in item.properties:
                if isinstance(prop, StringProp):
                    if prop.name == AUTHORIZATION_URL:
                        url = prop.value
                    elif prop.name == AUTHORIZATION_USERNAME:
                        username = prop.value
                    elif prop.name == AUTHORIZATION_PASSWORD:
                        password = prop.value
                    elif prop.name == AUTHORIZATION_DOMAIN:
                        domain = prop.value
                    elif prop.name == AUTHORIZATION_REALM:
                        realm = prop.value
                    elif prop.name == AUTHORIZATION_MECHANISM:
                        mechanism = prop.value
            result.append(AuthorizationData(
                url=url,
                username=username,
                password=password,
                domain=domain,
                realm=realm,
                mechanism=mechanism
            ))
        return result

    def from_data(self, data: list[AuthorizationData]) -> None:
        self.clear()
        for item in data:
            self.add_authorization(
                item.url, item.username, item.password,
                item.domain, item.realm, item.mechanism
            )
    
    def clear(self) -> None:
        self.items = []


class DNSServersProp(CollectionProp):
    def __init__(self, name: str = "DNSCacheManager.servers"):
        super().__init__(name)
    
    @staticmethod
    def _java_hash(s: str) -> int:
        h = 0
        for c in s:
            h = (31 * h + ord(c)) & 0xFFFFFFFF
        if h > 0x7FFFFFFF:
            h -= 0x100000000
        return h
    
    def add_server(self, server: str) -> None:
        hash_value = self._java_hash(server)
        prop = StringProp(str(hash_value), server)
        self.items.append(prop)
    
    def remove_server(self, server: str) -> None:
        self.items = [
            item for item in self.items
            if not (isinstance(item, StringProp) and item.value == server)
        ]
    
    def get_servers(self) -> list[str]:
        return [item.value for item in self.items if isinstance(item, StringProp)]
    
    def clear(self) -> None:
        self.items = []


class DNSHostsProp(CollectionProp):
    def __init__(self, name: str = "DNSCacheManager.hosts"):
        super().__init__(name)
    
    def add_host(self, hostname: str, address: str) -> None:
        host = ElementProp(
            name=hostname,
            element_type="StaticHost",
            properties=[
                StringProp(STATICHOST_NAME, hostname),
                StringProp(STATICHOST_ADDRESS, address)
            ]
        )
        self.items.append(host)
    
    def remove_host(self, hostname: str) -> None:
        self.items = [item for item in self.items if item.name != hostname]
    
    def get_host(self, hostname: str) -> ElementProp | None:
        for item in self.items:
            if item.name == hostname:
                return item
        return None
    
    def get_host_address(self, hostname: str) -> str | None:
        host = self.get_host(hostname)
        if host is None:
            return None
        for prop in host.properties:
            if isinstance(prop, StringProp) and prop.name == STATICHOST_ADDRESS:
                return prop.value
        return None

    def has_host(self, hostname: str, address: str | None = None) -> bool:
        if address is None:
            return self.get_host(hostname) is not None
        return self.get_host_address(hostname) == address
    
    def to_data(self) -> list[DNSHostData]:
        result = []
        for item in self.items:
            hostname = None
            address = None
            for prop in item.properties:
                if isinstance(prop, StringProp):
                    if prop.name == STATICHOST_NAME:
                        hostname = prop.value
                    elif prop.name == STATICHOST_ADDRESS:
                        address = prop.value
            if hostname is not None and address is not None:
                result.append(DNSHostData(hostname=hostname, address=address))
        return result

    def from_data(self, data: list[DNSHostData]) -> None:
        self.clear()
        for item in data:
            self.add_host(item.hostname, item.address)
    
    def clear(self) -> None:
        self.items = []


class ArgumentsProp(CollectionProp):
    def __init__(self, name: str = ARGUMENTS_ARGUMENTS):
        super().__init__(name)
    
    def add_argument(self, name: str, value: str) -> None:
        argument = ElementProp(
            name=name,
            element_type="Argument",
            properties=[
                StringProp(ARGUMENT_NAME, name),
                StringProp(ARGUMENT_VALUE, value),
                StringProp(ARGUMENT_METADATA, "=")
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
    
    def set_argument(self, name: str, value: str) -> bool:
        argument = self.get_argument(name)
        if argument is None:
            return False
        
        for prop in argument.properties:
            if isinstance(prop, StringProp) and prop.name == ARGUMENT_VALUE:
                prop.value = value
                return True
        return False
    
    def get_argument_value(self, name: str) -> str | None:
        argument = self.get_argument(name)
        if argument is None:
            return None
        for prop in argument.properties:
            if isinstance(prop, StringProp) and prop.name == ARGUMENT_VALUE:
                return prop.value
        return None

    def has_argument(self, name: str, value: str | None = None) -> bool:
        if value is None:
            return self.get_argument(name) is not None
        return self.get_argument_value(name) == value
    
    def to_data(self) -> list[ArgumentData]:
        result = []
        for item in self.items:
            name = None
            value = None
            for prop in item.properties:
                if isinstance(prop, StringProp):
                    if prop.name == ARGUMENT_NAME:
                        name = prop.value
                    elif prop.name == ARGUMENT_VALUE:
                        value = prop.value
            if name is not None and value is not None:
                result.append(ArgumentData(name=name, value=value))
        return result

    def from_data(self, data: list[ArgumentData]) -> None:
        self.clear()
        for item in data:
            self.add_argument(item.name, item.value)
    
    def clear(self) -> None:
        self.items = []




