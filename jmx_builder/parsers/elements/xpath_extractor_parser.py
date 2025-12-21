from jmx_builder.parsers.elements.base import TreeElementParser
from jmx_builder.models.tree import XPathExtractor
from jmx_builder.parsers.const import *


class XPathExtractorParser(TreeElementParser):
    @staticmethod
    def parse(xml_content: str) -> XPathExtractor:
        testname = TreeElementParser.extract_attribute(xml_content, ATTR_TESTNAME) or "XPath Extractor"
        enabled_attr = TreeElementParser.extract_attribute(xml_content, ATTR_ENABLED)
        enabled = enabled_attr != "false"
        
        extractor = XPathExtractor(testname=testname, enabled=enabled)
        
        comment = TreeElementParser.extract_simple_prop_value(xml_content, TESTPLAN_COMMENTS)
        if comment:
            extractor.change_comment(comment)
        
        default = TreeElementParser.extract_simple_prop_value(xml_content, XPATHEXTRACTOR_DEFAULT)
        if default is not None:
            extractor.set_default(default)
        
        refname = TreeElementParser.extract_simple_prop_value(xml_content, XPATHEXTRACTOR_REFNAME)
        if refname is not None:
            extractor.set_refname(refname)
        
        match_number = TreeElementParser.extract_simple_prop_value(xml_content, XPATHEXTRACTOR_MATCH_NUMBER)
        if match_number is not None:
            extractor.set_match_number_raw(match_number)
        
        xpath_query = TreeElementParser.extract_simple_prop_value(xml_content, XPATHEXTRACTOR_XPATH_QUERY)
        if xpath_query is not None:
            extractor.set_xpath_query(xpath_query)
        
        fragment = TreeElementParser.extract_simple_prop_value(xml_content, XPATHEXTRACTOR_FRAGMENT)
        if fragment:
            extractor.set_fragment(fragment.lower() == "true")
        
        validate = TreeElementParser.extract_simple_prop_value(xml_content, XPATHEXTRACTOR_VALIDATE)
        if validate:
            extractor.set_validate(validate.lower() == "true")
        
        tolerant = TreeElementParser.extract_simple_prop_value(xml_content, XPATHEXTRACTOR_TOLERANT)
        if tolerant:
            extractor.set_tolerant(tolerant.lower() == "true")
        
        namespace = TreeElementParser.extract_simple_prop_value(xml_content, XPATHEXTRACTOR_NAMESPACE)
        if namespace:
            extractor.set_namespace(namespace.lower() == "true")
        
        report_errors = TreeElementParser.extract_simple_prop_value(xml_content, XPATHEXTRACTOR_REPORT_ERRORS)
        if report_errors:
            extractor.set_report_errors(report_errors.lower() == "true")
        
        show_warnings = TreeElementParser.extract_simple_prop_value(xml_content, XPATHEXTRACTOR_SHOW_WARNINGS)
        if show_warnings:
            extractor.set_show_warnings(show_warnings.lower() == "true")
        
        whitespace = TreeElementParser.extract_simple_prop_value(xml_content, XPATHEXTRACTOR_WHITESPACE)
        if whitespace:
            extractor.set_whitespace(whitespace.lower() == "true")
        
        download_dtds = TreeElementParser.extract_simple_prop_value(xml_content, XPATHEXTRACTOR_DOWNLOAD_DTDS)
        if download_dtds:
            extractor.set_download_dtds(download_dtds.lower() == "true")
        
        scope = TreeElementParser.extract_simple_prop_value(xml_content, SAMPLE_SCOPE)
        if scope is not None:
            extractor.set_scope_raw(scope)
        
        scope_variable = TreeElementParser.extract_simple_prop_value(xml_content, SCOPE_VARIABLE)
        if scope_variable is not None:
            extractor.set_scope_variable(scope_variable)
        
        return extractor