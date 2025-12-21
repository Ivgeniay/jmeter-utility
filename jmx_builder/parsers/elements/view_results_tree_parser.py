from jmx_builder.models.props import SampleSaveConfiguration
from jmx_builder.parsers.elements.base import TreeElementParser
from jmx_builder.models.tree import ViewResultsTree
from jmx_builder.parsers.const import *
import re


class ViewResultsTreeParser(TreeElementParser):
    @staticmethod
    def parse(xml_content: str) -> ViewResultsTree:
        testname = TreeElementParser.extract_attribute(xml_content, ATTR_TESTNAME) or "View Results Tree"
        enabled_attr = TreeElementParser.extract_attribute(xml_content, ATTR_ENABLED)
        enabled = enabled_attr != "false"
        
        collector = ViewResultsTree(testname=testname, enabled=enabled)
        
        comment = TreeElementParser.extract_simple_prop_value(xml_content, TESTPLAN_COMMENTS)
        if comment:
            collector.change_comment(comment)
        
        error_logging = TreeElementParser.extract_simple_prop_value(xml_content, RESULTCOLLECTOR_ERROR_LOGGING)
        if error_logging:
            collector.set_error_logging(error_logging.lower() == "true")
        
        success_only = TreeElementParser.extract_simple_prop_value(xml_content, RESULTCOLLECTOR_SUCCESS_ONLY_LOGGING)
        if success_only:
            collector.set_success_only_logging(success_only.lower() == "true")
        
        filename = TreeElementParser.extract_simple_prop_value(xml_content, RESULTCOLLECTOR_FILENAME)
        if filename is not None:
            collector.set_filename(filename)
        
        ViewResultsTreeParser._parse_save_config(xml_content, collector.save_config)
        
        return collector
    
    @staticmethod
    def _parse_save_config(xml_content: str, config: 'SampleSaveConfiguration') -> None:
        def extract_bool(name: str) -> bool | None:
            pattern = rf'<{name}>([^<]*)</{name}>'
            match = re.search(pattern, xml_content)
            if match:
                return match.group(1).lower() == "true"
            return None
        
        def extract_int(name: str) -> int | None:
            pattern = rf'<{name}>([^<]*)</{name}>'
            match = re.search(pattern, xml_content)
            if match:
                return int(match.group(1))
            return None
        
        if (v := extract_bool("time")) is not None: config.time = v
        if (v := extract_bool("latency")) is not None: config.latency = v
        if (v := extract_bool("timestamp")) is not None: config.timestamp = v
        if (v := extract_bool("success")) is not None: config.success = v
        if (v := extract_bool("label")) is not None: config.label = v
        if (v := extract_bool("code")) is not None: config.code = v
        if (v := extract_bool("message")) is not None: config.message = v
        if (v := extract_bool("threadName")) is not None: config.thread_name = v
        if (v := extract_bool("dataType")) is not None: config.data_type = v
        if (v := extract_bool("encoding")) is not None: config.encoding = v
        if (v := extract_bool("assertions")) is not None: config.assertions = v
        if (v := extract_bool("subresults")) is not None: config.subresults = v
        if (v := extract_bool("responseData")) is not None: config.response_data = v
        if (v := extract_bool("samplerData")) is not None: config.sampler_data = v
        if (v := extract_bool("xml")) is not None: config.xml = v
        if (v := extract_bool("fieldNames")) is not None: config.field_names = v
        if (v := extract_bool("responseHeaders")) is not None: config.response_headers = v
        if (v := extract_bool("requestHeaders")) is not None: config.request_headers = v
        if (v := extract_bool("responseDataOnError")) is not None: config.response_data_on_error = v
        if (v := extract_bool("saveAssertionResultsFailureMessage")) is not None: config.save_assertion_results_failure_message = v
        if (v := extract_int("assertionsResultsToSave")) is not None: config.assertions_results_to_save = v
        if (v := extract_bool("bytes")) is not None: config.bytes = v
        if (v := extract_bool("sentBytes")) is not None: config.sent_bytes = v
        if (v := extract_bool("url")) is not None: config.url = v
        if (v := extract_bool("threadCounts")) is not None: config.thread_counts = v
        if (v := extract_bool("idleTime")) is not None: config.idle_time = v
        if (v := extract_bool("connectTime")) is not None: config.connect_time = v
        if (v := extract_bool("fileName")) is not None: config.file_name = v
        if (v := extract_bool("hostname")) is not None: config.hostname = v
        if (v := extract_bool("sampleCount")) is not None: config.sample_count = v