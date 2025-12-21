from jmx_builder.parsers.elements.base import TreeElementParser
from jmx_builder.models.tree import LoginConfigElement
from jmx_builder.parsers.const import *


class LoginConfigElementParser(TreeElementParser):
    @staticmethod
    def parse(xml_content: str) -> LoginConfigElement:
        testname = TreeElementParser.extract_attribute(xml_content, ATTR_TESTNAME) or "Login Config Element"
        enabled_attr = TreeElementParser.extract_attribute(xml_content, ATTR_ENABLED)
        enabled = enabled_attr != "false"
        
        element = LoginConfigElement(testname=testname, enabled=enabled)
        
        comment = TreeElementParser.extract_simple_prop_value(xml_content, TESTPLAN_COMMENTS)
        if comment:
            element.change_comment(comment)
        
        username = TreeElementParser.extract_simple_prop_value(xml_content, LOGINCONFIG_USERNAME)
        if username:
            element.set_username(username)
        
        password = TreeElementParser.extract_simple_prop_value(xml_content, LOGINCONFIG_PASSWORD)
        if password:
            element.set_password(password)
        
        return element