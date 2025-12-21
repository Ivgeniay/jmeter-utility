from jmx_builder.parsers.elements.base import TreeElementParser
from jmx_builder.models.tree import RandomController
from jmx_builder.parsers.const import (
    ATTR_TESTNAME,
    ATTR_ENABLED,
    TESTPLAN_COMMENTS,
    INTERLEAVECONTROL_STYLE,
)


class RandomControllerParser(TreeElementParser):
    @staticmethod
    def parse(xml_content: str) -> RandomController:
        testname = TreeElementParser.extract_attribute(xml_content, ATTR_TESTNAME) or "Random Controller"
        enabled_attr = TreeElementParser.extract_attribute(xml_content, ATTR_ENABLED)
        enabled = enabled_attr != "false"
        
        controller = RandomController(testname=testname, enabled=enabled)
        
        comment = TreeElementParser.extract_simple_prop_value(xml_content, TESTPLAN_COMMENTS)
        if comment:
            controller.change_comment(comment)
        
        style = TreeElementParser.extract_simple_prop_value(xml_content, INTERLEAVECONTROL_STYLE)
        if style:
            controller.set_style_raw(int(style))
        
        return controller