from jmx_builder.parsers.elements.base import TreeElementParser
from jmx_builder.models.tree import JSONPostProcessor
from jmx_builder.parsers.const import *


class JSONPostProcessorParser(TreeElementParser):
    @staticmethod
    def parse(xml_content: str) -> JSONPostProcessor:
        testname = TreeElementParser.extract_attribute(xml_content, ATTR_TESTNAME) or "JSON Extractor"
        enabled_attr = TreeElementParser.extract_attribute(xml_content, ATTR_ENABLED)
        enabled = enabled_attr != "false"
        
        extractor = JSONPostProcessor(testname=testname, enabled=enabled)
        
        comment = TreeElementParser.extract_simple_prop_value(xml_content, TESTPLAN_COMMENTS)
        if comment:
            extractor.change_comment(comment)
        
        reference_names = TreeElementParser.extract_simple_prop_value(xml_content, JSONPOSTPROCESSOR_REFERENCE_NAMES)
        if reference_names is not None:
            extractor.set_reference_names(reference_names)
        
        json_path_exprs = TreeElementParser.extract_simple_prop_value(xml_content, JSONPOSTPROCESSOR_JSON_PATH_EXPRS)
        if json_path_exprs is not None:
            extractor.set_json_path_exprs(json_path_exprs)
        
        match_numbers = TreeElementParser.extract_simple_prop_value(xml_content, JSONPOSTPROCESSOR_MATCH_NUMBERS)
        if match_numbers is not None:
            extractor.set_match_numbers(match_numbers)
        
        default_values = TreeElementParser.extract_simple_prop_value(xml_content, JSONPOSTPROCESSOR_DEFAULT_VALUES)
        if default_values is not None:
            extractor.set_default_values(default_values)
        
        compute_concat = TreeElementParser.extract_simple_prop_value(xml_content, JSONPOSTPROCESSOR_COMPUTE_CONCAT)
        if compute_concat:
            extractor.set_compute_concat(compute_concat.lower() == "true")
        
        scope = TreeElementParser.extract_simple_prop_value(xml_content, SAMPLE_SCOPE)
        if scope is not None:
            extractor.set_scope_raw(scope)
        
        scope_variable = TreeElementParser.extract_simple_prop_value(xml_content, SCOPE_VARIABLE)
        if scope_variable is not None:
            extractor.set_scope_variable(scope_variable)
        
        return extractor