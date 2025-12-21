from jmx_builder.parsers.elements.base import TreeElementParser
from jmx_builder.models.tree import XPath2Extractor
from jmx_builder.parsers.const import *


class XPath2ExtractorParser(TreeElementParser):
    @staticmethod
    def parse(xml_content: str) -> XPath2Extractor:
        testname = TreeElementParser.extract_attribute(xml_content, ATTR_TESTNAME) or "XPath2 Extractor"
        enabled_attr = TreeElementParser.extract_attribute(xml_content, ATTR_ENABLED)
        enabled = enabled_attr != "false"
        
        extractor = XPath2Extractor(testname=testname, enabled=enabled)
        
        comment = TreeElementParser.extract_simple_prop_value(xml_content, TESTPLAN_COMMENTS)
        if comment:
            extractor.change_comment(comment)
        
        default = TreeElementParser.extract_simple_prop_value(xml_content, XPATH2EXTRACTOR_DEFAULT)
        if default is not None:
            extractor.set_default(default)
        
        refname = TreeElementParser.extract_simple_prop_value(xml_content, XPATH2EXTRACTOR_REFNAME)
        if refname is not None:
            extractor.set_refname(refname)
        
        match_number = TreeElementParser.extract_simple_prop_value(xml_content, XPATH2EXTRACTOR_MATCH_NUMBER)
        if match_number is not None:
            extractor.set_match_number_raw(match_number)
        
        xpath_query = TreeElementParser.extract_simple_prop_value(xml_content, XPATH2EXTRACTOR_XPATH_QUERY)
        if xpath_query is not None:
            extractor.set_xpath_query(xpath_query)
        
        fragment = TreeElementParser.extract_simple_prop_value(xml_content, XPATH2EXTRACTOR_FRAGMENT)
        if fragment:
            extractor.set_fragment(fragment.lower() == "true")
        
        namespaces = TreeElementParser.extract_simple_prop_value(xml_content, XPATH2EXTRACTOR_NAMESPACES)
        if namespaces is not None:
            extractor.set_namespaces(namespaces)
        
        scope = TreeElementParser.extract_simple_prop_value(xml_content, SAMPLE_SCOPE)
        if scope is not None:
            extractor.set_scope_raw(scope)
        
        scope_variable = TreeElementParser.extract_simple_prop_value(xml_content, SCOPE_VARIABLE)
        if scope_variable is not None:
            extractor.set_scope_variable(scope_variable)
        
        return extractor