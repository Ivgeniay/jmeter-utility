from jmx_builder.parsers.elements.aggregate_report_parser import AggregateReportParser
from jmx_builder.parsers.elements.arguments_parser import ArgumentsParser
from jmx_builder.parsers.elements.auth_manager_parser import AuthManagerParser
from jmx_builder.parsers.elements.backend_listener_parser import BackendListenerParser
from jmx_builder.parsers.elements.bolt_connection_element_parser import BoltConnectionElementParser
from jmx_builder.parsers.elements.boundary_extractor_parser import BoundaryExtractorParser
from jmx_builder.parsers.elements.cache_manager_parser import CacheManagerParser
from jmx_builder.parsers.elements.constant_throughput_timer_parser import ConstantThroughputTimerParser
from jmx_builder.parsers.elements.constant_timer_parser import ConstantTimerParser
from jmx_builder.parsers.elements.cookie_manager_parser import CookieManagerParser
from jmx_builder.parsers.elements.counter_config_parser import CounterConfigParser
from jmx_builder.parsers.elements.critical_section_controller_parser import CriticalSectionControllerParser
from jmx_builder.parsers.elements.csv_data_set_parser import CSVDataSetParser
from jmx_builder.parsers.elements.debug_post_processor_parser import DebugPostProcessorParser
from jmx_builder.parsers.elements.debug_sampler_parser import DebugSamplerParser
from jmx_builder.parsers.elements.dns_cache_manager_parser import DNSCacheManagerParser
from jmx_builder.parsers.elements.foreach_controller_parser import ForeachControllerParser
from jmx_builder.parsers.elements.ftp_request_defaults_parser import FtpRequestDefaultsParser
from jmx_builder.parsers.elements.generic_controller_parser import GenericControllerParser
from jmx_builder.parsers.elements.header_manager_parser import HeaderManagerParser
from jmx_builder.parsers.elements.html_extractor_parser import HtmlExtractorParser
from jmx_builder.parsers.elements.http_sampler_proxy_parser import HTTPSamplerProxyParser
from jmx_builder.parsers.elements.if_controller_parser import IfControllerParser
from jmx_builder.parsers.elements.include_controller_parser import IncludeControllerParser
from jmx_builder.parsers.elements.interleave_control_parser import InterleaveControlParser
from jmx_builder.parsers.elements.java_config_parser import JavaConfigParser
from jmx_builder.parsers.elements.jdbc_data_source_parser import JDBCDataSourceParser
from jmx_builder.parsers.elements.jmes_path_extractor_parser import JMESPathExtractorParser
from jmx_builder.parsers.elements.json_post_processor_parser import JSONPostProcessorParser
from jmx_builder.parsers.elements.jsr223_parser import JSR223PostProcessorParser, JSR223PreProcessorParser, JSR223SamplerParser
from jmx_builder.parsers.elements.keystore_config_parser import KeystoreConfigParser
from jmx_builder.parsers.elements.ldap_ext_request_defaults_parser import LdapExtRequestDefaultsParser
from jmx_builder.parsers.elements.ldap_request_defaults_parser import LdapRequestDefaultsParser
from jmx_builder.parsers.elements.login_config_element_parser import LoginConfigElementParser
from jmx_builder.parsers.elements.loop_controller_parser import LoopControllerParser
from jmx_builder.parsers.elements.module_controller_parser import ModuleControllerParser
from jmx_builder.parsers.elements.once_only_controller_parser import OnceOnlyControllerParser
from jmx_builder.parsers.elements.precise_throughput_timer_parser import PreciseThroughputTimerParser
from jmx_builder.parsers.elements.random_controller_parser import RandomControllerParser
from jmx_builder.parsers.elements.random_order_controller_parser import RandomOrderControllerParser
from jmx_builder.parsers.elements.random_variable_config_parser import RandomVariableConfigParser
from jmx_builder.parsers.elements.recording_controller_parser import RecordingControllerParser
from jmx_builder.parsers.elements.regex_extractor_parser import RegexExtractorParser
from jmx_builder.parsers.elements.result_action_parser import ResultActionParser
from jmx_builder.parsers.elements.runtime_parser import RunTimeParser
from jmx_builder.parsers.elements.simple_config_element_parser import SimpleConfigElementParser
from jmx_builder.parsers.elements.simple_data_writer_parser import SimpleDataWriterParser
from jmx_builder.parsers.elements.summary_report_parser import SummaryReportParser
from jmx_builder.parsers.elements.switch_controller_parser import SwitchControllerParser
from jmx_builder.parsers.elements.tcp_sampler_config_parser import TcpSamplerConfigParser
from jmx_builder.parsers.elements.test_action_parser import TestActionParser
from jmx_builder.parsers.elements.test_plan_parser import TestPlanParser
from jmx_builder.parsers.elements.thread_group_parser import ThreadGroupParser
from jmx_builder.parsers.elements.throughput_controller_parser import ThroughputControllerParser
from jmx_builder.parsers.elements.transaction_controller_parser import TransactionControllerParser
from jmx_builder.parsers.elements.uniform_random_timer_parser import UniformRandomTimerParser
from jmx_builder.parsers.elements.view_results_tree_parser import ViewResultsTreeParser
from jmx_builder.parsers.elements.while_controller_parser import WhileControllerParser
from jmx_builder.parsers.elements.xpath2_extractor_parser import XPath2ExtractorParser
from jmx_builder.parsers.elements.xpath_extractor_parser import XPathExtractorParser
from jmx_builder.parsers.tree_parser import TreeParser


def get_configured_parser() -> TreeParser:

    parser: TreeParser = TreeParser()
    parser.register_parser("TestPlan", TestPlanParser)

    # Thread
    parser.register_parser("ThreadGroup", ThreadGroupParser)

    # Config Elements
    parser.register_parser("CookieManager", CookieManagerParser)
    parser.register_parser("CacheManager", CacheManagerParser)
    parser.register_parser("Arguments", ArgumentsParser)
    parser.register_parser("HeaderManager", HeaderManagerParser)
    parser.register_parser("CSVDataSet", CSVDataSetParser)
    parser.register_parser("BoltConnectionElement", BoltConnectionElementParser)
    parser.register_parser("CounterConfig", CounterConfigParser)
    parser.register_parser("RandomVariableConfig", RandomVariableConfigParser)
    parser.register_parser("ConfigTestElement", LdapExtRequestDefaultsParser, "LdapExtConfigGui")
    parser.register_parser("ConfigTestElement", FtpRequestDefaultsParser, "FtpConfigGui")
    parser.register_parser("ConfigTestElement", LdapRequestDefaultsParser, "LdapConfigGui")
    parser.register_parser("ConfigTestElement", LoginConfigElementParser, "LoginConfigGui")
    parser.register_parser("ConfigTestElement", SimpleConfigElementParser, "SimpleConfigGui")
    parser.register_parser("ConfigTestElement", TcpSamplerConfigParser, "TCPConfigGui")
    parser.register_parser("KeystoreConfig", KeystoreConfigParser)
    parser.register_parser("AuthManager", AuthManagerParser)
    parser.register_parser("JDBCDataSource", JDBCDataSourceParser)
    parser.register_parser("JavaConfig", JavaConfigParser)
    parser.register_parser("DNSCacheManager", DNSCacheManagerParser)

    # Timers
    parser.register_parser("UniformRandomTimer", UniformRandomTimerParser)
    parser.register_parser("ConstantTimer", ConstantTimerParser)
    parser.register_parser("PreciseThroughputTimer", PreciseThroughputTimerParser)
    parser.register_parser("ConstantThroughputTimer", ConstantThroughputTimerParser)

    # Samplers
    parser.register_parser("TestAction", TestActionParser)
    parser.register_parser("HTTPSamplerProxy", HTTPSamplerProxyParser)
    parser.register_parser("JSR223Sampler", JSR223SamplerParser)
    parser.register_parser("DebugSampler", DebugSamplerParser)

    # LISTENERS
    parser.register_parser("ResultCollector", ViewResultsTreeParser, "ViewResultsFullVisualizer")
    parser.register_parser("ResultCollector", SummaryReportParser, "SummaryReport")
    parser.register_parser("ResultCollector", AggregateReportParser, "StatVisualizer")
    parser.register_parser("ResultCollector", SimpleDataWriterParser, "SimpleDataWriter")
    parser.register_parser("BackendListener", BackendListenerParser)


    # PRE PROCESS
    parser.register_parser("JSR223PreProcessor", JSR223PreProcessorParser)

    # POST PROCESS
    parser.register_parser("JSR223PostProcessor", JSR223PostProcessorParser)
    parser.register_parser("RegexExtractor", RegexExtractorParser)
    parser.register_parser("JSONPostProcessor", JSONPostProcessorParser)
    parser.register_parser("HtmlExtractor", HtmlExtractorParser)
    parser.register_parser("BoundaryExtractor", BoundaryExtractorParser)
    parser.register_parser("JMESPathExtractor", JMESPathExtractorParser)
    parser.register_parser("DebugPostProcessor", DebugPostProcessorParser)
    parser.register_parser("ResultAction", ResultActionParser)
    parser.register_parser("XPathExtractor", XPathExtractorParser)
    parser.register_parser("XPath2Extractor", XPath2ExtractorParser)

    # Controls
    parser.register_parser("IfController", IfControllerParser)
    parser.register_parser("TransactionController", TransactionControllerParser)
    parser.register_parser("LoopController", LoopControllerParser)
    parser.register_parser("WhileController", WhileControllerParser)
    parser.register_parser("CriticalSectionController", CriticalSectionControllerParser)
    parser.register_parser("ForeachController", ForeachControllerParser)
    parser.register_parser("IncludeController", IncludeControllerParser)
    parser.register_parser("InterleaveControl", InterleaveControlParser)
    parser.register_parser("OnceOnlyController", OnceOnlyControllerParser)
    parser.register_parser("RandomController", RandomControllerParser)
    parser.register_parser("RandomOrderController", RandomOrderControllerParser)
    parser.register_parser("RecordingController", RecordingControllerParser)
    parser.register_parser("RunTime", RunTimeParser)
    parser.register_parser("GenericController", GenericControllerParser)
    parser.register_parser("ThroughputController", ThroughputControllerParser)
    parser.register_parser("ModuleController", ModuleControllerParser)
    parser.register_parser("SwitchController", SwitchControllerParser)
    
    return parser