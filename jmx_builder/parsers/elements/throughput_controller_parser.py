from jmx_builder.parsers.elements.base import TreeElementParser
from jmx_builder.models.tree import ThroughputController
from jmx_builder.parsers.const import (
    ATTR_TESTNAME,
    ATTR_ENABLED,
    TESTPLAN_COMMENTS,
    THROUGHPUTCONTROLLER_STYLE,
    THROUGHPUTCONTROLLER_PER_THREAD,
    THROUGHPUTCONTROLLER_MAX_THROUGHPUT,
    THROUGHPUTCONTROLLER_PERCENT_THROUGHPUT,
)
import re


class ThroughputControllerParser(TreeElementParser):
    @staticmethod
    def parse(xml_content: str) -> ThroughputController:
        testname = TreeElementParser.extract_attribute(xml_content, ATTR_TESTNAME) or "Throughput Controller"
        enabled_attr = TreeElementParser.extract_attribute(xml_content, ATTR_ENABLED)
        enabled = enabled_attr != "false"
        
        controller = ThroughputController(testname=testname, enabled=enabled)
        
        comment = TreeElementParser.extract_simple_prop_value(xml_content, TESTPLAN_COMMENTS)
        if comment:
            controller.change_comment(comment)
        
        style = TreeElementParser.extract_simple_prop_value(xml_content, THROUGHPUTCONTROLLER_STYLE)
        if style:
            controller.set_style_raw(int(style))
        
        per_thread = TreeElementParser.extract_simple_prop_value(xml_content, THROUGHPUTCONTROLLER_PER_THREAD)
        if per_thread:
            controller.set_per_thread(per_thread.lower() == "true")
        
        max_throughput = TreeElementParser.extract_simple_prop_value(xml_content, THROUGHPUTCONTROLLER_MAX_THROUGHPUT)
        if max_throughput:
            controller.set_max_throughput(int(max_throughput))
        
        percent_throughput = ThroughputControllerParser._extract_float_property(xml_content, THROUGHPUTCONTROLLER_PERCENT_THROUGHPUT)
        if percent_throughput is not None:
            controller.set_percent_throughput(percent_throughput)
        
        return controller
    
    @staticmethod
    def _extract_float_property(xml_content: str, prop_name: str) -> float | None:
        pattern = rf'<FloatProperty>\s*<name>{prop_name}</name>\s*<value>([^<]*)</value>'
        match = re.search(pattern, xml_content)
        if match:
            return float(match.group(1))
        return None