from jmx_builder.parsers.elements.base import TreeElementParser
from jmx_builder.models.tree import GenericController
from jmx_builder.parsers.const import (
    ATTR_TESTNAME,
    ATTR_ENABLED,
    TESTPLAN_COMMENTS,
)


class GenericControllerParser(TreeElementParser):
    @staticmethod
    def parse(xml_content: str) -> GenericController:
        testname = TreeElementParser.extract_attribute(xml_content, ATTR_TESTNAME) or "Simple Controller"
        enabled_attr = TreeElementParser.extract_attribute(xml_content, ATTR_ENABLED)
        enabled = enabled_attr != "false"
        
        controller = GenericController(testname=testname, enabled=enabled)
        
        comment = TreeElementParser.extract_simple_prop_value(xml_content, TESTPLAN_COMMENTS)
        if comment:
            controller.change_comment(comment)
        
        return controller