from jmx_builder.parsers.elements.base import TreeElementParser
from jmx_builder.models.tree import HttpRequestDefaults
from jmx_builder.parsers.const import *
import re


class HttpRequestDefaultsParser(TreeElementParser):
    @staticmethod
    def parse(xml_content: str) -> HttpRequestDefaults:
        testname = TreeElementParser.extract_attribute(xml_content, ATTR_TESTNAME) or "HTTP Request Defaults"
        enabled_attr = TreeElementParser.extract_attribute(xml_content, ATTR_ENABLED)
        enabled = enabled_attr != "false"
        
        element = HttpRequestDefaults(testname=testname, enabled=enabled)
        
        comment = TreeElementParser.extract_simple_prop_value(xml_content, TESTPLAN_COMMENTS)
        if comment:
            element.change_comment(comment)
        
        domain = TreeElementParser.extract_simple_prop_value(xml_content, HTTPSAMPLER_DOMAIN)
        if domain:
            element.set_domain(domain)
        
        port = TreeElementParser.extract_simple_prop_value(xml_content, HTTPSAMPLER_PORT)
        if port:
            element.set_port(port)
        
        protocol = TreeElementParser.extract_simple_prop_value(xml_content, HTTPSAMPLER_PROTOCOL)
        if protocol:
            element.set_protocol(protocol)
        
        path = TreeElementParser.extract_simple_prop_value(xml_content, HTTPSAMPLER_PATH)
        if path:
            element.set_path(path)
        
        content_encoding = TreeElementParser.extract_simple_prop_value(xml_content, HTTPSAMPLER_CONTENT_ENCODING)
        if content_encoding:
            element.set_content_encoding(content_encoding)
        
        connect_timeout = TreeElementParser.extract_simple_prop_value(xml_content, HTTPSAMPLER_CONNECT_TIMEOUT)
        if connect_timeout:
            element.set_connect_timeout(int(connect_timeout))
        
        response_timeout = TreeElementParser.extract_simple_prop_value(xml_content, HTTPSAMPLER_RESPONSE_TIMEOUT)
        if response_timeout:
            element.set_response_timeout(int(response_timeout))
        
        image_parser = TreeElementParser.extract_simple_prop_value(xml_content, HTTPSAMPLER_IMAGE_PARSER)
        if image_parser:
            element.set_image_parser(image_parser.lower() == "true")
        
        concurrent_dwn = TreeElementParser.extract_simple_prop_value(xml_content, HTTPSAMPLER_CONCURRENT_DWN)
        if concurrent_dwn:
            element.set_concurrent_dwn(concurrent_dwn.lower() == "true")
        
        concurrent_pool = TreeElementParser.extract_simple_prop_value(xml_content, HTTPSAMPLER_CONCURRENT_POOL)
        if concurrent_pool:
            element.set_concurrent_pool(int(concurrent_pool))
        
        md5 = TreeElementParser.extract_simple_prop_value(xml_content, HTTPSAMPLER_MD5)
        if md5:
            element.set_md5(md5.lower() == "true")
        
        embedded_url_re = TreeElementParser.extract_simple_prop_value(xml_content, HTTPSAMPLER_EMBEDDED_URL_RE)
        if embedded_url_re:
            element.set_embedded_url_re(embedded_url_re)
        
        embedded_url_exclude_re = TreeElementParser.extract_simple_prop_value(xml_content, HTTPSAMPLER_EMBEDDED_URL_EXCLUDE_RE)
        if embedded_url_exclude_re:
            element.set_embedded_url_exclude_re(embedded_url_exclude_re)
        
        ip_source = TreeElementParser.extract_simple_prop_value(xml_content, HTTPSAMPLER_IP_SOURCE)
        if ip_source:
            element.set_ip_source(ip_source)
        
        ip_source_type = TreeElementParser.extract_simple_prop_value(xml_content, HTTPSAMPLER_IP_SOURCE_TYPE)
        if ip_source_type:
            element.set_ip_source_type(int(ip_source_type))
        
        implementation = TreeElementParser.extract_simple_prop_value(xml_content, HTTPSAMPLER_IMPLEMENTATION)
        if implementation:
            element.set_implementation(implementation)
        
        proxy_scheme = TreeElementParser.extract_simple_prop_value(xml_content, HTTPSAMPLER_PROXY_SCHEME)
        if proxy_scheme:
            element.set_proxy_scheme(proxy_scheme)
        
        proxy_host = TreeElementParser.extract_simple_prop_value(xml_content, HTTPSAMPLER_PROXY_HOST)
        if proxy_host:
            element.set_proxy_host(proxy_host)
        
        proxy_port = TreeElementParser.extract_simple_prop_value(xml_content, HTTPSAMPLER_PROXY_PORT)
        if proxy_port:
            element.set_proxy_port(proxy_port)
        
        proxy_user = TreeElementParser.extract_simple_prop_value(xml_content, HTTPSAMPLER_PROXY_USER)
        if proxy_user:
            element.set_proxy_user(proxy_user)
        
        proxy_pass = TreeElementParser.extract_simple_prop_value(xml_content, HTTPSAMPLER_PROXY_PASS)
        if proxy_pass:
            element.set_proxy_pass(proxy_pass)
        
        post_body_raw = TreeElementParser.extract_simple_prop_value(xml_content, HTTPSAMPLER_POST_BODY_RAW)
        is_raw_body = post_body_raw and post_body_raw.lower() == "true"
        
        arguments_content = TreeElementParser.extract_element_prop_content(xml_content, HTTPSAMPLER_ARGUMENTS)
        if arguments_content:
            if is_raw_body:
                HttpRequestDefaultsParser._parse_body(element, arguments_content)
            else:
                HttpRequestDefaultsParser._parse_arguments(element, arguments_content)
        
        return element
    
    @staticmethod
    def _parse_body(element: HttpRequestDefaults, arguments_content: str) -> None:
        body_value = TreeElementParser.extract_simple_prop_value(arguments_content, ARGUMENT_VALUE)
        if body_value:
            element.set_body_data(body_value)
    
    @staticmethod
    def _parse_arguments(element: HttpRequestDefaults, arguments_content: str) -> None:
        element_props = re.finditer(
            r'<elementProp\s+name="([^"]*)"[^>]*elementType="HTTPArgument"[^>]*>(.*?)</elementProp>',
            arguments_content,
            re.DOTALL
        )
        
        for match in element_props:
            prop_content = match.group(2)
            
            name = TreeElementParser.extract_simple_prop_value(prop_content, ARGUMENT_NAME) or ""
            value = TreeElementParser.extract_simple_prop_value(prop_content, ARGUMENT_VALUE) or ""
            
            always_encode_str = TreeElementParser.extract_simple_prop_value(prop_content, HTTPARGUMENT_ALWAYS_ENCODE)
            always_encode = always_encode_str and always_encode_str.lower() == "true"
            
            use_equals_str = TreeElementParser.extract_simple_prop_value(prop_content, HTTPARGUMENT_USE_EQUALS)
            use_equals = use_equals_str is None or use_equals_str.lower() == "true"
            
            element.add_argument(name, value, always_encode, use_equals)