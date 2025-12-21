from jmx_builder.parsers.elements.base import TreeElementParser
from jmx_builder.models.tree import AuthManager
from jmx_builder.parsers.const import *
import re


class AuthManagerParser(TreeElementParser):
    @staticmethod
    def parse(xml_content: str) -> AuthManager:
        testname = TreeElementParser.extract_attribute(xml_content, ATTR_TESTNAME) or "HTTP Authorization Manager"
        enabled_attr = TreeElementParser.extract_attribute(xml_content, ATTR_ENABLED)
        enabled = enabled_attr != "false"
        
        manager = AuthManager(testname=testname, enabled=enabled)
        
        comment = TreeElementParser.extract_simple_prop_value(xml_content, TESTPLAN_COMMENTS)
        if comment:
            manager.change_comment(comment)
        
        controlled = TreeElementParser.extract_simple_prop_value(xml_content, AUTHMANAGER_CONTROLLED_BY_THREADGROUP)
        if controlled:
            manager.set_controlled_by_threadgroup(controlled.lower() == "true")
        
        clear_each = TreeElementParser.extract_simple_prop_value(xml_content, AUTHMANAGER_CLEAR_EACH_ITERATION)
        if clear_each:
            manager.set_clear_each_iteration(clear_each.lower() == "true")
        
        auth_list_content = TreeElementParser.extract_collection_prop_content(xml_content, AUTHMANAGER_AUTH_LIST)
        if auth_list_content:
            AuthManagerParser._parse_authorizations(manager, auth_list_content)
        
        return manager
    
    @staticmethod
    def _parse_authorizations(manager: AuthManager, collection_content: str) -> None:
        element_props = re.finditer(
            r'<elementProp\s+name="[^"]*"[^>]*elementType="Authorization"[^>]*>(.*?)</elementProp>',
            collection_content,
            re.DOTALL
        )
        
        for match in element_props:
            prop_content = match.group(1)
            
            url = TreeElementParser.extract_simple_prop_value(prop_content, AUTHORIZATION_URL) or ""
            username = TreeElementParser.extract_simple_prop_value(prop_content, AUTHORIZATION_USERNAME) or ""
            password = TreeElementParser.extract_simple_prop_value(prop_content, AUTHORIZATION_PASSWORD) or ""
            domain = TreeElementParser.extract_simple_prop_value(prop_content, AUTHORIZATION_DOMAIN) or ""
            realm = TreeElementParser.extract_simple_prop_value(prop_content, AUTHORIZATION_REALM) or ""
            mechanism = TreeElementParser.extract_simple_prop_value(prop_content, AUTHORIZATION_MECHANISM) or "BASIC"
            
            manager.add_authorization(url, username, password, domain, realm, mechanism)