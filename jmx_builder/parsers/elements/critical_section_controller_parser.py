from jmx_builder.parsers.elements.base import TreeElementParser
from jmx_builder.models.tree import CriticalSectionController
from jmx_builder.parsers.const import (
    ATTR_TESTNAME,
    ATTR_ENABLED,
    TESTPLAN_COMMENTS,
    CRITICALSECTIONCONTROLLER_LOCK_NAME,
)


class CriticalSectionControllerParser(TreeElementParser):
    @staticmethod
    def parse(xml_content: str) -> CriticalSectionController:
        testname = TreeElementParser.extract_attribute(xml_content, ATTR_TESTNAME) or "Critical Section Controller"
        enabled_attr = TreeElementParser.extract_attribute(xml_content, ATTR_ENABLED)
        enabled = enabled_attr != "false"
        
        controller = CriticalSectionController(testname=testname, enabled=enabled)
        
        comment = TreeElementParser.extract_simple_prop_value(xml_content, TESTPLAN_COMMENTS)
        if comment:
            controller.change_comment(comment)
        
        lock_name = TreeElementParser.extract_simple_prop_value(xml_content, CRITICALSECTIONCONTROLLER_LOCK_NAME)
        if lock_name:
            controller.set_lock_name(lock_name)
        
        return controller