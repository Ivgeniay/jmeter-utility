from jmx_builder.parsers.elements.base import TreeElementParser
from jmx_builder.models.tree import BoltConnectionElement
from jmx_builder.parsers.const import (
    ATTR_TESTNAME,
    ATTR_ENABLED,
    TESTPLAN_COMMENTS,
    BOLTCONNECTION_URI,
    BOLTCONNECTION_MAX_POOL_SIZE,
    BOLTCONNECTION_PASSWORD,
    BOLTCONNECTION_USERNAME,
)


class BoltConnectionElementParser(TreeElementParser):
    @staticmethod
    def parse(xml_content: str) -> BoltConnectionElement:
        testname = TreeElementParser.extract_attribute(xml_content, ATTR_TESTNAME) or "Bolt Connection Configuration"
        enabled_attr = TreeElementParser.extract_attribute(xml_content, ATTR_ENABLED)
        enabled = enabled_attr != "false"
        
        element = BoltConnectionElement(testname=testname, enabled=enabled)
        
        comment = TreeElementParser.extract_simple_prop_value(xml_content, TESTPLAN_COMMENTS)
        if comment:
            element.change_comment(comment)
        
        bolt_uri = TreeElementParser.extract_simple_prop_value(xml_content, BOLTCONNECTION_URI)
        if bolt_uri:
            element.set_bolt_uri(bolt_uri)
        
        max_pool_size = TreeElementParser.extract_simple_prop_value(xml_content, BOLTCONNECTION_MAX_POOL_SIZE)
        if max_pool_size:
            element.set_max_connection_pool_size(int(max_pool_size))
        
        password = TreeElementParser.extract_simple_prop_value(xml_content, BOLTCONNECTION_PASSWORD)
        if password:
            element.set_password(password)
        
        username = TreeElementParser.extract_simple_prop_value(xml_content, BOLTCONNECTION_USERNAME)
        if username:
            element.set_username(username)
        
        return element