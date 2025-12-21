import argparse;
import sys;
import re

from jmeter_runner import run_and_collect
from console import CompositeLog, ConsoleLog, Log, SLog
from jmx_builder.parsers.elements.arguments_parser import ArgumentsParser
from jmx_builder.parsers.elements.cache_manager_parser import CacheManagerParser
from jmx_builder.parsers.elements.constant_throughput_timer_parser import ConstantThroughputTimerParser
from jmx_builder.parsers.elements.constant_timer_parser import ConstantTimerParser
from jmx_builder.parsers.elements.cookie_manager_parser import CookieManagerParser
from jmx_builder.parsers.elements.header_manager_parser import HeaderManagerParser
from jmx_builder.parsers.elements.http_sampler_proxy_parser import HTTPSamplerProxyParser
from jmx_builder.parsers.elements.jsr223_parser import JSR223PostProcessorParser, JSR223PreProcessorParser, JSR223SamplerParser
from jmx_builder.parsers.elements.precise_throughput_timer_parser import PreciseThroughputTimerParser
from jmx_builder.parsers.elements.test_action_parser import TestActionParser
from jmx_builder.parsers.elements.uniform_random_timer_parser import UniformRandomTimerParser
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
    <TestPlan guiclass="TestPlanGui" testclass="TestPlan" testname="My Test Plan">
      <boolProp name="TestPlan.tearDown_on_shutdown">true</boolProp>
      <elementProp name="TestPlan.user_defined_variables" elementType="Arguments" guiclass="ArgumentsPanel" testclass="Arguments" testname="User Defined Variables">
        <collectionProp name="Arguments.arguments">
          <elementProp name="host" elementType="Argument">
            <stringProp name="Argument.name">host</stringProp>
            <stringProp name="Argument.value">localhost</stringProp>
            <stringProp name="Argument.metadata">=</stringProp>
          </elementProp>
        </collectionProp>
      </elementProp>
    </TestPlan>
    <hashTree>
      <CookieManager guiclass="CookiePanel" testclass="CookieManager" testname="HTTP Cookie Manager">
        <collectionProp name="CookieManager.cookies">
          <elementProp name="cookie1" elementType="Cookie" testname="cookie1">
            <stringProp name="Cookie.value">123</stringProp>
            <stringProp name="Cookie.domain">domain</stringProp>
            <stringProp name="Cookie.path">/index.html</stringProp>
            <boolProp name="Cookie.secure">true</boolProp>
            <longProp name="Cookie.expires">0</longProp>
            <boolProp name="Cookie.path_specified">true</boolProp>
            <boolProp name="Cookie.domain_specified">true</boolProp>
          </elementProp>
          <elementProp name="cookie2" elementType="Cookie" testname="cookie2">
            <stringProp name="Cookie.value">321</stringProp>
            <stringProp name="Cookie.domain">domain</stringProp>
            <stringProp name="Cookie.path">/path</stringProp>
            <boolProp name="Cookie.secure">false</boolProp>
            <longProp name="Cookie.expires">0</longProp>
            <boolProp name="Cookie.path_specified">true</boolProp>
            <boolProp name="Cookie.domain_specified">true</boolProp>
          </elementProp>
        </collectionProp>
        <boolProp name="CookieManager.clearEachIteration">true</boolProp>
        <boolProp name="CookieManager.controlledByThreadGroup">true</boolProp>
        <stringProp name="CookieManager.policy">best-match</stringProp>
      </CookieManager>
      <hashTree/>
      <CacheManager guiclass="CacheManagerGui" testclass="CacheManager" testname="HTTP Cache Manager" enabled="true">
        <boolProp name="clearEachIteration">false</boolProp>
        <boolProp name="useExpires">false</boolProp>
        <boolProp name="CacheManager.controlledByThread">true</boolProp>
        <intProp name="maxSize">5005</intProp>
      </CacheManager>
      <hashTree/>
      <Arguments guiclass="ArgumentsPanel" testclass="Arguments" testname="User Defined Variables" enabled="true">
        <collectionProp name="Arguments.arguments">
          <elementProp name="var1" elementType="Argument">
            <stringProp name="Argument.name">var1</stringProp>
            <stringProp name="Argument.value">value1</stringProp>
            <stringProp name="Argument.desc">descr1</stringProp>
            <stringProp name="Argument.metadata">=</stringProp>
          </elementProp>
          <elementProp name="var2" elementType="Argument">
            <stringProp name="Argument.name">var2</stringProp>
            <stringProp name="Argument.value">value2</stringProp>
            <stringProp name="Argument.desc">desdcr2</stringProp>
            <stringProp name="Argument.metadata">=</stringProp>
          </elementProp>
        </collectionProp>
      </Arguments>
      <hashTree/>
      <HeaderManager guiclass="HeaderPanel" testclass="HeaderManager" testname="HTTP Header Manager" enabled="true">
        <collectionProp name="HeaderManager.headers">
          <elementProp name="" elementType="Header">
            <stringProp name="Header.name">header</stringProp>
            <stringProp name="Header.value">shoulers</stringProp>
          </elementProp>
          <elementProp name="" elementType="Header">
            <stringProp name="Header.name">header2</stringProp>
            <stringProp name="Header.value">shoulders</stringProp>
          </elementProp>
        </collectionProp>
      </HeaderManager>
      <hashTree/>
      <ThreadGroup guiclass="ThreadGroupGui" testclass="ThreadGroup" testname="Thread Group">
        <intProp name="ThreadGroup.num_threads">1</intProp>
        <intProp name="ThreadGroup.ramp_time">1</intProp>
        <longProp name="ThreadGroup.duration">0</longProp>
        <longProp name="ThreadGroup.delay">0</longProp>
        <boolProp name="ThreadGroup.same_user_on_next_iteration">true</boolProp>
        <stringProp name="ThreadGroup.on_sample_error">stopthread</stringProp>
        <elementProp name="ThreadGroup.main_controller" elementType="LoopController" guiclass="LoopControlPanel" testclass="LoopController" testname="Loop Controller">
          <stringProp name="LoopController.loops">1</stringProp>
          <boolProp name="LoopController.continue_forever">false</boolProp>
        </elementProp>
      </ThreadGroup>
      <hashTree>
        <TransactionController guiclass="TransactionControllerGui" testclass="TransactionController" testname="Transaction Controller">
          <boolProp name="TransactionController.includeTimers">false</boolProp>
        </TransactionController>
        <hashTree>
          <HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="HTTP Request">
            <stringProp name="TestPlan.comments">comment</stringProp>
            <boolProp name="HTTPSampler.image_parser">true</boolProp>
            <boolProp name="HTTPSampler.md5">true</boolProp>
            <stringProp name="HTTPSampler.ipSource">192.168.1.1</stringProp>
            <stringProp name="HTTPSampler.proxyScheme">scheme</stringProp>
            <stringProp name="HTTPSampler.proxyHost">127.0.0.1</stringProp>
            <intProp name="HTTPSampler.proxyPort">8080</intProp>
            <stringProp name="HTTPSampler.proxyUser">proxyusername</stringProp>
            <stringProp name="HTTPSampler.proxyPass">proxypass</stringProp>
            <stringProp name="HTTPSampler.domain">127.0.0.1</stringProp>
            <stringProp name="HTTPSampler.port">80</stringProp>
            <stringProp name="HTTPSampler.protocol">http</stringProp>
            <stringProp name="HTTPSampler.contentEncoding">utf-8</stringProp>
            <stringProp name="HTTPSampler.path">/index.html</stringProp>
            <boolProp name="HTTPSampler.follow_redirects">true</boolProp>
            <stringProp name="HTTPSampler.method">GET</stringProp>
            <boolProp name="HTTPSampler.use_keepalive">true</boolProp>
            <boolProp name="HTTPSampler.DO_MULTIPART_POST">true</boolProp>
            <boolProp name="HTTPSampler.BROWSER_COMPATIBLE_MULTIPART">true</boolProp>
            <boolProp name="HTTPSampler.postBodyRaw">false</boolProp>
            <elementProp name="HTTPsampler.Arguments" elementType="Arguments" guiclass="HTTPArgumentsPanel" testclass="Arguments" testname="User Defined Variables">
              <collectionProp name="Arguments.arguments">
                <elementProp name="username" elementType="HTTPArgument">
                  <boolProp name="HTTPArgument.always_encode">false</boolProp>
                  <stringProp name="Argument.value">admin</stringProp>
                  <stringProp name="Argument.metadata">=</stringProp>
                  <boolProp name="HTTPArgument.use_equals">true</boolProp>
                  <stringProp name="Argument.name">username</stringProp>
                </elementProp>
                <elementProp name="password" elementType="HTTPArgument">
                  <boolProp name="HTTPArgument.always_encode">false</boolProp>
                  <stringProp name="Argument.value">adminpass</stringProp>
                  <stringProp name="Argument.metadata">=</stringProp>
                  <boolProp name="HTTPArgument.use_equals">true</boolProp>
                  <stringProp name="Argument.name">password</stringProp>
                </elementProp>
              </collectionProp>
            </elementProp>
            <intProp name="HTTPSampler.ipSourceType">3</intProp>
            <stringProp name="HTTPSampler.implementation">Java</stringProp>
          </HTTPSamplerProxy>
          <hashTree/>
          <JSR223Sampler guiclass="TestBeanGUI" testclass="JSR223Sampler" testname="JSR223 Sampler">
            <stringProp name="cacheKey">true</stringProp>
            <stringProp name="filename">path/to/file</stringProp>
            <stringProp name="parameters">parameter</stringProp>
            <stringProp name="script">SAMPLER
vars.get(&quot;current_time&quot;)

hello world</stringProp>
            <stringProp name="scriptLanguage">groovy</stringProp>
          </JSR223Sampler>
          <hashTree/>
          <JSR223PreProcessor guiclass="TestBeanGUI" testclass="JSR223PreProcessor" testname="JSR223 PreProcessor">
            <stringProp name="cacheKey">true</stringProp>
            <stringProp name="filename">path/to/file</stringProp>
            <stringProp name="parameters">Params</stringProp>
            <stringProp name="script">PREPROC
vars.get(&quot;current_time&quot;)

hello world</stringProp>
            <stringProp name="scriptLanguage">groovy</stringProp>
          </JSR223PreProcessor>
          <hashTree/>
          <JSR223PostProcessor guiclass="TestBeanGUI" testclass="JSR223PostProcessor" testname="JSR223 PostProcessor">
            <stringProp name="cacheKey">true</stringProp>
            <stringProp name="filename">path/to/file</stringProp>
            <stringProp name="parameters">Params</stringProp>
            <stringProp name="script">POST PROC
vars.get(&quot;current_time&quot;)

hello world</stringProp>
            <stringProp name="scriptLanguage">groovy</stringProp>
          </JSR223PostProcessor>
          <hashTree/>
          <TestAction guiclass="TestActionGui" testclass="TestAction" testname="Think Time">
            <intProp name="ActionProcessor.action">1</intProp>
            <intProp name="ActionProcessor.target">0</intProp>
            <stringProp name="ActionProcessor.duration">0</stringProp>
          </TestAction>
          <hashTree>
            <UniformRandomTimer guiclass="UniformRandomTimerGui" testclass="UniformRandomTimer" testname="Pause">
              <stringProp name="ConstantTimer.delay">1000</stringProp>
              <stringProp name="RandomTimer.range">100</stringProp>
            </UniformRandomTimer>
            <hashTree/>
          </hashTree>
        </hashTree>
      </hashTree>
    </hashTree>
  </hashTree>
</jmeterTestPlan>
'''

parser1: TreeParser = TreeParser()
parser1.register_parser("TestPlan", TestPlanParser)
parser1.register_parser("ThreadGroup", ThreadGroupParser)
parser1.register_parser("TransactionController", TransactionControllerParser)
parser1.register_parser("HTTPSamplerProxy", HTTPSamplerProxyParser)
parser1.register_parser("CookieManager", CookieManagerParser)
parser1.register_parser("CacheManager", CacheManagerParser)
parser1.register_parser("Arguments", ArgumentsParser)
parser1.register_parser("HeaderManager", HeaderManagerParser)
parser1.register_parser("TestAction", TestActionParser)
parser1.register_parser("UniformRandomTimer", UniformRandomTimerParser)
parser1.register_parser("ConstantTimer", ConstantTimerParser)
parser1.register_parser("PreciseThroughputTimer", PreciseThroughputTimerParser)
parser1.register_parser("ConstantThroughputTimer", ConstantThroughputTimerParser)
parser1.register_parser("JSR223Sampler", JSR223SamplerParser)
parser1.register_parser("JSR223PreProcessor", JSR223PreProcessorParser)
parser1.register_parser("JSR223PostProcessor", JSR223PostProcessorParser)

test_plan = parser1.parse(xml)

jsrSampler = test_plan.children[0].children[4].children[0].children[1]
jsrPre = test_plan.children[0].children[4].children[0].children[2]
jsrPost = test_plan.children[0].children[4].children[0].children[3]

jsrSampler.print_info()
jsrPre.print_info()
jsrPost.print_info()


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