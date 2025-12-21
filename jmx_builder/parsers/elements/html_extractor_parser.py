from jmx_builder.parsers.elements.base import TreeElementParser
from jmx_builder.models.tree import HtmlExtractor
from jmx_builder.parsers.const import *


class HtmlExtractorParser(TreeElementParser):
    @staticmethod
    def parse(xml_content: str) -> HtmlExtractor:
        testname = TreeElementParser.extract_attribute(xml_content, ATTR_TESTNAME) or "CSS Selector Extractor"
        enabled_attr = TreeElementParser.extract_attribute(xml_content, ATTR_ENABLED)
        enabled = enabled_attr != "false"
        
        extractor = HtmlExtractor(testname=testname, enabled=enabled)
        
        comment = TreeElementParser.extract_simple_prop_value(xml_content, TESTPLAN_COMMENTS)
        if comment:
            extractor.change_comment(comment)
        
        refname = TreeElementParser.extract_simple_prop_value(xml_content, HTMLEXTRACTOR_REFNAME)
        if refname is not None:
            extractor.set_refname(refname)
        
        expr = TreeElementParser.extract_simple_prop_value(xml_content, HTMLEXTRACTOR_EXPR)
        if expr is not None:
            extractor.set_expr(expr)
        
        attribute = TreeElementParser.extract_simple_prop_value(xml_content, HTMLEXTRACTOR_ATTRIBUTE)
        if attribute is not None:
            extractor.set_attribute(attribute)
        
        default = TreeElementParser.extract_simple_prop_value(xml_content, HTMLEXTRACTOR_DEFAULT)
        if default is not None:
            extractor.set_default(default)
        
        default_empty = TreeElementParser.extract_simple_prop_value(xml_content, HTMLEXTRACTOR_DEFAULT_EMPTY_VALUE)
        if default_empty:
            extractor.set_default_empty_value(default_empty.lower() == "true")
        
        match_number = TreeElementParser.extract_simple_prop_value(xml_content, HTMLEXTRACTOR_MATCH_NUMBER)
        if match_number is not None:
            extractor.set_match_number_raw(match_number)
        
        extractor_impl = TreeElementParser.extract_simple_prop_value(xml_content, HTMLEXTRACTOR_EXTRACTOR_IMPL)
        if extractor_impl is not None:
            extractor.set_extractor_impl_raw(extractor_impl)
        
        scope = TreeElementParser.extract_simple_prop_value(xml_content, SAMPLE_SCOPE)
        if scope is not None:
            extractor.set_scope_raw(scope)
        
        scope_variable = TreeElementParser.extract_simple_prop_value(xml_content, SCOPE_VARIABLE)
        if scope_variable is not None:
            extractor.set_scope_variable(scope_variable)
        
        return extractor