from jmx_builder.parsers.elements.base import TreeElementParser
from jmx_builder.models.tree import JSR223Sampler, JSR223PreProcessor, JSR223PostProcessor, JSR223Element
from jmx_builder.parsers.const import (
    ATTR_TESTNAME,
    ATTR_ENABLED,
    TESTPLAN_COMMENTS,
    JSR223_SCRIPT_LANGUAGE,
    JSR223_FILENAME,
    JSR223_PARAMETERS,
    JSR223_SCRIPT,
    JSR223_CACHE_KEY,
)


class JSR223Parser(TreeElementParser):
    @staticmethod
    def _parse_common(xml_content: str, element: JSR223Element) -> None:
        comment = TreeElementParser.extract_simple_prop_value(xml_content, TESTPLAN_COMMENTS)
        if comment:
            element.change_comment(comment)
        
        script_language = TreeElementParser.extract_simple_prop_value(xml_content, JSR223_SCRIPT_LANGUAGE)
        if script_language:
            element.set_script_language(script_language)
        
        filename = TreeElementParser.extract_simple_prop_value(xml_content, JSR223_FILENAME)
        if filename:
            element.set_filename(filename)
        
        parameters = TreeElementParser.extract_simple_prop_value(xml_content, JSR223_PARAMETERS)
        if parameters:
            element.set_parameters(parameters)
        
        script = TreeElementParser.extract_simple_prop_value(xml_content, JSR223_SCRIPT)
        if script:
            element.set_script(script)
        
        cache_key = TreeElementParser.extract_simple_prop_value(xml_content, JSR223_CACHE_KEY)
        if cache_key:
            element.set_cache_key(cache_key.lower() == "true")


class JSR223SamplerParser(JSR223Parser):
    @staticmethod
    def parse(xml_content: str) -> JSR223Sampler:
        testname = TreeElementParser.extract_attribute(xml_content, ATTR_TESTNAME) or "JSR223 Sampler"
        enabled_attr = TreeElementParser.extract_attribute(xml_content, ATTR_ENABLED)
        enabled = enabled_attr != "false"
        
        sampler = JSR223Sampler(testname=testname, enabled=enabled)
        JSR223Parser._parse_common(xml_content, sampler)
        
        return sampler


class JSR223PreProcessorParser(JSR223Parser):
    @staticmethod
    def parse(xml_content: str) -> JSR223PreProcessor:
        testname = TreeElementParser.extract_attribute(xml_content, ATTR_TESTNAME) or "JSR223 PreProcessor"
        enabled_attr = TreeElementParser.extract_attribute(xml_content, ATTR_ENABLED)
        enabled = enabled_attr != "false"
        
        preprocessor = JSR223PreProcessor(testname=testname, enabled=enabled)
        JSR223Parser._parse_common(xml_content, preprocessor)
        
        return preprocessor


class JSR223PostProcessorParser(JSR223Parser):
    @staticmethod
    def parse(xml_content: str) -> JSR223PostProcessor:
        testname = TreeElementParser.extract_attribute(xml_content, ATTR_TESTNAME) or "JSR223 PostProcessor"
        enabled_attr = TreeElementParser.extract_attribute(xml_content, ATTR_ENABLED)
        enabled = enabled_attr != "false"
        
        postprocessor = JSR223PostProcessor(testname=testname, enabled=enabled)
        JSR223Parser._parse_common(xml_content, postprocessor)
        
        return postprocessor