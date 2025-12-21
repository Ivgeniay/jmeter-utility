from jmx_builder.parsers.elements.base import TreeElementParser
from jmx_builder.models.tree import LdapRequestDefaults
from jmx_builder.parsers.const import *
import re


class LdapRequestDefaultsParser(TreeElementParser):
    @staticmethod
    def parse(xml_content: str) -> LdapRequestDefaults:
        testname = TreeElementParser.extract_attribute(xml_content, ATTR_TESTNAME) or "LDAP Request Defaults"
        enabled_attr = TreeElementParser.extract_attribute(xml_content, ATTR_ENABLED)
        enabled = enabled_attr != "false"
        
        element = LdapRequestDefaults(testname=testname, enabled=enabled)
        
        comment = TreeElementParser.extract_simple_prop_value(xml_content, TESTPLAN_COMMENTS)
        if comment:
            element.change_comment(comment)
        
        servername = TreeElementParser.extract_simple_prop_value(xml_content, LDAP_SERVERNAME)
        if servername:
            element.set_servername(servername)
        
        port = TreeElementParser.extract_simple_prop_value(xml_content, LDAP_PORT)
        if port:
            element.set_port(port)
        
        rootdn = TreeElementParser.extract_simple_prop_value(xml_content, LDAP_ROOTDN)
        if rootdn:
            element.set_rootdn(rootdn)
        
        user_defined = TreeElementParser.extract_simple_prop_value(xml_content, LDAP_USER_DEFINED)
        if user_defined:
            element.set_user_defined(user_defined.lower() == "true")
        
        test = TreeElementParser.extract_simple_prop_value(xml_content, LDAP_TEST)
        if test:
            element.set_test(test)
        
        base_entry_dn = TreeElementParser.extract_simple_prop_value(xml_content, LDAP_BASE_ENTRY_DN)
        if base_entry_dn:
            element.set_base_entry_dn(base_entry_dn)
        
        arguments_content = TreeElementParser.extract_element_prop_content(xml_content, LDAP_ARGUMENTS)
        if arguments_content:
            LdapRequestDefaultsParser._parse_arguments(element, arguments_content)
        
        return element
    
    @staticmethod
    def _parse_arguments(element: LdapRequestDefaults, arguments_content: str) -> None:
        element_props = re.finditer(
            r'<elementProp\s+name="([^"]*)"[^>]*elementType="Argument"[^>]*>(.*?)</elementProp>',
            arguments_content,
            re.DOTALL
        )
        
        for match in element_props:
            prop_content = match.group(2)
            
            name = TreeElementParser.extract_simple_prop_value(prop_content, ARGUMENT_NAME)
            value = TreeElementParser.extract_simple_prop_value(prop_content, ARGUMENT_VALUE)
            
            if name:
                element.add_argument(name, value or "")