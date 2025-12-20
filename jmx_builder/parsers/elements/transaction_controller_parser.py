from jmx_builder.parsers.elements.base import TreeElementParser
from jmx_builder.models.tree import TransactionController
from jmx_builder.parsers.const import (
    ATTR_TESTNAME,
    ATTR_ENABLED,
    TESTPLAN_COMMENTS,
    TRANSACTIONCONTROLLER_PARENT,
    TRANSACTIONCONTROLLER_INCLUDE_TIMERS,
)


class TransactionControllerParser(TreeElementParser):
    @staticmethod
    def parse(xml_content: str) -> TransactionController:
        testname = TreeElementParser.extract_attribute(xml_content, ATTR_TESTNAME) or ""
        enabled_attr = TreeElementParser.extract_attribute(xml_content, ATTR_ENABLED)
        enabled = enabled_attr != "false"
        
        transaction = TransactionController(testname=testname, enabled=enabled)
        
        comment = TreeElementParser.extract_simple_prop_value(xml_content, TESTPLAN_COMMENTS)
        if comment:
            transaction.change_comment(comment)
        
        parent = TreeElementParser.extract_simple_prop_value(xml_content, TRANSACTIONCONTROLLER_PARENT)
        if parent:
            transaction.generate_parent_sample.value = parent.lower() == "true"
        
        include_timers = TreeElementParser.extract_simple_prop_value(xml_content, TRANSACTIONCONTROLLER_INCLUDE_TIMERS)
        if include_timers:
            transaction.include_timers.value = include_timers.lower() == "true"
        
        return transaction