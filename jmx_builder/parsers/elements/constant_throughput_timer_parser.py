from jmx_builder.parsers.elements.base import TreeElementParser
from jmx_builder.models.tree import ConstantThroughputTimer
from jmx_builder.parsers.const import (
    ATTR_TESTNAME,
    ATTR_ENABLED,
    TESTPLAN_COMMENTS,
    CONSTANTTHROUGHPUTTIMER_THROUGHPUT,
    CONSTANTTHROUGHPUTTIMER_CALC_MODE,
)
import re


class ConstantThroughputTimerParser(TreeElementParser):
    @staticmethod
    def parse(xml_content: str) -> ConstantThroughputTimer:
        testname = TreeElementParser.extract_attribute(xml_content, ATTR_TESTNAME) or "Constant Throughput Timer"
        enabled_attr = TreeElementParser.extract_attribute(xml_content, ATTR_ENABLED)
        enabled = enabled_attr != "false"
        
        timer = ConstantThroughputTimer(testname=testname, enabled=enabled)
        
        comment = TreeElementParser.extract_simple_prop_value(xml_content, TESTPLAN_COMMENTS)
        if comment:
            timer.change_comment(comment)
        
        throughput = ConstantThroughputTimerParser._extract_double_prop(xml_content, CONSTANTTHROUGHPUTTIMER_THROUGHPUT)
        if throughput is not None:
            timer.set_throughput(throughput)
        
        calc_mode = TreeElementParser.extract_simple_prop_value(xml_content, CONSTANTTHROUGHPUTTIMER_CALC_MODE)
        if calc_mode:
            timer.set_calc_mode_raw(int(calc_mode))
        
        return timer
    
    @staticmethod
    def _extract_double_prop(xml_content: str, prop_name: str) -> float | None:
        pattern = rf'<doubleProp>\s*<name>{prop_name}</name>\s*<value>([^<]*)</value>'
        match = re.search(pattern, xml_content)
        if match:
            return float(match.group(1))
        return None