from jmx_builder.parsers.elements.base import TreeElementParser
from jmx_builder.models.tree import LoopController
from jmx_builder.parsers.const import (
    ATTR_TESTNAME,
    ATTR_ENABLED,
    TESTPLAN_COMMENTS,
    LOOPCONTROLLER_LOOPS,
    LOOPCONTROLLER_CONTINUE_FOREVER,
)


class LoopControllerParser(TreeElementParser):
    @staticmethod
    def parse(xml_content: str) -> LoopController:
        testname = TreeElementParser.extract_attribute(xml_content, ATTR_TESTNAME) or "Loop Controller"
        enabled_attr = TreeElementParser.extract_attribute(xml_content, ATTR_ENABLED)
        enabled = enabled_attr != "false"
        
        controller = LoopController(testname=testname, enabled=enabled)
        
        comment = TreeElementParser.extract_simple_prop_value(xml_content, TESTPLAN_COMMENTS)
        if comment:
            controller.change_comment(comment)
        
        loops = TreeElementParser.extract_simple_prop_value(xml_content, LOOPCONTROLLER_LOOPS)
        if loops:
            if loops == "-1":
                controller.set_loop_count_infinite(True)
            elif loops.lstrip("-").isdigit():
                controller.set_loop_count(int(loops))
            else:
                controller.set_loop_count_raw(loops)
        
        return controller