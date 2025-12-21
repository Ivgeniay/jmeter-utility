from jmx_builder.parsers.elements.base import TreeElementParser
from jmx_builder.models.tree import TcpSamplerConfig
from jmx_builder.parsers.const import *


class TcpSamplerConfigParser(TreeElementParser):
    @staticmethod
    def parse(xml_content: str) -> TcpSamplerConfig:
        testname = TreeElementParser.extract_attribute(xml_content, ATTR_TESTNAME) or "TCP Sampler Config"
        enabled_attr = TreeElementParser.extract_attribute(xml_content, ATTR_ENABLED)
        enabled = enabled_attr != "false"
        
        element = TcpSamplerConfig(testname=testname, enabled=enabled)
        
        comment = TreeElementParser.extract_simple_prop_value(xml_content, TESTPLAN_COMMENTS)
        if comment:
            element.change_comment(comment)
        
        server = TreeElementParser.extract_simple_prop_value(xml_content, TCPSAMPLER_SERVER)
        if server:
            element.set_server(server)
        
        port = TreeElementParser.extract_simple_prop_value(xml_content, TCPSAMPLER_PORT)
        if port:
            element.set_port(port)
        
        reuse_connection = TreeElementParser.extract_simple_prop_value(xml_content, TCPSAMPLER_REUSE_CONNECTION)
        if reuse_connection:
            element.set_reuse_connection(reuse_connection.lower() == "true")
        
        nodelay = TreeElementParser.extract_simple_prop_value(xml_content, TCPSAMPLER_NODELAY)
        if nodelay:
            element.set_nodelay(nodelay.lower() == "true")
        
        timeout = TreeElementParser.extract_simple_prop_value(xml_content, TCPSAMPLER_TIMEOUT)
        if timeout:
            element.set_timeout(timeout)
        
        request = TreeElementParser.extract_simple_prop_value(xml_content, TCPSAMPLER_REQUEST)
        if request:
            element.set_request(request)
        
        close_connection = TreeElementParser.extract_simple_prop_value(xml_content, TCPSAMPLER_CLOSE_CONNECTION)
        if close_connection:
            element.set_close_connection(close_connection.lower() == "true")
        
        classname = TreeElementParser.extract_simple_prop_value(xml_content, TCPSAMPLER_CLASSNAME)
        if classname:
            element.set_classname(classname)
        
        ctimeout = TreeElementParser.extract_simple_prop_value(xml_content, TCPSAMPLER_CTIMEOUT)
        if ctimeout:
            element.set_ctimeout(ctimeout)
        
        so_linger = TreeElementParser.extract_simple_prop_value(xml_content, TCPSAMPLER_SO_LINGER)
        if so_linger:
            element.set_so_linger(so_linger)
        
        eol_byte = TreeElementParser.extract_simple_prop_value(xml_content, TCPSAMPLER_EOL_BYTE)
        if eol_byte:
            element.set_eol_byte(eol_byte)
        
        return element