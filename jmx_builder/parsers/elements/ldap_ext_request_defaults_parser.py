from jmx_builder.parsers.elements.base import TreeElementParser
from jmx_builder.models.tree import LdapExtRequestDefaults
from jmx_builder.parsers.const import *


class LdapExtRequestDefaultsParser(TreeElementParser):
    @staticmethod
    def parse(xml_content: str) -> LdapExtRequestDefaults:
        testname = TreeElementParser.extract_attribute(xml_content, ATTR_TESTNAME) or "LDAP Extended Request Defaults"
        enabled_attr = TreeElementParser.extract_attribute(xml_content, ATTR_ENABLED)
        enabled = enabled_attr != "false"
        
        element = LdapExtRequestDefaults(testname=testname, enabled=enabled)
        
        comment = TreeElementParser.extract_simple_prop_value(xml_content, TESTPLAN_COMMENTS)
        if comment:
            element.change_comment(comment)
        
        servername = TreeElementParser.extract_simple_prop_value(xml_content, LDAPEXT_SERVERNAME)
        if servername:
            element.set_servername(servername)
        
        port = TreeElementParser.extract_simple_prop_value(xml_content, LDAPEXT_PORT)
        if port:
            element.set_port(port)
        
        rootdn = TreeElementParser.extract_simple_prop_value(xml_content, LDAPEXT_ROOTDN)
        if rootdn:
            element.set_rootdn(rootdn)
        
        scope = TreeElementParser.extract_simple_prop_value(xml_content, LDAPEXT_SCOPE)
        if scope:
            element.set_scope(scope)
        
        countlimit = TreeElementParser.extract_simple_prop_value(xml_content, LDAPEXT_COUNTLIMIT)
        if countlimit:
            element.set_countlimit(countlimit)
        
        timelimit = TreeElementParser.extract_simple_prop_value(xml_content, LDAPEXT_TIMELIMIT)
        if timelimit:
            element.set_timelimit(timelimit)
        
        attributes = TreeElementParser.extract_simple_prop_value(xml_content, LDAPEXT_ATTRIBUTES)
        if attributes:
            element.set_attributes(attributes)
        
        return_object = TreeElementParser.extract_simple_prop_value(xml_content, LDAPEXT_RETURN_OBJECT)
        if return_object:
            element.set_return_object(return_object.lower() == "true")
        
        deref_aliases = TreeElementParser.extract_simple_prop_value(xml_content, LDAPEXT_DEREF_ALIASES)
        if deref_aliases:
            element.set_deref_aliases(deref_aliases.lower() == "true")
        
        connection_timeout = TreeElementParser.extract_simple_prop_value(xml_content, LDAPEXT_CONNECTION_TIMEOUT)
        if connection_timeout:
            element.set_connection_timeout(connection_timeout)
        
        parseflag = TreeElementParser.extract_simple_prop_value(xml_content, LDAPEXT_PARSEFLAG)
        if parseflag:
            element.set_parseflag(parseflag.lower() == "true")
        
        secure = TreeElementParser.extract_simple_prop_value(xml_content, LDAPEXT_SECURE)
        if secure:
            element.set_secure(secure.lower() == "true")
        
        trustall = TreeElementParser.extract_simple_prop_value(xml_content, LDAPEXT_TRUSTALL)
        if trustall:
            element.set_trustall(trustall.lower() == "true")
        
        user_dn = TreeElementParser.extract_simple_prop_value(xml_content, LDAPEXT_USER_DN)
        if user_dn:
            element.set_user_dn(user_dn)
        
        user_pw = TreeElementParser.extract_simple_prop_value(xml_content, LDAPEXT_USER_PW)
        if user_pw:
            element.set_user_pw(user_pw)
        
        comparedn = TreeElementParser.extract_simple_prop_value(xml_content, LDAPEXT_COMPAREDN)
        if comparedn:
            element.set_comparedn(comparedn)
        
        comparefilt = TreeElementParser.extract_simple_prop_value(xml_content, LDAPEXT_COMPAREFILT)
        if comparefilt:
            element.set_comparefilt(comparefilt)
        
        modddn = TreeElementParser.extract_simple_prop_value(xml_content, LDAPEXT_MODDDN)
        if modddn:
            element.set_modddn(modddn)
        
        newdn = TreeElementParser.extract_simple_prop_value(xml_content, LDAPEXT_NEWDN)
        if newdn:
            element.set_newdn(newdn)
        
        test = TreeElementParser.extract_simple_prop_value(xml_content, LDAPEXT_TEST)
        if test:
            element.set_test(test)
        
        return element