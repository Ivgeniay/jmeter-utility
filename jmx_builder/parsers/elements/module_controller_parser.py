from jmx_builder.parsers.elements.base import TreeElementParser
from jmx_builder.models.tree import ModuleController
from jmx_builder.parsers.const import (
    ATTR_TESTNAME,
    ATTR_ENABLED,
    TESTPLAN_COMMENTS,
    MODULECONTROLLER_NODE_PATH,
)
import re


class ModuleControllerParser(TreeElementParser):
    @staticmethod
    def parse(xml_content: str) -> ModuleController:
        testname = TreeElementParser.extract_attribute(xml_content, ATTR_TESTNAME) or "Module Controller"
        enabled_attr = TreeElementParser.extract_attribute(xml_content, ATTR_ENABLED)
        enabled = enabled_attr != "false"
        
        controller = ModuleController(testname=testname, enabled=enabled)
        
        comment = TreeElementParser.extract_simple_prop_value(xml_content, TESTPLAN_COMMENTS)
        if comment:
            controller.change_comment(comment)
        
        collection_content = TreeElementParser.extract_collection_prop_content(xml_content, MODULECONTROLLER_NODE_PATH)
        if collection_content:
            path_list = ModuleControllerParser._parse_node_path(collection_content)
            if path_list:
                controller.set_module_path_list(path_list)
        
        return controller
    
    @staticmethod
    def _parse_node_path(collection_content: str) -> list[str]:
        path_list = []
        
        string_props = re.findall(
            r'<stringProp\s+name="[^"]*">([^<]*)</stringProp>',
            collection_content
        )
        
        for value in string_props:
            if value:
                path_list.append(value)
        
        return path_list