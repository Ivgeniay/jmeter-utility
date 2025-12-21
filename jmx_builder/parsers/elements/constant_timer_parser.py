from jmx_builder.parsers.elements.base import TreeElementParser
from jmx_builder.models.tree import ConstantTimer
from jmx_builder.parsers.const import (
    ATTR_TESTNAME,
    ATTR_ENABLED,
    TESTPLAN_COMMENTS,
    CONSTANTTIMER_DELAY,
)


class ConstantTimerParser(TreeElementParser):
    @staticmethod
    def parse(xml_content: str) -> ConstantTimer:
        testname = TreeElementParser.extract_attribute(xml_content, ATTR_TESTNAME) or "Constant Timer"
        enabled_attr = TreeElementParser.extract_attribute(xml_content, ATTR_ENABLED)
        enabled = enabled_attr != "false"
        
        timer = ConstantTimer(testname=testname, enabled=enabled)
        
        comment = TreeElementParser.extract_simple_prop_value(xml_content, TESTPLAN_COMMENTS)
        if comment:
            timer.change_comment(comment)
        
        delay = TreeElementParser.extract_simple_prop_value(xml_content, CONSTANTTIMER_DELAY)
        if delay:
            timer.set_delay_raw(delay)
        
        return timer