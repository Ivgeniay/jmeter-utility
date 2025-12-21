from jmx_builder.parsers.elements.base import TreeElementParser
from jmx_builder.models.tree import DNSCacheManager
from jmx_builder.parsers.const import *
import re


class DNSCacheManagerParser(TreeElementParser):
    @staticmethod
    def parse(xml_content: str) -> DNSCacheManager:
        testname = TreeElementParser.extract_attribute(xml_content, ATTR_TESTNAME) or "DNS Cache Manager"
        enabled_attr = TreeElementParser.extract_attribute(xml_content, ATTR_ENABLED)
        enabled = enabled_attr != "false"
        
        manager = DNSCacheManager(testname=testname, enabled=enabled)
        
        comment = TreeElementParser.extract_simple_prop_value(xml_content, TESTPLAN_COMMENTS)
        if comment:
            manager.change_comment(comment)
        
        clear_each = TreeElementParser.extract_simple_prop_value(xml_content, DNSCACHEMANAGER_CLEAR_EACH_ITERATION)
        if clear_each:
            manager.set_clear_each_iteration(clear_each.lower() == "true")
        
        is_custom = TreeElementParser.extract_simple_prop_value(xml_content, DNSCACHEMANAGER_IS_CUSTOM_RESOLVER)
        if is_custom:
            manager.set_is_custom_resolver(is_custom.lower() == "true")
        
        servers_content = TreeElementParser.extract_collection_prop_content(xml_content, DNSCACHEMANAGER_SERVERS)
        if servers_content:
            DNSCacheManagerParser._parse_servers(manager, servers_content)
        
        hosts_content = TreeElementParser.extract_collection_prop_content(xml_content, DNSCACHEMANAGER_HOSTS)
        if hosts_content:
            DNSCacheManagerParser._parse_hosts(manager, hosts_content)
        
        return manager
    
    @staticmethod
    def _parse_servers(manager: DNSCacheManager, collection_content: str) -> None:
        string_props = re.finditer(
            r'<stringProp\s+name="[^"]*">([^<]*)</stringProp>',
            collection_content
        )
        
        for match in string_props:
            server = match.group(1)
            if server:
                manager.add_server(server)
    
    @staticmethod
    def _parse_hosts(manager: DNSCacheManager, collection_content: str) -> None:
        element_props = re.finditer(
            r'<elementProp\s+name="[^"]*"[^>]*elementType="StaticHost"[^>]*>(.*?)</elementProp>',
            collection_content,
            re.DOTALL
        )
        
        for match in element_props:
            prop_content = match.group(1)
            
            hostname = TreeElementParser.extract_simple_prop_value(prop_content, STATICHOST_NAME) or ""
            address = TreeElementParser.extract_simple_prop_value(prop_content, STATICHOST_ADDRESS) or ""
            
            if hostname:
                manager.add_host(hostname, address)