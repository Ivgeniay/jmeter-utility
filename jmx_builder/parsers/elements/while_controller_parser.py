from jmx_builder.parsers.elements.base import TreeElementParser
from jmx_builder.models.tree import WhileController
from jmx_builder.parsers.const import (
    ATTR_TESTNAME,
    ATTR_ENABLED,
    TESTPLAN_COMMENTS,
    WHILECONTROLLER_CONDITION,
)


class WhileControllerParser(TreeElementParser):
    @staticmethod
    def parse(xml_content: str) -> WhileController:
        testname = TreeElementParser.extract_attribute(xml_content, ATTR_TESTNAME) or "While Controller"
        enabled_attr = TreeElementParser.extract_attribute(xml_content, ATTR_ENABLED)
        enabled = enabled_attr != "false"
        
        controller = WhileController(testname=testname, enabled=enabled)
        
        comment = TreeElementParser.extract_simple_prop_value(xml_content, TESTPLAN_COMMENTS)
        if comment:
            controller.change_comment(comment)
        
        condition = TreeElementParser.extract_simple_prop_value(xml_content, WHILECONTROLLER_CONDITION)
        if condition:
            controller.set_condition(condition)
        
        return controller