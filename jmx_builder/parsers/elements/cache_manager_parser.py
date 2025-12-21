from jmx_builder.parsers.elements.base import TreeElementParser
from jmx_builder.models.tree import CacheManager
from jmx_builder.parsers.const import (
    ATTR_TESTNAME,
    ATTR_ENABLED,
    TESTPLAN_COMMENTS,
    CACHEMANAGER_CLEAR_EACH_ITERATION,
    CACHEMANAGER_USE_EXPIRES,
    CACHEMANAGER_CONTROLLED_BY_THREAD,
    CACHEMANAGER_MAX_SIZE,
)


class CacheManagerParser(TreeElementParser):
    @staticmethod
    def parse(xml_content: str) -> CacheManager:
        testname = TreeElementParser.extract_attribute(xml_content, ATTR_TESTNAME) or "HTTP Cache Manager"
        enabled_attr = TreeElementParser.extract_attribute(xml_content, ATTR_ENABLED)
        enabled = enabled_attr != "false"
        
        manager = CacheManager(testname=testname, enabled=enabled)
        
        comment = TreeElementParser.extract_simple_prop_value(xml_content, TESTPLAN_COMMENTS)
        if comment:
            manager.change_comment(comment)
        
        clear_each = TreeElementParser.extract_simple_prop_value(xml_content, CACHEMANAGER_CLEAR_EACH_ITERATION)
        if clear_each:
            manager.set_clear_each_iteration(clear_each.lower() == "true")
        
        use_expires = TreeElementParser.extract_simple_prop_value(xml_content, CACHEMANAGER_USE_EXPIRES)
        if use_expires:
            manager.set_use_expires(use_expires.lower() == "true")
        
        controlled = TreeElementParser.extract_simple_prop_value(xml_content, CACHEMANAGER_CONTROLLED_BY_THREAD)
        if controlled:
            manager.set_controlled_by_thread(controlled.lower() == "true")
        
        max_size = TreeElementParser.extract_simple_prop_value(xml_content, CACHEMANAGER_MAX_SIZE)
        if max_size:
            manager.set_max_size(int(max_size))
        
        return manager