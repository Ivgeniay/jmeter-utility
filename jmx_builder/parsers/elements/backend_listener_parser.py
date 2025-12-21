from jmx_builder.parsers.elements.base import TreeElementParser
from jmx_builder.models.tree import BackendListener
from jmx_builder.parsers.const import *
import re


class BackendListenerParser(TreeElementParser):
    @staticmethod
    def parse(xml_content: str) -> BackendListener:
        testname = TreeElementParser.extract_attribute(xml_content, ATTR_TESTNAME) or "Backend Listener"
        enabled_attr = TreeElementParser.extract_attribute(xml_content, ATTR_ENABLED)
        enabled = enabled_attr != "false"
        
        listener = BackendListener(testname=testname, enabled=enabled)
        listener.clear_arguments()
        
        comment = TreeElementParser.extract_simple_prop_value(xml_content, TESTPLAN_COMMENTS)
        if comment:
            listener.change_comment(comment)
        
        classname = TreeElementParser.extract_simple_prop_value(xml_content, BACKENDLISTENER_CLASSNAME)
        if classname:
            listener.set_classname_raw(classname)
        
        queue_size = TreeElementParser.extract_simple_prop_value(xml_content, BACKENDLISTENER_QUEUE_SIZE)
        if queue_size:
            listener.set_queue_size_raw(queue_size)
        
        arguments_content = TreeElementParser.extract_element_prop_content(xml_content, BACKENDLISTENER_ARGUMENTS)
        if arguments_content:
            collection_content = TreeElementParser.extract_collection_prop_content(arguments_content, ARGUMENTS_ARGUMENTS)
            if collection_content:
                BackendListenerParser._parse_arguments(listener, collection_content)
        
        return listener
    
    @staticmethod
    def _parse_arguments(listener: BackendListener, collection_content: str) -> None:
        element_props = re.findall(
            r'<elementProp\s+name="[^"]*"[^>]*>(.*?)</elementProp>',
            collection_content,
            re.DOTALL
        )
        
        for prop_content in element_props:
            name = TreeElementParser.extract_simple_prop_value(prop_content, ARGUMENT_NAME)
            value = TreeElementParser.extract_simple_prop_value(prop_content, ARGUMENT_VALUE)
            
            if name is not None:
                listener.add_argument(name, value if value is not None else "")