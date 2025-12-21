from jmx_builder.parsers.elements.base import TreeElementParser
from jmx_builder.models.tree import SwitchController
from jmx_builder.parsers.const import (
    ATTR_TESTNAME,
    ATTR_ENABLED,
    TESTPLAN_COMMENTS,
    SWITCHCONTROLLER_VALUE,
)


class SwitchControllerParser(TreeElementParser):
    @staticmethod
    def parse(xml_content: str) -> SwitchController:
        testname = TreeElementParser.extract_attribute(xml_content, ATTR_TESTNAME) or "Switch Controller"
        enabled_attr = TreeElementParser.extract_attribute(xml_content, ATTR_ENABLED)
        enabled = enabled_attr != "false"
        
        controller = SwitchController(testname=testname, enabled=enabled)
        
        comment = TreeElementParser.extract_simple_prop_value(xml_content, TESTPLAN_COMMENTS)
        if comment:
            controller.change_comment(comment)
        
        switch_value = TreeElementParser.extract_simple_prop_value(xml_content, SWITCHCONTROLLER_VALUE)
        if switch_value:
            controller.set_switch_value(switch_value)
        
        return controller