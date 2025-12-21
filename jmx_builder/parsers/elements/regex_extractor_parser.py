from jmx_builder.parsers.elements.base import TreeElementParser
from jmx_builder.models.tree import RegexExtractor
from jmx_builder.parsers.const import (
    ATTR_TESTNAME,
    ATTR_ENABLED,
    TESTPLAN_COMMENTS,
    REGEXEXTRACTOR_USE_HEADERS,
    REGEXEXTRACTOR_REFNAME,
    REGEXEXTRACTOR_REGEX,
    REGEXEXTRACTOR_TEMPLATE,
    REGEXEXTRACTOR_DEFAULT,
    REGEXEXTRACTOR_DEFAULT_EMPTY_VALUE,
    REGEXEXTRACTOR_MATCH_NUMBER,
    SAMPLE_SCOPE,
    SCOPE_VARIABLE,
)


class RegexExtractorParser(TreeElementParser):
    @staticmethod
    def parse(xml_content: str) -> RegexExtractor:
        testname = TreeElementParser.extract_attribute(xml_content, ATTR_TESTNAME) or "Regular Expression Extractor"
        enabled_attr = TreeElementParser.extract_attribute(xml_content, ATTR_ENABLED)
        enabled = enabled_attr != "false"
        
        extractor = RegexExtractor(testname=testname, enabled=enabled)
        
        comment = TreeElementParser.extract_simple_prop_value(xml_content, TESTPLAN_COMMENTS)
        if comment:
            extractor.change_comment(comment)
        
        use_headers = TreeElementParser.extract_simple_prop_value(xml_content, REGEXEXTRACTOR_USE_HEADERS)
        if use_headers is not None:
            extractor.set_field_raw(use_headers)
        
        refname = TreeElementParser.extract_simple_prop_value(xml_content, REGEXEXTRACTOR_REFNAME)
        if refname is not None:
            extractor.set_refname(refname)
        
        regex = TreeElementParser.extract_simple_prop_value(xml_content, REGEXEXTRACTOR_REGEX)
        if regex is not None:
            extractor.set_regex(regex)
        
        template = TreeElementParser.extract_simple_prop_value(xml_content, REGEXEXTRACTOR_TEMPLATE)
        if template is not None:
            extractor.set_template(template)
        
        default = TreeElementParser.extract_simple_prop_value(xml_content, REGEXEXTRACTOR_DEFAULT)
        if default is not None:
            extractor.set_default(default)
        
        default_empty = TreeElementParser.extract_simple_prop_value(xml_content, REGEXEXTRACTOR_DEFAULT_EMPTY_VALUE)
        if default_empty:
            extractor.set_default_empty_value(default_empty.lower() == "true")
        
        match_number = TreeElementParser.extract_simple_prop_value(xml_content, REGEXEXTRACTOR_MATCH_NUMBER)
        if match_number is not None:
            extractor.set_match_number_raw(match_number)
        
        scope = TreeElementParser.extract_simple_prop_value(xml_content, SAMPLE_SCOPE)
        if scope is not None:
            extractor.set_scope_raw(scope)
        
        scope_variable = TreeElementParser.extract_simple_prop_value(xml_content, SCOPE_VARIABLE)
        if scope_variable is not None:
            extractor.set_scope_variable(scope_variable)
        
        return extractor