import argparse;
import sys;
import re

from jmeter_runner import run_and_collect
from console import CompositeLog, ConsoleLog, Log, SLog
from jmx_builder.parsers.elements.aggregate_report_parser import AggregateReportParser
from jmx_builder.parsers.elements.arguments_parser import ArgumentsParser
from jmx_builder.parsers.elements.backend_listener_parser import BackendListenerParser
from jmx_builder.parsers.elements.boundary_extractor_parser import BoundaryExtractorParser
from jmx_builder.parsers.elements.cache_manager_parser import CacheManagerParser
from jmx_builder.parsers.elements.constant_throughput_timer_parser import ConstantThroughputTimerParser
from jmx_builder.parsers.elements.constant_timer_parser import ConstantTimerParser
from jmx_builder.parsers.elements.cookie_manager_parser import CookieManagerParser
from jmx_builder.parsers.elements.critical_section_controller_parser import CriticalSectionControllerParser
from jmx_builder.parsers.elements.debug_post_processor_parser import DebugPostProcessorParser
from jmx_builder.parsers.elements.debug_sampler_parser import DebugSamplerParser
from jmx_builder.parsers.elements.foreach_controller_parser import ForeachControllerParser
from jmx_builder.parsers.elements.generic_controller_parser import GenericControllerParser
from jmx_builder.parsers.elements.header_manager_parser import HeaderManagerParser
from jmx_builder.parsers.elements.html_extractor_parser import HtmlExtractorParser
from jmx_builder.parsers.elements.http_sampler_proxy_parser import HTTPSamplerProxyParser
from jmx_builder.parsers.elements.if_controller_parser import IfControllerParser
from jmx_builder.parsers.elements.include_controller_parser import IncludeControllerParser
from jmx_builder.parsers.elements.interleave_control_parser import InterleaveControlParser
from jmx_builder.parsers.elements.jmes_path_extractor_parser import JMESPathExtractorParser
from jmx_builder.parsers.elements.json_post_processor_parser import JSONPostProcessorParser
from jmx_builder.parsers.elements.jsr223_parser import JSR223PostProcessorParser, JSR223PreProcessorParser, JSR223SamplerParser
from jmx_builder.parsers.elements.loop_controller_parser import LoopControllerParser
from jmx_builder.parsers.elements.module_controller_parser import ModuleControllerParser
from jmx_builder.parsers.elements.once_only_controller_parser import OnceOnlyControllerParser
from jmx_builder.parsers.elements.precise_throughput_timer_parser import PreciseThroughputTimerParser
from jmx_builder.parsers.elements.random_controller_parser import RandomControllerParser
from jmx_builder.parsers.elements.random_order_controller_parser import RandomOrderControllerParser
from jmx_builder.parsers.elements.recording_controller_parser import RecordingControllerParser
from jmx_builder.parsers.elements.regex_extractor_parser import RegexExtractorParser
from jmx_builder.parsers.elements.result_action_parser import ResultActionParser
from jmx_builder.parsers.elements.runtime_parser import RunTimeParser
from jmx_builder.parsers.elements.simple_data_writer_parser import SimpleDataWriterParser
from jmx_builder.parsers.elements.summary_report_parser import SummaryReportParser
from jmx_builder.parsers.elements.switch_controller_parser import SwitchControllerParser
from jmx_builder.parsers.elements.test_action_parser import TestActionParser
from jmx_builder.parsers.elements.throughput_controller_parser import ThroughputControllerParser
from jmx_builder.parsers.elements.uniform_random_timer_parser import UniformRandomTimerParser
from jmx_builder.parsers.elements.view_results_tree_parser import ViewResultsTreeParser
from jmx_builder.parsers.elements.while_controller_parser import WhileControllerParser
from jmx_builder.parsers.elements.xpath2_extractor_parser import XPath2ExtractorParser
from jmx_builder.parsers.elements.xpath_extractor_parser import XPathExtractorParser
from scope import extract_scope_by_element_name
from har_parser import parse_har
from jmeter_parser import parse_jmeter
from comparer import SimpleComparer, TransactionComparer


from jmx_builder.parsers.elements.test_plan_parser import TestPlanParser
from jmx_builder.parsers.elements.thread_group_parser import ThreadGroupParser
from jmx_builder.parsers.elements.transaction_controller_parser import TransactionControllerParser
from jmx_builder.parsers.tree_parser import TreeParser


def remove_suffix(
        filepath: str, 
        verbose: bool, 
        output: str | None, 
        scope: str | None
        ) -> int:
    
    def remove_jmeter_suffix(testname):
        return re.sub(r'-\d+$', '', testname)
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        change_counter = 0
        
        def replacer(match):
            nonlocal change_counter
            full_match: str = match.group(0)
            testname = match.group(1)
            new_testname = remove_jmeter_suffix(testname)
            result = full_match.replace(f'testname="{testname}"', f'testname="{new_testname}"')
            
            if testname != new_testname:
                change_counter = change_counter + 1
                if verbose:
                    SLog.log(f'{testname} -> {new_testname}')
            return result
        
        regex = r'<HTTPSamplerProxy[^>]*testname=\"([^\"]*)\"[^>]*>'

        if scope:
            scope_result = extract_scope_by_element_name(content, scope)
            if not scope_result.found:
                SLog.log(f'Element "{scope}" not found')
                return 1
            modified_scope = re.sub(regex, replacer, scope_result.content)
            new_content = content[:scope_result.start_pos] + modified_scope + content[scope_result.end_pos:]
        else:
            new_content = re.sub(regex, replacer, content)

        target_path = output if output else filepath
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        if verbose:
            SLog.log(f'Number of modified lines: {change_counter}')


    except Exception as ex:
        SLog.log(ex)
        return 1
    

    return 0

def add_methods(
        filepath: str, 
        verbose: bool, 
        output: str | None, 
        scope: str | None
        ) -> int:
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        change_counter = 0

        def replacer(match):
            nonlocal change_counter

            full_block = match.group(0)
            testname = match.group(1)
            method = match.group(2)
            
            if testname.startswith(method + ' '):
                return full_block
            
            new_testname = f'{method} {testname}'
            result = full_block.replace(f'testname="{testname}"', f'testname="{new_testname}"')
            change_counter = change_counter + 1

            if verbose:
                SLog.log(f'{testname} -> {new_testname}')
            
            return result
        
        regex = r'<HTTPSamplerProxy[^>]*testname="([^"]*)"[^>]*>.*?<stringProp name="HTTPSampler\.method">([^<]*)</stringProp>.*?</HTTPSamplerProxy>'
        if scope:
            scope_result = extract_scope_by_element_name(content, scope)
            if not scope_result.found:
                SLog.log(f'Element "{scope}" not found')
                return 1
            modified_scope = re.sub(regex, replacer, scope_result.content, flags=re.DOTALL)
            new_content = content[:scope_result.start_pos] + modified_scope + content[scope_result.end_pos:]
        else:
            new_content = re.sub(regex, replacer, content, flags=re.DOTALL)

        target_path = output if output else filepath
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        if verbose:
            SLog.log(f'Number of modified lines: {change_counter}')

    except Exception as ex:
        SLog.log(ex)
        return 1
    
    return 0

def compare_traffic(
        jmeter_path: str, 
        har_path: str, 
        scope: str | None, 
        difficult: str,
        verbose: bool) -> int:
    try:
        har_requests = parse_har(har_path)
        jmeter_requests = parse_jmeter(jmeter_path, scope)
        
        if difficult == 'simple':
            comparer = SimpleComparer()
        else:
            SLog.log(f'There is no {difficult}. Chech --help')
            exit(1)
        
        result = comparer.compare(har_requests, jmeter_requests)
        
        result.print_summary()
        
        if verbose:
            result.print_details()
        
        return 0
    
    except ValueError as ex:
        SLog.log(ex)
        return 1
    except Exception as ex:
        SLog.log(f'Error: {ex}')
        return 1

def run_and_compare(jmeter_path: str, jmx_path: str, har_path: str, difficult: str, verbose: bool) -> int:
    try:
        har_requests = parse_har(har_path)
        if verbose:
            SLog.log(f'Parsed {len(har_requests)} requests from HAR')

        jmeter_result = run_and_collect(jmeter_path, jmx_path)
        if verbose:
            SLog.log(f'Collected {len(jmeter_result.all_requests)} requests in {len(jmeter_result.transactions)} transactions')

        if difficult == 'simple':
            base_comparer = SimpleComparer()
        else:
            SLog.log(f'Unknown comparison method: {difficult}. Check --help')
            return 1

        if jmeter_result.transactions:
            comparer = TransactionComparer(base_comparer)
            result = comparer.compare(har_requests, jmeter_result)
            result.print_summary()
            if verbose:
                result.print_details()
        else:
            result = base_comparer.compare(har_requests, jmeter_result.all_requests)
            result.print_summary()
            if verbose:
                result.print_details()
        
        return 0
    
    except ValueError as ex:
        SLog.log(f'Error: {ex}')
        return 1
    except Exception as ex:
        SLog.log(f'Error: {ex}')
        return 1


consLog = ConsoleLog()
logger: CompositeLog = CompositeLog(consLog)
SLog.register_logger(logger)

xml = '''<?xml version="1.0" encoding="UTF-8"?>
<jmeterTestPlan version="1.2" properties="5.0" jmeter="5.6.3">
  <hashTree>
    <TestPlan guiclass="TestPlanGui" testclass="TestPlan" testname="Test Plan">
      <boolProp name="TestPlan.tearDown_on_shutdown">true</boolProp>
      <elementProp name="TestPlan.user_defined_variables" elementType="Arguments" guiclass="ArgumentsPanel" testclass="Arguments" testname="User Defined Variables">
        <collectionProp name="Arguments.arguments"/>
      </elementProp>
    </TestPlan>
    <hashTree>
      <ForeachController guiclass="ForeachControlPanel" testclass="ForeachController" testname="ForEach Controller">
        <stringProp name="ForeachController.inputVal">prefix</stringProp>
        <stringProp name="ForeachController.returnVal">varname</stringProp>
        <boolProp name="ForeachController.useSeparator">true</boolProp>
        <stringProp name="ForeachController.startIndex">1</stringProp>
        <stringProp name="ForeachController.endIndex">10</stringProp>
      </ForeachController>
      <hashTree/>
      <IncludeController guiclass="IncludeControllerGui" testclass="IncludeController" testname="Include Controller">
        <stringProp name="IncludeController.includepath">filename.jmx</stringProp>
      </IncludeController>
      <hashTree/>
      <OnceOnlyController guiclass="OnceOnlyControllerGui" testclass="OnceOnlyController" testname="Once Only Controller"/>
      <hashTree/>
      <InterleaveControl guiclass="InterleaveControlGui" testclass="InterleaveControl" testname="Interleave Controller">
        <intProp name="InterleaveControl.style">0</intProp>
        <boolProp name="InterleaveControl.accrossThreads">true</boolProp>
      </InterleaveControl>
      <hashTree/>
      <RandomController guiclass="RandomControlGui" testclass="RandomController" testname="Random Controller">
        <intProp name="InterleaveControl.style">1</intProp>
      </RandomController>
      <hashTree/>
      <RandomOrderController guiclass="RandomOrderControllerGui" testclass="RandomOrderController" testname="Random Order Controller"/>
      <hashTree/>
      <RecordingController guiclass="RecordController" testclass="RecordingController" testname="Recording Controller"/>
      <hashTree/>
      <RunTime guiclass="RunTimeGui" testclass="RunTime" testname="Runtime Controller">
        <stringProp name="RunTime.seconds">10</stringProp>
      </RunTime>
      <hashTree/>
      <GenericController guiclass="LogicControllerGui" testclass="GenericController" testname="Simple Controller"/>
      <hashTree/>
      <ThroughputController guiclass="ThroughputControllerGui" testclass="ThroughputController" testname="Throughput Controller">
        <intProp name="ThroughputController.style">1</intProp>
        <boolProp name="ThroughputController.perThread">true</boolProp>
        <intProp name="ThroughputController.maxThroughput">20</intProp>
        <FloatProperty>
          <name>ThroughputController.percentThroughput</name>
          <value>50.5</value>
          <savedValue>0.0</savedValue>
        </FloatProperty>
      </ThroughputController>
      <hashTree/>
      <SwitchController guiclass="SwitchControllerGui" testclass="SwitchController" testname="Switch Controller">
        <stringProp name="SwitchController.value">switch_value</stringProp>
      </SwitchController>
      <hashTree/>
      <ModuleController guiclass="ModuleControllerGui" testclass="ModuleController" testname="Module Controller">
        <collectionProp name="ModuleController.node_path">
          <stringProp name="764597751">Test Plan</stringProp>
          <stringProp name="1732785315">My Test Plan</stringProp>
          <stringProp name="-1948168983">Thread Group</stringProp>
        </collectionProp>
      </ModuleController>
      <hashTree/>
      <ModuleController guiclass="ModuleControllerGui" testclass="ModuleController" testname="Empty Module Controller"/>
      <hashTree/>
    </hashTree>
  </hashTree>
</jmeterTestPlan>'''

parser1: TreeParser = TreeParser()
parser1.register_parser("TestPlan", TestPlanParser)

# Thread
parser1.register_parser("ThreadGroup", ThreadGroupParser)

# Config Elements
parser1.register_parser("CookieManager", CookieManagerParser)
parser1.register_parser("CacheManager", CacheManagerParser)
parser1.register_parser("Arguments", ArgumentsParser)
parser1.register_parser("HeaderManager", HeaderManagerParser)

# Timers
parser1.register_parser("UniformRandomTimer", UniformRandomTimerParser)
parser1.register_parser("ConstantTimer", ConstantTimerParser)
parser1.register_parser("PreciseThroughputTimer", PreciseThroughputTimerParser)
parser1.register_parser("ConstantThroughputTimer", ConstantThroughputTimerParser)

# Samplers
parser1.register_parser("TestAction", TestActionParser)
parser1.register_parser("HTTPSamplerProxy", HTTPSamplerProxyParser)
parser1.register_parser("JSR223Sampler", JSR223SamplerParser)
parser1.register_parser("DebugSampler", DebugSamplerParser)

# LISTENERS
parser1.register_parser("ResultCollector", ViewResultsTreeParser, "ViewResultsFullVisualizer")
parser1.register_parser("ResultCollector", SummaryReportParser, "SummaryReport")
parser1.register_parser("ResultCollector", AggregateReportParser, "StatVisualizer")
parser1.register_parser("ResultCollector", SimpleDataWriterParser, "SimpleDataWriter")
parser1.register_parser("BackendListener", BackendListenerParser)


# PRE PROCESS
parser1.register_parser("JSR223PreProcessor", JSR223PreProcessorParser)

# POST PROCESS
parser1.register_parser("JSR223PostProcessor", JSR223PostProcessorParser)
parser1.register_parser("RegexExtractor", RegexExtractorParser)
parser1.register_parser("JSONPostProcessor", JSONPostProcessorParser)
parser1.register_parser("HtmlExtractor", HtmlExtractorParser)
parser1.register_parser("BoundaryExtractor", BoundaryExtractorParser)
parser1.register_parser("JMESPathExtractor", JMESPathExtractorParser)
parser1.register_parser("DebugPostProcessor", DebugPostProcessorParser)
parser1.register_parser("ResultAction", ResultActionParser)
parser1.register_parser("XPathExtractor", XPathExtractorParser)
parser1.register_parser("XPath2Extractor", XPath2ExtractorParser)

# Controls
parser1.register_parser("IfController", IfControllerParser)
parser1.register_parser("TransactionController", TransactionControllerParser)
parser1.register_parser("LoopController", LoopControllerParser)
parser1.register_parser("WhileController", WhileControllerParser)
parser1.register_parser("CriticalSectionController", CriticalSectionControllerParser)
parser1.register_parser("ForeachController", ForeachControllerParser)
parser1.register_parser("IncludeController", IncludeControllerParser)
parser1.register_parser("InterleaveControl", InterleaveControlParser)
parser1.register_parser("OnceOnlyController", OnceOnlyControllerParser)
parser1.register_parser("RandomController", RandomControllerParser)
parser1.register_parser("RandomOrderController", RandomOrderControllerParser)
parser1.register_parser("RecordingController", RecordingControllerParser)
parser1.register_parser("RunTime", RunTimeParser)
parser1.register_parser("GenericController", GenericControllerParser)
parser1.register_parser("ThroughputController", ThroughputControllerParser)
parser1.register_parser("ModuleController", ModuleControllerParser)
parser1.register_parser("SwitchController", SwitchControllerParser)



test_plan = parser1.parse(xml)

for child in test_plan.children[0].children:
    child.print_info()

res = test_plan.to_xml()
SLog.log("=============================================")
SLog.log(res)
SLog.log("=============================================")




if __name__ == "__main__":
    args_parser = argparse.ArgumentParser(
        description='Utilities for Automatic Http Request Processing in JMeter'
    )

    args_parser.add_argument('-i', '--input', help='Path to jmx file')
    args_parser.add_argument('-o', '--output', help='Path to output file. By default input file will be overrided')
    args_parser.add_argument('-v', '--verbose', help='Includes a detailed description of the changes', action='store_true')
    args_parser.add_argument('-p', '--prefix', help='Removes prefixes that JMeter creates while recording traffic in Http Requsets.', action='store_true')
    args_parser.add_argument('-m', '--method', help='Adds the method name to the Http Request name (/index.html -> GET /index.html)', action='store_true')
    args_parser.add_argument('-s', '--scope', help='Name of the element in the tree')
    args_parser.add_argument('-c', '--compare', help='Path to HAR file for comparison')
    args_parser.add_argument('-d', '--difficult', help='Comparison method. Available options: [simple]', default='simple')
    args_parser.add_argument('-r', '--run-compare', help='Run JMeter and compare with HAR. Requires --jmeter-path')
    args_parser.add_argument('-g', '--jmeter-path', help='Path to JMeter executable (jmeter, jmeter.sh, jmeter.bat)')


    args = args_parser.parse_args()


    if (args.prefix):
        if not args.input:
            SLog.log('Error: --input is required for comparison')
            exit(1)
        remove_suffix(args.input, args.verbose, args.output, args.scope)

    if (args.method):
        if not args.input:
            SLog.log('Error: --input is required for comparison')
            exit(1)
        add_methods(args.input, args.verbose, args.output, args.scope)
        exit(0)

    if (args.compare):
        if not args.input:
            SLog.log('Error: --input is required for comparison')
            exit(1)
        result = compare_traffic(args.input, args.compare, args.scope, args.difficult, args.verbose)
        exit(result)

    if args.run_compare:
        if not args.input:
            SLog.log('Error: --input is required for run-compare')
            exit(1)
        if not args.jmeter_path:
            SLog.log('Error: --jmeter-path is required for run-compare')
            exit(1)
        result = run_and_compare(args.jmeter_path, args.input, args.run_compare, args.difficult, args.verbose)
        exit(result)
    

    args_parser.print_help()