from jmx_builder.parsers.elements.base import TreeElementParser
from jmx_builder.models.tree import TestAction
from jmx_builder.parsers.const import (
    ATTR_TESTNAME,
    ATTR_ENABLED,
    TESTPLAN_COMMENTS,
    TESTACTION_ACTION,
    TESTACTION_TARGET,
    TESTACTION_DURATION,
)


class TestActionParser(TreeElementParser):
    @staticmethod
    def parse(xml_content: str) -> TestAction:
        testname = TreeElementParser.extract_attribute(xml_content, ATTR_TESTNAME) or "Think Time"
        enabled_attr = TreeElementParser.extract_attribute(xml_content, ATTR_ENABLED)
        enabled = enabled_attr != "false"
        
        test_action = TestAction(testname=testname, enabled=enabled)
        
        comment = TreeElementParser.extract_simple_prop_value(xml_content, TESTPLAN_COMMENTS)
        if comment:
            test_action.change_comment(comment)
        
        action = TreeElementParser.extract_simple_prop_value(xml_content, TESTACTION_ACTION)
        if action:
            test_action.set_action_raw(int(action))
        
        target = TreeElementParser.extract_simple_prop_value(xml_content, TESTACTION_TARGET)
        if target:
            test_action.set_target_raw(int(target))
        
        duration = TreeElementParser.extract_simple_prop_value(xml_content, TESTACTION_DURATION)
        if duration:
            test_action.set_duration_raw(duration)
        
        return test_action