from jmx_builder.parsers.elements.base import TreeElementParser
from jmx_builder.models.tree import SimpleConfigElement
from jmx_builder.parsers.const import *
import re


class SimpleConfigElementParser(TreeElementParser):
    @staticmethod
    def parse(xml_content: str) -> SimpleConfigElement:
        testname = TreeElementParser.extract_attribute(xml_content, ATTR_TESTNAME) or "Simple Config Element"
        enabled_attr = TreeElementParser.extract_attribute(xml_content, ATTR_ENABLED)
        enabled = enabled_attr != "false"
        
        element = SimpleConfigElement(testname=testname, enabled=enabled)
        
        comment = TreeElementParser.extract_simple_prop_value(xml_content, TESTPLAN_COMMENTS)
        if comment:
            element.change_comment(comment)
        
        props = re.finditer(
            r'<stringProp\s+name="([^"]+)"[^>]*>([^<]*)</stringProp>',
            xml_content
        )
        
        for match in props:
            name = match.group(1)
            value = match.group(2)
            if name != TESTPLAN_COMMENTS:
                element.add_property(name, value)
        
        return element