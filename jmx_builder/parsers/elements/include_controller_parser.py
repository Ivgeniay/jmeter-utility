from jmx_builder.parsers.elements.base import TreeElementParser
from jmx_builder.models.tree import IncludeController
from jmx_builder.parsers.const import (
    ATTR_TESTNAME,
    ATTR_ENABLED,
    TESTPLAN_COMMENTS,
    INCLUDECONTROLLER_INCLUDE_PATH,
)


class IncludeControllerParser(TreeElementParser):
    @staticmethod
    def parse(xml_content: str) -> IncludeController:
        testname = TreeElementParser.extract_attribute(xml_content, ATTR_TESTNAME) or "Include Controller"
        enabled_attr = TreeElementParser.extract_attribute(xml_content, ATTR_ENABLED)
        enabled = enabled_attr != "false"
        
        controller = IncludeController(testname=testname, enabled=enabled)
        
        comment = TreeElementParser.extract_simple_prop_value(xml_content, TESTPLAN_COMMENTS)
        if comment:
            controller.change_comment(comment)
        
        include_path = TreeElementParser.extract_simple_prop_value(xml_content, INCLUDECONTROLLER_INCLUDE_PATH)
        if include_path:
            controller.set_include_path(include_path)
        
        return controller