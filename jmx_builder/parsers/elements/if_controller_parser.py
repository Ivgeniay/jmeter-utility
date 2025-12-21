from jmx_builder.parsers.elements.base import TreeElementParser
from jmx_builder.models.tree import IfController
from jmx_builder.parsers.const import (
    ATTR_TESTNAME,
    ATTR_ENABLED,
    TESTPLAN_COMMENTS,
    IFCONTROLLER_CONDITION,
    IFCONTROLLER_EVALUATE_ALL,
    IFCONTROLLER_USE_EXPRESSION,
)


class IfControllerParser(TreeElementParser):
    @staticmethod
    def parse(xml_content: str) -> IfController:
        testname = TreeElementParser.extract_attribute(xml_content, ATTR_TESTNAME) or "If Controller"
        enabled_attr = TreeElementParser.extract_attribute(xml_content, ATTR_ENABLED)
        enabled = enabled_attr != "false"
        
        controller = IfController(testname=testname, enabled=enabled)
        
        comment = TreeElementParser.extract_simple_prop_value(xml_content, TESTPLAN_COMMENTS)
        if comment:
            controller.change_comment(comment)
        
        condition = TreeElementParser.extract_simple_prop_value(xml_content, IFCONTROLLER_CONDITION)
        if condition:
            controller.set_condition(condition)
        
        evaluate_all = TreeElementParser.extract_simple_prop_value(xml_content, IFCONTROLLER_EVALUATE_ALL)
        if evaluate_all:
            controller.set_evaluate_all(evaluate_all.lower() == "true")
        
        use_expression = TreeElementParser.extract_simple_prop_value(xml_content, IFCONTROLLER_USE_EXPRESSION)
        if use_expression:
            controller.set_use_expression(use_expression.lower() == "true")
        
        return controller