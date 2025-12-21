from jmx_builder.parsers.elements.base import TreeElementParser
from jmx_builder.models.tree import CookieManager
from jmx_builder.parsers.const import *
import re


class CookieManagerParser(TreeElementParser):
    @staticmethod
    def parse(xml_content: str) -> CookieManager:
        testname = TreeElementParser.extract_attribute(xml_content, ATTR_TESTNAME) or "HTTP Cookie Manager"
        enabled_attr = TreeElementParser.extract_attribute(xml_content, ATTR_ENABLED)
        enabled = enabled_attr != "false"
        
        manager = CookieManager(testname=testname, enabled=enabled)
        
        comment = TreeElementParser.extract_simple_prop_value(xml_content, TESTPLAN_COMMENTS)
        if comment:
            manager.change_comment(comment)

        policy = TreeElementParser.extract_simple_prop_value(xml_content, COOKIEMANAGER_POLICY)
        if policy:
            manager.set_cookie_manager_policy(policy)
        
        clear_each = TreeElementParser.extract_simple_prop_value(xml_content, COOKIEMANAGER_CLEAR_EACH_ITERATION)
        if clear_each:
            manager.set_clear_each_iteration(clear_each.lower() == "true")
        
        controlled = TreeElementParser.extract_simple_prop_value(xml_content, COOKIEMANAGER_CONTROLLED_BY_THREADGROUP)
        if controlled:
            manager.set_controlled_by_threadgroup(controlled.lower() == "true")
        
        cookies_content = TreeElementParser.extract_collection_prop_content(xml_content, COOKIEMANAGER_COOKIES)
        if cookies_content:
            CookieManagerParser._parse_cookies(manager, cookies_content)
        
        return manager
    
    @staticmethod
    def _parse_cookies(manager: CookieManager, collection_content: str) -> None:
        element_props = re.finditer(
            r'<elementProp\s+name="([^"]*)"[^>]*>(.*?)</elementProp>',
            collection_content,
            re.DOTALL
        )
        
        for match in element_props:
            name = match.group(1)
            prop_content = match.group(2)
            
            value = TreeElementParser.extract_simple_prop_value(prop_content, COOKIE_VALUE) or ""
            domain = TreeElementParser.extract_simple_prop_value(prop_content, COOKIE_DOMAIN) or ""
            path = TreeElementParser.extract_simple_prop_value(prop_content, COOKIE_PATH) or "/"
            
            secure_str = TreeElementParser.extract_simple_prop_value(prop_content, COOKIE_SECURE)
            secure = secure_str and secure_str.lower() == "true"
            
            expires_str = TreeElementParser.extract_simple_prop_value(prop_content, COOKIE_EXPIRES)
            expires = int(expires_str) if expires_str else 0
            
            path_specified_str = TreeElementParser.extract_simple_prop_value(prop_content, COOKIE_PATH_SPECIFIED)
            path_specified = path_specified_str is None or path_specified_str.lower() == "true"

            domain_specified_str = TreeElementParser.extract_simple_prop_value(prop_content, COOKIE_DOMAIN_SPECIFIED)
            domain_specified = domain_specified_str is None or domain_specified_str.lower() == "true"
            
            manager.add_cookie(
                name=name,
                value=value,
                domain=domain,
                path=path,
                secure=secure,
                expires=expires,
                path_specified=path_specified,
                domain_specified=domain_specified
            )