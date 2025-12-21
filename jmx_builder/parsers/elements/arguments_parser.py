from jmx_builder.parsers.elements.base import TreeElementParser
from jmx_builder.models.tree import Arguments
from jmx_builder.parsers.const import (
    ATTR_TESTNAME,
    ATTR_ENABLED,
    TESTPLAN_COMMENTS,
    ARGUMENTS_ARGUMENTS,
    ARGUMENT_NAME,
    ARGUMENT_VALUE,
    ARGUMENT_DESC,
)
import re


class ArgumentsParser(TreeElementParser):
    @staticmethod
    def parse(xml_content: str) -> Arguments:
        testname = TreeElementParser.extract_attribute(xml_content, ATTR_TESTNAME) or "User Defined Variables"
        enabled_attr = TreeElementParser.extract_attribute(xml_content, ATTR_ENABLED)
        enabled = enabled_attr != "false"
        
        arguments = Arguments(testname=testname, enabled=enabled)
        
        comment = TreeElementParser.extract_simple_prop_value(xml_content, TESTPLAN_COMMENTS)
        if comment:
            arguments.change_comment(comment)
        
        collection_content = TreeElementParser.extract_collection_prop_content(xml_content, ARGUMENTS_ARGUMENTS)
        if collection_content:
            ArgumentsParser._parse_variables(arguments, collection_content)
        
        return arguments
    
    @staticmethod
    def _parse_variables(arguments: Arguments, collection_content: str) -> None:
        element_props = re.findall(
            r'<elementProp\s+name="[^"]*"[^>]*>(.*?)</elementProp>',
            collection_content,
            re.DOTALL
        )
        
        for prop_content in element_props:
            name = TreeElementParser.extract_simple_prop_value(prop_content, ARGUMENT_NAME)
            value = TreeElementParser.extract_simple_prop_value(prop_content, ARGUMENT_VALUE)
            desc = TreeElementParser.extract_simple_prop_value(prop_content, ARGUMENT_DESC) or ""
            
            if name is not None and value is not None:
                arguments.add_variable(name, value, desc)