from jmx_builder.parsers.elements.base import TreeElementParser
from jmx_builder.models.tree import HeaderManager
from jmx_builder.parsers.const import (
    ATTR_TESTNAME,
    ATTR_ENABLED,
    TESTPLAN_COMMENTS,
    HEADERMANAGER_HEADERS,
    HEADER_NAME,
    HEADER_VALUE,
)
import re


class HeaderManagerParser(TreeElementParser):
    @staticmethod
    def parse(xml_content: str) -> HeaderManager:
        testname = TreeElementParser.extract_attribute(xml_content, ATTR_TESTNAME) or "HTTP Header Manager"
        enabled_attr = TreeElementParser.extract_attribute(xml_content, ATTR_ENABLED)
        enabled = enabled_attr != "false"
        
        manager = HeaderManager(testname=testname, enabled=enabled)
        
        comment = TreeElementParser.extract_simple_prop_value(xml_content, TESTPLAN_COMMENTS)
        if comment:
            manager.change_comment(comment)
        
        collection_content = TreeElementParser.extract_collection_prop_content(xml_content, HEADERMANAGER_HEADERS)
        if collection_content:
            HeaderManagerParser._parse_headers(manager, collection_content)
        
        return manager
    
    @staticmethod
    def _parse_headers(manager: HeaderManager, collection_content: str) -> None:
        element_props = re.findall(
            r'<elementProp\s+name="[^"]*"[^>]*>(.*?)</elementProp>',
            collection_content,
            re.DOTALL
        )
        
        for prop_content in element_props:
            name = TreeElementParser.extract_simple_prop_value(prop_content, HEADER_NAME)
            value = TreeElementParser.extract_simple_prop_value(prop_content, HEADER_VALUE)
            
            if name is not None and value is not None:
                manager.add_header(name, value)