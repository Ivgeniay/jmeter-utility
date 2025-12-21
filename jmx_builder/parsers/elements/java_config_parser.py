from jmx_builder.parsers.elements.base import TreeElementParser
from jmx_builder.models.tree import JavaConfig
from jmx_builder.parsers.const import *
import re


class JavaConfigParser(TreeElementParser):
    @staticmethod
    def parse(xml_content: str) -> JavaConfig:
        testname = TreeElementParser.extract_attribute(xml_content, ATTR_TESTNAME) or "Java Request Defaults"
        enabled_attr = TreeElementParser.extract_attribute(xml_content, ATTR_ENABLED)
        enabled = enabled_attr != "false"
        
        element = JavaConfig(testname=testname, enabled=enabled)
        
        comment = TreeElementParser.extract_simple_prop_value(xml_content, TESTPLAN_COMMENTS)
        if comment:
            element.change_comment(comment)
        
        classname = TreeElementParser.extract_simple_prop_value(xml_content, JAVACONFIG_CLASSNAME)
        if classname:
            element.set_classname(classname)
        
        arguments_content = TreeElementParser.extract_element_prop_content(xml_content, JAVACONFIG_ARGUMENTS)
        if arguments_content:
            JavaConfigParser._parse_arguments(element, arguments_content)
        
        return element
    
    @staticmethod
    def _parse_arguments(element: JavaConfig, arguments_content: str) -> None:
        element_props = re.finditer(
            r'<elementProp\s+name="([^"]*)"[^>]*elementType="Argument"[^>]*>(.*?)</elementProp>',
            arguments_content,
            re.DOTALL
        )
        
        for match in element_props:
            prop_content = match.group(2)
            
            name = TreeElementParser.extract_simple_prop_value(prop_content, ARGUMENT_NAME)
            value = TreeElementParser.extract_simple_prop_value(prop_content, ARGUMENT_VALUE)
            
            if name:
                element.add_argument(name, value or "")