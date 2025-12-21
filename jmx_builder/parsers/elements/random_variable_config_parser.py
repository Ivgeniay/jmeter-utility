from jmx_builder.parsers.elements.base import TreeElementParser
from jmx_builder.models.tree import RandomVariableConfig
from jmx_builder.parsers.const import *


class RandomVariableConfigParser(TreeElementParser):
    @staticmethod
    def parse(xml_content: str) -> RandomVariableConfig:
        testname = TreeElementParser.extract_attribute(xml_content, ATTR_TESTNAME) or "Random Variable"
        enabled_attr = TreeElementParser.extract_attribute(xml_content, ATTR_ENABLED)
        enabled = enabled_attr != "false"
        
        config = RandomVariableConfig(testname=testname, enabled=enabled)
        
        comment = TreeElementParser.extract_simple_prop_value(xml_content, TESTPLAN_COMMENTS)
        if comment:
            config.change_comment(comment)
        
        maximum_value = TreeElementParser.extract_simple_prop_value(xml_content, RANDOMVARIABLE_MAXIMUM_VALUE)
        if maximum_value:
            config.set_maximum_value(maximum_value)
        
        minimum_value = TreeElementParser.extract_simple_prop_value(xml_content, RANDOMVARIABLE_MINIMUM_VALUE)
        if minimum_value:
            config.set_minimum_value(minimum_value)
        
        output_format = TreeElementParser.extract_simple_prop_value(xml_content, RANDOMVARIABLE_OUTPUT_FORMAT)
        if output_format:
            config.set_output_format(output_format)
        
        per_thread = TreeElementParser.extract_simple_prop_value(xml_content, RANDOMVARIABLE_PER_THREAD)
        if per_thread:
            config.set_per_thread(per_thread.lower() == "true")
        
        random_seed = TreeElementParser.extract_simple_prop_value(xml_content, RANDOMVARIABLE_RANDOM_SEED)
        if random_seed:
            config.set_random_seed(random_seed)
        
        variable_name = TreeElementParser.extract_simple_prop_value(xml_content, RANDOMVARIABLE_VARIABLE_NAME)
        if variable_name:
            config.set_variable_name(variable_name)
        
        return config