from jmx_builder.parsers.elements.base import TreeElementParser
from jmx_builder.models.tree import ForeachController
from jmx_builder.parsers.const import (
    ATTR_TESTNAME,
    ATTR_ENABLED,
    TESTPLAN_COMMENTS,
    FOREACHCONTROLLER_INPUT_VAL,
    FOREACHCONTROLLER_RETURN_VAL,
    FOREACHCONTROLLER_USE_SEPARATOR,
    FOREACHCONTROLLER_START_INDEX,
    FOREACHCONTROLLER_END_INDEX,
)


class ForeachControllerParser(TreeElementParser):
    @staticmethod
    def parse(xml_content: str) -> ForeachController:
        testname = TreeElementParser.extract_attribute(xml_content, ATTR_TESTNAME) or "ForEach Controller"
        enabled_attr = TreeElementParser.extract_attribute(xml_content, ATTR_ENABLED)
        enabled = enabled_attr != "false"
        
        controller = ForeachController(testname=testname, enabled=enabled)
        
        comment = TreeElementParser.extract_simple_prop_value(xml_content, TESTPLAN_COMMENTS)
        if comment:
            controller.change_comment(comment)
        
        input_val = TreeElementParser.extract_simple_prop_value(xml_content, FOREACHCONTROLLER_INPUT_VAL)
        if input_val:
            controller.set_input_variable(input_val)
        
        return_val = TreeElementParser.extract_simple_prop_value(xml_content, FOREACHCONTROLLER_RETURN_VAL)
        if return_val:
            controller.set_output_variable(return_val)
        
        use_separator = TreeElementParser.extract_simple_prop_value(xml_content, FOREACHCONTROLLER_USE_SEPARATOR)
        if use_separator:
            controller.set_use_separator(use_separator.lower() == "true")
        
        start_index = TreeElementParser.extract_simple_prop_value(xml_content, FOREACHCONTROLLER_START_INDEX)
        if start_index:
            controller.set_start_index_raw(start_index)
        
        end_index = TreeElementParser.extract_simple_prop_value(xml_content, FOREACHCONTROLLER_END_INDEX)
        if end_index:
            controller.set_end_index_raw(end_index)
        
        return controller