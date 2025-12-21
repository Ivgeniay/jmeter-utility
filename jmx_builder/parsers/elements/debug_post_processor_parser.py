from jmx_builder.parsers.elements.base import TreeElementParser
from jmx_builder.models.tree import DebugPostProcessor
from jmx_builder.parsers.const import *


class DebugPostProcessorParser(TreeElementParser):
    @staticmethod
    def parse(xml_content: str) -> DebugPostProcessor:
        testname = TreeElementParser.extract_attribute(xml_content, ATTR_TESTNAME) or "Debug PostProcessor"
        enabled_attr = TreeElementParser.extract_attribute(xml_content, ATTR_ENABLED)
        enabled = enabled_attr != "false"
        
        processor = DebugPostProcessor(testname=testname, enabled=enabled)
        
        comment = TreeElementParser.extract_simple_prop_value(xml_content, TESTPLAN_COMMENTS)
        if comment:
            processor.change_comment(comment)
        
        display_props = TreeElementParser.extract_simple_prop_value(xml_content, DEBUGPOSTPROCESSOR_DISPLAY_JMETER_PROPERTIES)
        if display_props:
            processor.set_display_jmeter_properties(display_props.lower() == "true")
        
        display_vars = TreeElementParser.extract_simple_prop_value(xml_content, DEBUGPOSTPROCESSOR_DISPLAY_JMETER_VARIABLES)
        if display_vars:
            processor.set_display_jmeter_variables(display_vars.lower() == "true")
        
        display_sampler = TreeElementParser.extract_simple_prop_value(xml_content, DEBUGPOSTPROCESSOR_DISPLAY_SAMPLER_PROPERTIES)
        if display_sampler:
            processor.set_display_sampler_properties(display_sampler.lower() == "true")
        
        display_system = TreeElementParser.extract_simple_prop_value(xml_content, DEBUGPOSTPROCESSOR_DISPLAY_SYSTEM_PROPERTIES)
        if display_system:
            processor.set_display_system_properties(display_system.lower() == "true")
        
        return processor