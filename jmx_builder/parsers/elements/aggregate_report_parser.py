from jmx_builder.parsers.elements.base import TreeElementParser
from jmx_builder.parsers.elements.view_results_tree_parser import ViewResultsTreeParser
from jmx_builder.models.tree import AggregateReport
from jmx_builder.parsers.const import *


class AggregateReportParser(TreeElementParser):
    @staticmethod
    def parse(xml_content: str) -> AggregateReport:
        testname = TreeElementParser.extract_attribute(xml_content, ATTR_TESTNAME) or "Aggregate Report"
        enabled_attr = TreeElementParser.extract_attribute(xml_content, ATTR_ENABLED)
        enabled = enabled_attr != "false"
        
        collector = AggregateReport(testname=testname, enabled=enabled)
        
        comment = TreeElementParser.extract_simple_prop_value(xml_content, TESTPLAN_COMMENTS)
        if comment:
            collector.change_comment(comment)
        
        error_logging = TreeElementParser.extract_simple_prop_value(xml_content, RESULTCOLLECTOR_ERROR_LOGGING)
        if error_logging:
            collector.set_error_logging(error_logging.lower() == "true")
        
        filename = TreeElementParser.extract_simple_prop_value(xml_content, RESULTCOLLECTOR_FILENAME)
        if filename is not None:
            collector.set_filename(filename)
        
        use_group_name = TreeElementParser.extract_simple_prop_value(xml_content, RESULTCOLLECTOR_USE_GROUP_NAME)
        if use_group_name:
            collector.set_use_group_name(use_group_name.lower() == "true")
        
        ViewResultsTreeParser._parse_save_config(xml_content, collector.save_config)
        
        return collector