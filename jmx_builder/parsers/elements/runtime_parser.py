from jmx_builder.parsers.elements.base import TreeElementParser
from jmx_builder.models.tree import RunTime
from jmx_builder.parsers.const import (
    ATTR_TESTNAME,
    ATTR_ENABLED,
    TESTPLAN_COMMENTS,
    RUNTIME_SECONDS,
)


class RunTimeParser(TreeElementParser):
    @staticmethod
    def parse(xml_content: str) -> RunTime:
        testname = TreeElementParser.extract_attribute(xml_content, ATTR_TESTNAME) or "Runtime Controller"
        enabled_attr = TreeElementParser.extract_attribute(xml_content, ATTR_ENABLED)
        enabled = enabled_attr != "false"
        
        controller = RunTime(testname=testname, enabled=enabled)
        
        comment = TreeElementParser.extract_simple_prop_value(xml_content, TESTPLAN_COMMENTS)
        if comment:
            controller.change_comment(comment)
        
        seconds = TreeElementParser.extract_simple_prop_value(xml_content, RUNTIME_SECONDS)
        if seconds:
            controller.set_seconds_raw(seconds)
        
        return controller