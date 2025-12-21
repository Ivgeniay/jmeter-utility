from jmx_builder.parsers.elements.base import TreeElementParser
from jmx_builder.models.tree import KeystoreConfig
from jmx_builder.parsers.const import *


class KeystoreConfigParser(TreeElementParser):
    @staticmethod
    def parse(xml_content: str) -> KeystoreConfig:
        testname = TreeElementParser.extract_attribute(xml_content, ATTR_TESTNAME) or "Keystore Configuration"
        enabled_attr = TreeElementParser.extract_attribute(xml_content, ATTR_ENABLED)
        enabled = enabled_attr != "false"
        
        element = KeystoreConfig(testname=testname, enabled=enabled)
        
        comment = TreeElementParser.extract_simple_prop_value(xml_content, TESTPLAN_COMMENTS)
        if comment:
            element.change_comment(comment)
        
        client_cert_alias = TreeElementParser.extract_simple_prop_value(xml_content, KEYSTORECONFIG_CLIENT_CERT_ALIAS_VAR_NAME)
        if client_cert_alias:
            element.set_client_cert_alias_var_name(client_cert_alias)
        
        end_index = TreeElementParser.extract_simple_prop_value(xml_content, KEYSTORECONFIG_END_INDEX)
        if end_index:
            element.set_end_index(end_index)
        
        preload = TreeElementParser.extract_simple_prop_value(xml_content, KEYSTORECONFIG_PRELOAD)
        if preload:
            element.set_preload(preload.lower() == "true")
        
        start_index = TreeElementParser.extract_simple_prop_value(xml_content, KEYSTORECONFIG_START_INDEX)
        if start_index:
            element.set_start_index(start_index)
        
        return element