from jmx_builder.parsers.elements.base import TreeElementParser
from jmx_builder.models.tree import HTTPSamplerProxy, IpSourceType, RedirectType
from jmx_builder.parsers.const import (
    ATTR_TESTNAME,
    ATTR_ENABLED,
    TESTPLAN_COMMENTS,
    ARGUMENT_NAME,
    ARGUMENT_VALUE,
    ARGUMENTS_ARGUMENTS,
    HTTPSAMPLER_DOMAIN,
    HTTPSAMPLER_PORT,
    HTTPSAMPLER_PROTOCOL,
    HTTPSAMPLER_PATH,
    HTTPSAMPLER_METHOD,
    HTTPSAMPLER_CONTENT_ENCODING,
    HTTPSAMPLER_FOLLOW_REDIRECTS,
    HTTPSAMPLER_AUTO_REDIRECTS,
    HTTPSAMPLER_USE_KEEPALIVE,
    HTTPSAMPLER_DO_MULTIPART_POST,
    HTTPSAMPLER_BROWSER_COMPATIBLE_MULTIPART,
    HTTPSAMPLER_POST_BODY_RAW,
    HTTPSAMPLER_ARGUMENTS,
    HTTPSAMPLER_FILES,
    HTTPSAMPLER_CONNECT_TIMEOUT,
    HTTPSAMPLER_RESPONSE_TIMEOUT,
    HTTPSAMPLER_IMAGE_PARSER,
    HTTPSAMPLER_CONCURRENT_DWN,
    HTTPSAMPLER_CONCURRENT_POOL,
    HTTPSAMPLER_EMBEDDED_URL_RE,
    HTTPSAMPLER_EMBEDDED_URL_EXCLUDE_RE,
    HTTPSAMPLER_IP_SOURCE,
    HTTPSAMPLER_IP_SOURCE_TYPE,
    HTTPSAMPLER_PROXY_SCHEME,
    HTTPSAMPLER_PROXY_HOST,
    HTTPSAMPLER_PROXY_PORT,
    HTTPSAMPLER_PROXY_USER,
    HTTPSAMPLER_PROXY_PASS,
    HTTPSAMPLER_IMPLEMENTATION,
    HTTPSAMPLER_MD5,
    HTTPARGUMENT_ALWAYS_ENCODE,
    HTTPARGUMENT_USE_EQUALS,
    HTTPFILEARG_PATH,
    HTTPFILEARG_PARAMNAME,
    HTTPFILEARG_MIMETYPE,
    HTTPFILEARGS_FILES,
)
import re


class HTTPSamplerProxyParser(TreeElementParser):
    @staticmethod
    def parse(xml_content: str) -> HTTPSamplerProxy:
        testname = TreeElementParser.extract_attribute(xml_content, ATTR_TESTNAME) or "HTTP Request"
        enabled_attr = TreeElementParser.extract_attribute(xml_content, ATTR_ENABLED)
        enabled = enabled_attr != "false"
        
        sampler = HTTPSamplerProxy(testname=testname, enabled=enabled)
        
        comment = TreeElementParser.extract_simple_prop_value(xml_content, TESTPLAN_COMMENTS)
        if comment:
            sampler.change_comment(comment)
        
        # === Basic Request ===
        
        domain = TreeElementParser.extract_simple_prop_value(xml_content, HTTPSAMPLER_DOMAIN)
        if domain:
            sampler.set_domain(domain)
        
        port = TreeElementParser.extract_simple_prop_value(xml_content, HTTPSAMPLER_PORT)
        if port:
            sampler.set_port(port)
        
        protocol = TreeElementParser.extract_simple_prop_value(xml_content, HTTPSAMPLER_PROTOCOL)
        if protocol:
            sampler.set_protocol(protocol)
        
        path = TreeElementParser.extract_simple_prop_value(xml_content, HTTPSAMPLER_PATH)
        if path:
            sampler.set_path(path)
        
        method = TreeElementParser.extract_simple_prop_value(xml_content, HTTPSAMPLER_METHOD)
        if method:
            sampler.set_method_raw(method)
        
        content_encoding = TreeElementParser.extract_simple_prop_value(xml_content, HTTPSAMPLER_CONTENT_ENCODING)
        if content_encoding:
            sampler.set_content_encoding(content_encoding)
        
        # === Redirects ===
        
        auto_redirects = TreeElementParser.extract_simple_prop_value(xml_content, HTTPSAMPLER_AUTO_REDIRECTS)
        follow_redirects = TreeElementParser.extract_simple_prop_value(xml_content, HTTPSAMPLER_FOLLOW_REDIRECTS)
        
        if auto_redirects and auto_redirects.lower() == "true":
            sampler.set_redirect_type(RedirectType.AUTO_REDIRECTS)
        elif follow_redirects and follow_redirects.lower() == "true":
            sampler.set_redirect_type(RedirectType.FOLLOW_REDIRECTS)
        elif follow_redirects and follow_redirects.lower() == "false":
            sampler.set_redirect_type(RedirectType.NONE)
        
        # === KeepAlive ===
        
        use_keepalive = TreeElementParser.extract_simple_prop_value(xml_content, HTTPSAMPLER_USE_KEEPALIVE)
        if use_keepalive:
            sampler.set_use_keepalive(use_keepalive.lower() == "true")
        
        # === Multipart ===
        
        do_multipart = TreeElementParser.extract_simple_prop_value(xml_content, HTTPSAMPLER_DO_MULTIPART_POST)
        browser_compatible = TreeElementParser.extract_simple_prop_value(xml_content, HTTPSAMPLER_BROWSER_COMPATIBLE_MULTIPART)
        
        if do_multipart and do_multipart.lower() == "true":
            bc = browser_compatible and browser_compatible.lower() == "true"
            sampler.set_multipart(True, bc)
        
        # === Timeouts ===
        
        connect_timeout = TreeElementParser.extract_simple_prop_value(xml_content, HTTPSAMPLER_CONNECT_TIMEOUT)
        if connect_timeout:
            sampler.set_connect_timeout(int(connect_timeout))
        
        response_timeout = TreeElementParser.extract_simple_prop_value(xml_content, HTTPSAMPLER_RESPONSE_TIMEOUT)
        if response_timeout:
            sampler.set_response_timeout(int(response_timeout))
        
        # === Embedded Resources ===
        
        image_parser = TreeElementParser.extract_simple_prop_value(xml_content, HTTPSAMPLER_IMAGE_PARSER)
        if image_parser and image_parser.lower() == "true":
            sampler.set_retrieve_embedded_resources(True)
        
        concurrent_dwn = TreeElementParser.extract_simple_prop_value(xml_content, HTTPSAMPLER_CONCURRENT_DWN)
        concurrent_pool = TreeElementParser.extract_simple_prop_value(xml_content, HTTPSAMPLER_CONCURRENT_POOL)
        
        if concurrent_dwn and concurrent_dwn.lower() == "true":
            pool_size = int(concurrent_pool) if concurrent_pool else 6
            sampler.set_concurrent_download(True, pool_size)
        
        embedded_url_re = TreeElementParser.extract_simple_prop_value(xml_content, HTTPSAMPLER_EMBEDDED_URL_RE)
        if embedded_url_re:
            sampler.set_embedded_url_match(embedded_url_re)
        
        embedded_url_exclude_re = TreeElementParser.extract_simple_prop_value(xml_content, HTTPSAMPLER_EMBEDDED_URL_EXCLUDE_RE)
        if embedded_url_exclude_re:
            sampler.set_embedded_url_exclude(embedded_url_exclude_re)
        
        # === IP Source ===
        
        ip_source = TreeElementParser.extract_simple_prop_value(xml_content, HTTPSAMPLER_IP_SOURCE)
        if ip_source:
            sampler.set_ip_source(ip_source)
        
        ip_source_type = TreeElementParser.extract_simple_prop_value(xml_content, HTTPSAMPLER_IP_SOURCE_TYPE)
        if ip_source_type:
            sampler.set_ip_source_type_raw(int(ip_source_type))
        
        # === Proxy ===
        
        proxy_host = TreeElementParser.extract_simple_prop_value(xml_content, HTTPSAMPLER_PROXY_HOST)
        if proxy_host:
            sampler.set_proxy_host(proxy_host)
        
        proxy_port = TreeElementParser.extract_simple_prop_value(xml_content, HTTPSAMPLER_PROXY_PORT)
        if proxy_port:
            sampler.set_proxy_port(int(proxy_port))
        
        proxy_scheme = TreeElementParser.extract_simple_prop_value(xml_content, HTTPSAMPLER_PROXY_SCHEME)
        if proxy_scheme:
            sampler.set_proxy_scheme(proxy_scheme)
        
        proxy_user = TreeElementParser.extract_simple_prop_value(xml_content, HTTPSAMPLER_PROXY_USER)
        if proxy_user:
            sampler.set_proxy_user(proxy_user)
        
        proxy_pass = TreeElementParser.extract_simple_prop_value(xml_content, HTTPSAMPLER_PROXY_PASS)
        if proxy_pass:
            sampler.set_proxy_pass(proxy_pass)
        
        # === Implementation ===
        
        implementation = TreeElementParser.extract_simple_prop_value(xml_content, HTTPSAMPLER_IMPLEMENTATION)
        if implementation:
            sampler.set_implementation_raw(implementation)
        
        # === MD5 ===
        
        md5 = TreeElementParser.extract_simple_prop_value(xml_content, HTTPSAMPLER_MD5)
        if md5 and md5.lower() == "true":
            sampler.set_md5(True)
        
        # === Body Data / Arguments ===
        
        post_body_raw = TreeElementParser.extract_simple_prop_value(xml_content, HTTPSAMPLER_POST_BODY_RAW)
        is_body_raw = post_body_raw and post_body_raw.lower() == "true"
        
        arguments_content = TreeElementParser.extract_element_prop_content(xml_content, HTTPSAMPLER_ARGUMENTS)
        if arguments_content:
            collection_content = TreeElementParser.extract_collection_prop_content(arguments_content, ARGUMENTS_ARGUMENTS)
            if collection_content:
                if is_body_raw:
                    HTTPSamplerProxyParser._parse_body_data(sampler, collection_content)
                else:
                    HTTPSamplerProxyParser._parse_arguments(sampler, collection_content)
        
        # === Files ===
        
        files_content = TreeElementParser.extract_element_prop_content(xml_content, HTTPSAMPLER_FILES)
        if files_content:
            files_collection = TreeElementParser.extract_collection_prop_content(files_content, HTTPFILEARGS_FILES)
            if files_collection:
                HTTPSamplerProxyParser._parse_files(sampler, files_collection)
        
        return sampler
    
    @staticmethod
    def _parse_arguments(sampler: HTTPSamplerProxy, collection_content: str) -> None:
        element_props = re.findall(
            r'<elementProp\s+name="[^"]*"[^>]*>(.*?)</elementProp>',
            collection_content,
            re.DOTALL
        )
        
        for prop_content in element_props:
            name = TreeElementParser.extract_simple_prop_value(prop_content, ARGUMENT_NAME)
            value = TreeElementParser.extract_simple_prop_value(prop_content, ARGUMENT_VALUE)
            
            always_encode_str = TreeElementParser.extract_simple_prop_value(prop_content, HTTPARGUMENT_ALWAYS_ENCODE)
            always_encode = always_encode_str and always_encode_str.lower() == "true"
            
            use_equals_str = TreeElementParser.extract_simple_prop_value(prop_content, HTTPARGUMENT_USE_EQUALS)
            use_equals = use_equals_str is None or use_equals_str.lower() == "true"
            
            if name is not None and value is not None:
                sampler.add_argument(name, value, always_encode, use_equals)
    
    @staticmethod
    def _parse_body_data(sampler: HTTPSamplerProxy, collection_content: str) -> None:
        element_props = re.findall(
            r'<elementProp\s+name="[^"]*"[^>]*>(.*?)</elementProp>',
            collection_content,
            re.DOTALL
        )
        
        if element_props:
            value = TreeElementParser.extract_simple_prop_value(element_props[0], ARGUMENT_VALUE)
            if value is not None:
                sampler.set_body_data(value)
    
    @staticmethod
    def _parse_files(sampler: HTTPSamplerProxy, collection_content: str) -> None:
        element_props = re.findall(
            r'<elementProp\s+name="[^"]*"[^>]*>(.*?)</elementProp>',
            collection_content,
            re.DOTALL
        )
        
        for prop_content in element_props:
            path = TreeElementParser.extract_simple_prop_value(prop_content, HTTPFILEARG_PATH)
            param_name = TreeElementParser.extract_simple_prop_value(prop_content, HTTPFILEARG_PARAMNAME) or ""
            mime_type = TreeElementParser.extract_simple_prop_value(prop_content, HTTPFILEARG_MIMETYPE) or "application/octet-stream"
            
            if path:
                sampler.add_file(path, param_name, mime_type)