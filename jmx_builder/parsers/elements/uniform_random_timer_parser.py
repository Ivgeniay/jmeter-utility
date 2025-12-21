from jmx_builder.parsers.elements.base import TreeElementParser
from jmx_builder.models.tree import UniformRandomTimer
from jmx_builder.parsers.const import (
    ATTR_TESTNAME,
    ATTR_ENABLED,
    TESTPLAN_COMMENTS,
    UNIFORMRANDOMTIMER_DELAY,
    UNIFORMRANDOMTIMER_RANGE,
)


class UniformRandomTimerParser(TreeElementParser):
    @staticmethod
    def parse(xml_content: str) -> UniformRandomTimer:
        testname = TreeElementParser.extract_attribute(xml_content, ATTR_TESTNAME) or "Uniform Random Timer"
        enabled_attr = TreeElementParser.extract_attribute(xml_content, ATTR_ENABLED)
        enabled = enabled_attr != "false"
        
        timer = UniformRandomTimer(testname=testname, enabled=enabled)
        
        comment = TreeElementParser.extract_simple_prop_value(xml_content, TESTPLAN_COMMENTS)
        if comment:
            timer.change_comment(comment)
        
        delay = TreeElementParser.extract_simple_prop_value(xml_content, UNIFORMRANDOMTIMER_DELAY)
        if delay:
            timer.set_delay_raw(delay)
        
        range_val = TreeElementParser.extract_simple_prop_value(xml_content, UNIFORMRANDOMTIMER_RANGE)
        if range_val:
            timer.set_range_raw(range_val)
        
        return timer