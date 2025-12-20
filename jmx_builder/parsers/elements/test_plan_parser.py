from jmx_builder.parsers.elements.tree_element_parser import TreeElementParser
from jmx_builder.models.tree import TestPlan
from jmx_builder.parsers.const import (
    ATTR_ENABLED,
    ATTR_TESTNAME,
    TESTPLAN_COMMENTS,
    TESTPLAN_FUNCTIONAL_MODE,
    TESTPLAN_SERIALIZE_THREADGROUPS,
    TESTPLAN_TEARDOWN_ON_SHUTDOWN,
    TESTPLAN_USER_DEFINED_VARIABLES,
    TESTPLAN_USER_DEFINE_CLASSPATH,
    ARGUMENT_NAME,
    ARGUMENT_VALUE,
    ARGUMENTS_ARGUMENTS,
)


class TestPlanParser(TreeElementParser):
    @staticmethod
    def parse(xml_content: str) -> TestPlan:
        testname = TreeElementParser.extract_attribute(xml_content, ATTR_TESTNAME) or "Test Plan"
        enabled_attr = TreeElementParser.extract_attribute(xml_content, ATTR_ENABLED)
        enabled = enabled_attr != "false"
        
        test_plan = TestPlan(testname=testname, enabled=enabled)

        comment = TreeElementParser.extract_simple_prop_value(xml_content, TESTPLAN_COMMENTS)
        if comment:
            test_plan.change_comment(comment)

        functional_mode = TreeElementParser.extract_simple_prop_value(xml_content, TESTPLAN_FUNCTIONAL_MODE)
        if functional_mode:
            test_plan.functional_mode.value = functional_mode.lower() == "true"

        serialize = TreeElementParser.extract_simple_prop_value(xml_content, TESTPLAN_SERIALIZE_THREADGROUPS)
        if serialize:
            test_plan.serialize_threadgroups.value = serialize.lower() == "true"

        teardown = TreeElementParser.extract_simple_prop_value(xml_content, TESTPLAN_TEARDOWN_ON_SHUTDOWN)
        if teardown:
            test_plan.teardown_on_shutdown.value = teardown.lower() == "true"

        classpath = TreeElementParser.extract_simple_prop_value(xml_content, TESTPLAN_USER_DEFINE_CLASSPATH)
        if classpath:
            test_plan.user_define_classpath.value = classpath

        variables_content = TreeElementParser.extract_element_prop_content(xml_content, TESTPLAN_USER_DEFINED_VARIABLES)
        if variables_content:
            collection_content = TreeElementParser.extract_collection_prop_content(variables_content, ARGUMENTS_ARGUMENTS)
            if collection_content:
                TestPlanParser._parse_variables(test_plan, collection_content)
        
        return test_plan
    
    @staticmethod
    def _parse_variables(test_plan: TestPlan, collection_content: str) -> None:
        import re
        
        element_props = re.findall(
            r'<elementProp\s+name="[^"]*"[^>]*>(.*?)</elementProp>',
            collection_content,
            re.DOTALL
        )
        
        for prop_content in element_props:
            name = TreeElementParser.extract_simple_prop_value(prop_content, ARGUMENT_NAME)
            value = TreeElementParser.extract_simple_prop_value(prop_content, ARGUMENT_VALUE)
            
            if name is not None and value is not None:
                test_plan.add_variable(name, value)