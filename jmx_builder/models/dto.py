from dataclasses import dataclass, field


@dataclass
class HTTPArgumentData:
    name: str
    value: str
    always_encode: bool = False
    use_equals: bool = True


@dataclass
class HTTPFileData:
    path: str
    param_name: str = ""
    mime_type: str = "application/octet-stream"


@dataclass
class HTTPSamplerData:
    testname: str = "HTTP Request"
    enabled: bool = True
    comment: str = ""
    
    domain: str = ""
    port: str = ""
    protocol: str = ""
    path: str = ""
    method: str = "GET"
    content_encoding: str = ""
    
    follow_redirects: bool = True
    auto_redirects: bool = False
    
    use_keepalive: bool = True
    do_multipart_post: bool = False
    browser_compatible_multipart: bool = False
    
    connect_timeout: int = 0
    response_timeout: int = 0
    
    image_parser: bool = False
    concurrent_dwn: bool = False
    concurrent_pool: int = 6
    md5: bool = False
    embedded_url_re: str = ""
    embedded_url_exclude_re: str = ""
    
    ip_source: str = ""
    ip_source_type: int = 0
    implementation: str = ""
    
    proxy_scheme: str = ""
    proxy_host: str = ""
    proxy_port: str = ""
    proxy_user: str = ""
    proxy_pass: str = ""
    
    body_data: str | None = None
    arguments: list[HTTPArgumentData] = field(default_factory=list)
    files: list[HTTPFileData] = field(default_factory=list)


@dataclass
class ArgumentData:
    """Данные аргумента (для ArgumentsProp, UserDefinedVariablesProp)"""
    name: str
    value: str


@dataclass
class ArgumentWithDescData:
    """Данные аргумента с описанием (для UserDefinedVariablesWithDescProp)"""
    name: str
    value: str
    description: str = ""


@dataclass
class HTTPArgumentData:
    """Данные HTTP аргумента (для HTTPArgumentsProp)"""
    name: str
    value: str
    always_encode: bool = False
    use_equals: bool = True


@dataclass
class HTTPFileData:
    """Данные HTTP файла (для HTTPFileArgsProp)"""
    path: str
    param_name: str = ""
    mime_type: str = "application/octet-stream"


@dataclass
class HeaderData:
    """Данные заголовка (для HeadersProp)"""
    name: str
    value: str


@dataclass
class CookieData:
    """Данные cookie (для CookiesProp)"""
    name: str
    value: str
    domain: str
    path: str = "/"
    secure: bool = False
    expires: int = 0
    path_specified: bool = True
    domain_specified: bool = True


@dataclass
class AuthorizationData:
    """Данные авторизации (для AuthorizationsProp)"""
    url: str
    username: str
    password: str
    domain: str = ""
    realm: str = ""
    mechanism: str = "BASIC"


@dataclass
class DNSHostData:
    """Данные DNS хоста (для DNSHostsProp)"""
    hostname: str
    address: str