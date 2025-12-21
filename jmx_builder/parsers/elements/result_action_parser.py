from jmx_builder.parsers.elements.base import TreeElementParser
from jmx_builder.models.tree import ResultAction
from jmx_builder.parsers.const import *


class ResultActionParser(TreeElementParser):
    @staticmethod
    def parse(xml_content: str) -> ResultAction:
        testname = TreeElementParser.extract_attribute(xml_content, ATTR_TESTNAME) or "Result Status Action Handler"
        enabled_attr = TreeElementParser.extract_attribute(xml_content, ATTR_ENABLED)
        enabled = enabled_attr != "false"
        
        action = ResultAction(testname=testname, enabled=enabled)
        
        comment = TreeElementParser.extract_simple_prop_value(xml_content, TESTPLAN_COMMENTS)
        if comment:
            action.change_comment(comment)
        
        on_error = TreeElementParser.extract_simple_prop_value(xml_content, RESULTACTION_ON_ERROR_ACTION)
        if on_error:
            action.set_on_error_action_raw(int(on_error))
        
        return action