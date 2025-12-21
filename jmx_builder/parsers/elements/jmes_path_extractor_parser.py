from jmx_builder.parsers.elements.base import TreeElementParser
from jmx_builder.models.tree import JMESPathExtractor
from jmx_builder.parsers.const import *


class JMESPathExtractorParser(TreeElementParser):
    @staticmethod
    def parse(xml_content: str) -> JMESPathExtractor:
        testname = TreeElementParser.extract_attribute(xml_content, ATTR_TESTNAME) or "JSON JMESPath Extractor"
        enabled_attr = TreeElementParser.extract_attribute(xml_content, ATTR_ENABLED)
        enabled = enabled_attr != "false"
        
        extractor = JMESPathExtractor(testname=testname, enabled=enabled)
        
        comment = TreeElementParser.extract_simple_prop_value(xml_content, TESTPLAN_COMMENTS)
        if comment:
            extractor.change_comment(comment)
        
        reference_name = TreeElementParser.extract_simple_prop_value(xml_content, JMESEXTRACTOR_REFERENCE_NAME)
        if reference_name is not None:
            extractor.set_reference_name(reference_name)
        
        jmes_path_expr = TreeElementParser.extract_simple_prop_value(xml_content, JMESEXTRACTOR_JMES_PATH_EXPR)
        if jmes_path_expr is not None:
            extractor.set_jmes_path_expr(jmes_path_expr)
        
        match_number = TreeElementParser.extract_simple_prop_value(xml_content, JMESEXTRACTOR_MATCH_NUMBER)
        if match_number is not None:
            extractor.set_match_number_raw(match_number)
        
        default_value = TreeElementParser.extract_simple_prop_value(xml_content, JMESEXTRACTOR_DEFAULT_VALUE)
        if default_value is not None:
            extractor.set_default_value(default_value)
        
        scope = TreeElementParser.extract_simple_prop_value(xml_content, SAMPLE_SCOPE)
        if scope is not None:
            extractor.set_scope_raw(scope)
        
        scope_variable = TreeElementParser.extract_simple_prop_value(xml_content, SCOPE_VARIABLE)
        if scope_variable is not None:
            extractor.set_scope_variable(scope_variable)
        
        return extractor