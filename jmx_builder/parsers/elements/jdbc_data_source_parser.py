from jmx_builder.parsers.elements.base import TreeElementParser
from jmx_builder.models.tree import JDBCDataSource
from jmx_builder.parsers.const import *


class JDBCDataSourceParser(TreeElementParser):
    @staticmethod
    def parse(xml_content: str) -> JDBCDataSource:
        testname = TreeElementParser.extract_attribute(xml_content, ATTR_TESTNAME) or "JDBC Connection Configuration"
        enabled_attr = TreeElementParser.extract_attribute(xml_content, ATTR_ENABLED)
        enabled = enabled_attr != "false"
        
        element = JDBCDataSource(testname=testname, enabled=enabled)
        
        comment = TreeElementParser.extract_simple_prop_value(xml_content, TESTPLAN_COMMENTS)
        if comment:
            element.change_comment(comment)
        
        autocommit = TreeElementParser.extract_simple_prop_value(xml_content, JDBCDATASOURCE_AUTOCOMMIT)
        if autocommit:
            element.set_autocommit(autocommit.lower() == "true")
        
        check_query = TreeElementParser.extract_simple_prop_value(xml_content, JDBCDATASOURCE_CHECK_QUERY)
        if check_query:
            element.set_check_query(check_query)
        
        connection_age = TreeElementParser.extract_simple_prop_value(xml_content, JDBCDATASOURCE_CONNECTION_AGE)
        if connection_age:
            element.set_connection_age(connection_age)
        
        connection_properties = TreeElementParser.extract_simple_prop_value(xml_content, JDBCDATASOURCE_CONNECTION_PROPERTIES)
        if connection_properties:
            element.set_connection_properties(connection_properties)
        
        datasource = TreeElementParser.extract_simple_prop_value(xml_content, JDBCDATASOURCE_DATASOURCE)
        if datasource:
            element.set_datasource(datasource)
        
        db_url = TreeElementParser.extract_simple_prop_value(xml_content, JDBCDATASOURCE_DB_URL)
        if db_url:
            element.set_db_url(db_url)
        
        driver = TreeElementParser.extract_simple_prop_value(xml_content, JDBCDATASOURCE_DRIVER)
        if driver:
            element.set_driver(driver)
        
        init_query = TreeElementParser.extract_simple_prop_value(xml_content, JDBCDATASOURCE_INIT_QUERY)
        if init_query:
            element.set_init_query(init_query)
        
        keep_alive = TreeElementParser.extract_simple_prop_value(xml_content, JDBCDATASOURCE_KEEP_ALIVE)
        if keep_alive:
            element.set_keep_alive(keep_alive.lower() == "true")
        
        password = TreeElementParser.extract_simple_prop_value(xml_content, JDBCDATASOURCE_PASSWORD)
        if password:
            element.set_password(password)
        
        pool_max = TreeElementParser.extract_simple_prop_value(xml_content, JDBCDATASOURCE_POOL_MAX)
        if pool_max:
            element.set_pool_max(pool_max)
        
        preinit = TreeElementParser.extract_simple_prop_value(xml_content, JDBCDATASOURCE_PREINIT)
        if preinit:
            element.set_preinit(preinit.lower() == "true")
        
        timeout = TreeElementParser.extract_simple_prop_value(xml_content, JDBCDATASOURCE_TIMEOUT)
        if timeout:
            element.set_timeout(timeout)
        
        transaction_isolation = TreeElementParser.extract_simple_prop_value(xml_content, JDBCDATASOURCE_TRANSACTION_ISOLATION)
        if transaction_isolation:
            element.set_transaction_isolation(transaction_isolation)
        
        trim_interval = TreeElementParser.extract_simple_prop_value(xml_content, JDBCDATASOURCE_TRIM_INTERVAL)
        if trim_interval:
            element.set_trim_interval(trim_interval)
        
        username = TreeElementParser.extract_simple_prop_value(xml_content, JDBCDATASOURCE_USERNAME)
        if username:
            element.set_username(username)
        
        pool_prepared_statements = TreeElementParser.extract_simple_prop_value(xml_content, JDBCDATASOURCE_POOL_PREPARED_STATEMENTS)
        if pool_prepared_statements:
            element.set_pool_prepared_statements(pool_prepared_statements)
        
        return element