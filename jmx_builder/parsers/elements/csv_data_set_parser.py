from jmx_builder.parsers.elements.base import TreeElementParser
from jmx_builder.models.tree import CSVDataSet
from jmx_builder.parsers.const import *


class CSVDataSetParser(TreeElementParser):
    @staticmethod
    def parse(xml_content: str) -> CSVDataSet:
        testname = TreeElementParser.extract_attribute(xml_content, ATTR_TESTNAME) or "CSV Data Set Config"
        enabled_attr = TreeElementParser.extract_attribute(xml_content, ATTR_ENABLED)
        enabled = enabled_attr != "false"
        
        csv_data_set = CSVDataSet(testname=testname, enabled=enabled)
        
        comment = TreeElementParser.extract_simple_prop_value(xml_content, TESTPLAN_COMMENTS)
        if comment:
            csv_data_set.change_comment(comment)
        
        filename = TreeElementParser.extract_simple_prop_value(xml_content, CSVDATASET_FILENAME)
        if filename:
            csv_data_set.set_filename(filename)
        
        file_encoding = TreeElementParser.extract_simple_prop_value(xml_content, CSVDATASET_FILE_ENCODING)
        if file_encoding:
            csv_data_set.set_file_encoding(file_encoding)
        
        variable_names = TreeElementParser.extract_simple_prop_value(xml_content, CSVDATASET_VARIABLE_NAMES)
        if variable_names:
            csv_data_set.set_variable_names(variable_names)
        
        ignore_first_line = TreeElementParser.extract_simple_prop_value(xml_content, CSVDATASET_IGNORE_FIRST_LINE)
        if ignore_first_line:
            csv_data_set.set_ignore_first_line(ignore_first_line.lower() == "true")
        
        delimiter = TreeElementParser.extract_simple_prop_value(xml_content, CSVDATASET_DELIMITER)
        if delimiter:
            csv_data_set.set_delimiter(delimiter)
        
        quoted_data = TreeElementParser.extract_simple_prop_value(xml_content, CSVDATASET_QUOTED_DATA)
        if quoted_data:
            csv_data_set.set_quoted_data(quoted_data.lower() == "true")
        
        recycle = TreeElementParser.extract_simple_prop_value(xml_content, CSVDATASET_RECYCLE)
        if recycle:
            csv_data_set.set_recycle(recycle.lower() == "true")
        
        stop_thread = TreeElementParser.extract_simple_prop_value(xml_content, CSVDATASET_STOP_THREAD)
        if stop_thread:
            csv_data_set.set_stop_thread(stop_thread.lower() == "true")
        
        share_mode = TreeElementParser.extract_simple_prop_value(xml_content, CSVDATASET_SHARE_MODE)
        if share_mode:
            csv_data_set.set_share_mode(share_mode)
        
        return csv_data_set