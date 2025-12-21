from jmx_builder.parsers.elements.base import TreeElementParser
from jmx_builder.models.tree import DebugSampler
from jmx_builder.parsers.const import (
    ATTR_TESTNAME,
    ATTR_ENABLED,
    TESTPLAN_COMMENTS,
    DEBUGSAMPLER_DISPLAY_JMETER_PROPERTIES,
    DEBUGSAMPLER_DISPLAY_JMETER_VARIABLES,
    DEBUGSAMPLER_DISPLAY_SYSTEM_PROPERTIES,
)


class DebugSamplerParser(TreeElementParser):
    @staticmethod
    def parse(xml_content: str) -> DebugSampler:
        testname = TreeElementParser.extract_attribute(xml_content, ATTR_TESTNAME) or "Debug Sampler"
        enabled_attr = TreeElementParser.extract_attribute(xml_content, ATTR_ENABLED)
        enabled = enabled_attr != "false"
        
        sampler = DebugSampler(testname=testname, enabled=enabled)
        
        comment = TreeElementParser.extract_simple_prop_value(xml_content, TESTPLAN_COMMENTS)
        if comment:
            sampler.change_comment(comment)
        
        display_props = TreeElementParser.extract_simple_prop_value(xml_content, DEBUGSAMPLER_DISPLAY_JMETER_PROPERTIES)
        if display_props:
            sampler.set_display_jmeter_properties(display_props.lower() == "true")
        
        display_vars = TreeElementParser.extract_simple_prop_value(xml_content, DEBUGSAMPLER_DISPLAY_JMETER_VARIABLES)
        if display_vars:
            sampler.set_display_jmeter_variables(display_vars.lower() == "true")
        
        display_system = TreeElementParser.extract_simple_prop_value(xml_content, DEBUGSAMPLER_DISPLAY_SYSTEM_PROPERTIES)
        if display_system:
            sampler.set_display_system_properties(display_system.lower() == "true")
        
        return sampler