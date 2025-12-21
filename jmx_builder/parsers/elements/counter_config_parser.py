from jmx_builder.parsers.elements.base import TreeElementParser
from jmx_builder.models.tree import CounterConfig
from jmx_builder.parsers.const import *


class CounterConfigParser(TreeElementParser):
    @staticmethod
    def parse(xml_content: str) -> CounterConfig:
        testname = TreeElementParser.extract_attribute(xml_content, ATTR_TESTNAME) or "Counter"
        enabled_attr = TreeElementParser.extract_attribute(xml_content, ATTR_ENABLED)
        enabled = enabled_attr != "false"
        
        counter = CounterConfig(testname=testname, enabled=enabled)
        
        comment = TreeElementParser.extract_simple_prop_value(xml_content, TESTPLAN_COMMENTS)
        if comment:
            counter.change_comment(comment)
        
        start = TreeElementParser.extract_simple_prop_value(xml_content, COUNTERCONFIG_START)
        if start:
            counter.set_start(start)
        
        end = TreeElementParser.extract_simple_prop_value(xml_content, COUNTERCONFIG_END)
        if end:
            counter.set_end(end)
        
        incr = TreeElementParser.extract_simple_prop_value(xml_content, COUNTERCONFIG_INCR)
        if incr:
            counter.set_incr(incr)
        
        variable_name = TreeElementParser.extract_simple_prop_value(xml_content, COUNTERCONFIG_NAME)
        if variable_name:
            counter.set_variable_name(variable_name)
        
        format_val = TreeElementParser.extract_simple_prop_value(xml_content, COUNTERCONFIG_FORMAT)
        if format_val:
            counter.set_format(format_val)
        
        per_user = TreeElementParser.extract_simple_prop_value(xml_content, COUNTERCONFIG_PER_USER)
        if per_user:
            counter.set_per_user(per_user.lower() == "true")
        
        reset = TreeElementParser.extract_simple_prop_value(xml_content, COUNTERCONFIG_RESET_ON_TG_ITERATION)
        if reset:
            counter.set_reset_on_tg_iteration(reset.lower() == "true")
        
        return counter