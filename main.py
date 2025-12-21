import argparse;
import sys;
import re

from jmeter_runner import run_and_collect
from console import CompositeLog, ConsoleLog, SLog
from jmx_builder_parser_export import get_configured_parser
from scope import extract_scope_by_element_name
from har_builder.parsers.har_parser import parse_har
from jmeter_parser import parse_jmeter
from comparer import SimpleComparer, TransactionComparer
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
      <DebugSampler guiclass="TestBeanGUI" testclass="DebugSampler" testname="Debug Sampler">
        <boolProp name="displayJMeterProperties">true</boolProp>
        <boolProp name="displayJMeterVariables">false</boolProp>
        <boolProp name="displaySystemProperties">true</boolProp>
      </DebugSampler>
      <hashTree/>
      <JSR223PostProcessor guiclass="TestBeanGUI" testclass="JSR223PostProcessor" testname="JSR223 PostProcessor">
        <stringProp name="cacheKey">true</stringProp>
        <stringProp name="filename">path/to/file</stringProp>
        <stringProp name="parameters">Params</stringProp>
        <stringProp name="script">vars.get("test")</stringProp>
        <stringProp name="scriptLanguage">groovy</stringProp>
      </JSR223PostProcessor>
      <hashTree/>
      <RegexExtractor guiclass="RegexExtractorGui" testclass="RegexExtractor" testname="Regular Expression Extractor">
        <stringProp name="RegexExtractor.useHeaders">false</stringProp>
        <stringProp name="RegexExtractor.refname">var</stringProp>
        <stringProp name="RegexExtractor.regex">.*</stringProp>
        <stringProp name="RegexExtractor.template">$1$</stringProp>
        <stringProp name="RegexExtractor.default">NO_VALUE</stringProp>
        <boolProp name="RegexExtractor.default_empty_value">false</boolProp>
        <stringProp name="RegexExtractor.match_number">0</stringProp>
        <stringProp name="Sample.scope">all</stringProp>
      </RegexExtractor>
      <hashTree/>
      <JSONPostProcessor guiclass="JSONPostProcessorGui" testclass="JSONPostProcessor" testname="JSON Extractor">
        <stringProp name="JSONPostProcessor.referenceNames">jsonVar</stringProp>
        <stringProp name="JSONPostProcessor.jsonPathExprs">$.person.name</stringProp>
        <stringProp name="JSONPostProcessor.match_numbers">0</stringProp>
        <stringProp name="Sample.scope">all</stringProp>
        <stringProp name="JSONPostProcessor.defaultValues">NO_VALUE</stringProp>
        <boolProp name="JSONPostProcessor.compute_concat">true</boolProp>
      </JSONPostProcessor>
      <hashTree/>
      <HtmlExtractor guiclass="HtmlExtractorGui" testclass="HtmlExtractor" testname="CSS Selector Extractor">
        <stringProp name="HtmlExtractor.refname">cssVar</stringProp>
        <stringProp name="HtmlExtractor.expr">div.class</stringProp>
        <stringProp name="HtmlExtractor.attribute">href</stringProp>
        <stringProp name="HtmlExtractor.default">NO_VALUE</stringProp>
        <boolProp name="HtmlExtractor.default_empty_value">false</boolProp>
        <stringProp name="HtmlExtractor.match_number">0</stringProp>
        <stringProp name="HtmlExtractor.extractor_impl">JSOUP</stringProp>
        <stringProp name="Sample.scope">all</stringProp>
      </HtmlExtractor>
      <hashTree/>
      <BoundaryExtractor guiclass="BoundaryExtractorGui" testclass="BoundaryExtractor" testname="Boundary Extractor">
        <stringProp name="BoundaryExtractor.useHeaders">true</stringProp>
        <stringProp name="BoundaryExtractor.refname">boundVar</stringProp>
        <stringProp name="BoundaryExtractor.lboundary">Left</stringProp>
        <stringProp name="BoundaryExtractor.rboundary">Right</stringProp>
        <stringProp name="BoundaryExtractor.default">NO_VALUE</stringProp>
        <boolProp name="BoundaryExtractor.default_empty_value">false</boolProp>
        <stringProp name="BoundaryExtractor.match_number">0</stringProp>
        <stringProp name="Sample.scope">all</stringProp>
      </BoundaryExtractor>
      <hashTree/>
      <JMESPathExtractor guiclass="JMESPathExtractorGui" testclass="JMESPathExtractor" testname="JSON JMESPath Extractor">
        <stringProp name="JMESExtractor.referenceName">jmesVar</stringProp>
        <stringProp name="JMESExtractor.jmesPathExpr">person.name</stringProp>
        <stringProp name="JMESExtractor.matchNumber">1</stringProp>
        <stringProp name="Sample.scope">all</stringProp>
        <stringProp name="JMESExtractor.defaultValue">NO_VALUE</stringProp>
      </JMESPathExtractor>
      <hashTree/>
      <DebugPostProcessor guiclass="TestBeanGUI" testclass="DebugPostProcessor" testname="Debug PostProcessor">
        <boolProp name="displayJMeterProperties">true</boolProp>
        <boolProp name="displayJMeterVariables">false</boolProp>
        <boolProp name="displaySamplerProperties">false</boolProp>
        <boolProp name="displaySystemProperties">true</boolProp>
      </DebugPostProcessor>
      <hashTree/>
      <ResultAction guiclass="ResultActionGui" testclass="ResultAction" testname="Result Status Action Handler">
        <intProp name="OnError.action">4</intProp>
      </ResultAction>
      <hashTree/>
      <XPathExtractor guiclass="XPathExtractorGui" testclass="XPathExtractor" testname="XPath Extractor">
        <stringProp name="XPathExtractor.default">NO_VALUE</stringProp>
        <stringProp name="XPathExtractor.refname">xpathVar</stringProp>
        <stringProp name="XPathExtractor.matchNumber">0</stringProp>
        <stringProp name="XPathExtractor.xpathQuery">//div</stringProp>
        <boolProp name="XPathExtractor.validate">true</boolProp>
        <boolProp name="XPathExtractor.tolerant">true</boolProp>
        <boolProp name="XPathExtractor.namespace">true</boolProp>
        <stringProp name="Sample.scope">all</stringProp>
        <boolProp name="XPathExtractor.fragment">true</boolProp>
      </XPathExtractor>
      <hashTree/>
      <XPath2Extractor guiclass="XPath2ExtractorGui" testclass="XPath2Extractor" testname="XPath2 Extractor">
        <stringProp name="XPathExtractor2.default">NO_VALUE</stringProp>
        <stringProp name="XPathExtractor2.refname">xpath2Var</stringProp>
        <stringProp name="XPathExtractor2.matchNumber">1</stringProp>
        <stringProp name="XPathExtractor2.xpathQuery">//span</stringProp>
        <stringProp name="XPathExtractor2.namespaces">ns=http://example.com</stringProp>
        <stringProp name="Sample.scope">all</stringProp>
        <boolProp name="XPathExtractor2.fragment">true</boolProp>
      </XPath2Extractor>
      <hashTree/>
      <ResultCollector guiclass="ViewResultsFullVisualizer" testclass="ResultCollector" testname="View Results Tree">
        <boolProp name="ResultCollector.error_logging">false</boolProp>
        <objProp>
          <name>saveConfig</name>
          <value class="SampleSaveConfiguration">
            <time>true</time>
            <latency>true</latency>
            <timestamp>true</timestamp>
            <success>true</success>
            <label>true</label>
            <code>true</code>
            <message>true</message>
            <threadName>true</threadName>
            <dataType>true</dataType>
            <encoding>false</encoding>
            <assertions>true</assertions>
            <subresults>true</subresults>
            <responseData>false</responseData>
            <samplerData>false</samplerData>
            <xml>false</xml>
            <fieldNames>true</fieldNames>
            <responseHeaders>false</responseHeaders>
            <requestHeaders>false</requestHeaders>
            <responseDataOnError>false</responseDataOnError>
            <saveAssertionResultsFailureMessage>true</saveAssertionResultsFailureMessage>
            <assertionsResultsToSave>0</assertionsResultsToSave>
            <bytes>true</bytes>
            <sentBytes>true</sentBytes>
            <url>true</url>
            <threadCounts>true</threadCounts>
            <idleTime>true</idleTime>
            <connectTime>true</connectTime>
          </value>
        </objProp>
        <stringProp name="filename">results.jtl</stringProp>
        <boolProp name="ResultCollector.success_only_logging">true</boolProp>
      </ResultCollector>
      <hashTree/>
      <ResultCollector guiclass="SummaryReport" testclass="ResultCollector" testname="Summary Report">
        <boolProp name="ResultCollector.error_logging">true</boolProp>
        <objProp>
          <name>saveConfig</name>
          <value class="SampleSaveConfiguration">
            <time>true</time>
            <latency>true</latency>
            <timestamp>true</timestamp>
            <success>true</success>
            <label>true</label>
            <code>true</code>
            <message>true</message>
            <threadName>true</threadName>
            <dataType>true</dataType>
            <encoding>true</encoding>
            <assertions>true</assertions>
            <subresults>true</subresults>
            <responseData>true</responseData>
            <samplerData>true</samplerData>
            <xml>true</xml>
            <fieldNames>true</fieldNames>
            <responseHeaders>true</responseHeaders>
            <requestHeaders>true</requestHeaders>
            <responseDataOnError>false</responseDataOnError>
            <saveAssertionResultsFailureMessage>true</saveAssertionResultsFailureMessage>
            <assertionsResultsToSave>0</assertionsResultsToSave>
            <bytes>true</bytes>
            <sentBytes>true</sentBytes>
            <url>true</url>
            <fileName>true</fileName>
            <hostname>true</hostname>
            <threadCounts>true</threadCounts>
            <sampleCount>true</sampleCount>
            <idleTime>true</idleTime>
            <connectTime>true</connectTime>
          </value>
        </objProp>
        <stringProp name="filename">summary.csv</stringProp>
        <boolProp name="useGroupName">true</boolProp>
      </ResultCollector>
      <hashTree/>
      <ResultCollector guiclass="StatVisualizer" testclass="ResultCollector" testname="Aggregate Report">
        <boolProp name="ResultCollector.error_logging">false</boolProp>
        <objProp>
          <name>saveConfig</name>
          <value class="SampleSaveConfiguration">
            <time>true</time>
            <latency>true</latency>
            <timestamp>true</timestamp>
            <success>true</success>
            <label>true</label>
            <code>true</code>
            <message>true</message>
            <threadName>true</threadName>
            <dataType>true</dataType>
            <encoding>false</encoding>
            <assertions>true</assertions>
            <subresults>true</subresults>
            <responseData>false</responseData>
            <samplerData>false</samplerData>
            <xml>false</xml>
            <fieldNames>true</fieldNames>
            <responseHeaders>false</responseHeaders>
            <requestHeaders>false</requestHeaders>
            <responseDataOnError>false</responseDataOnError>
            <saveAssertionResultsFailureMessage>true</saveAssertionResultsFailureMessage>
            <assertionsResultsToSave>0</assertionsResultsToSave>
            <bytes>true</bytes>
            <sentBytes>true</sentBytes>
            <url>true</url>
            <threadCounts>true</threadCounts>
            <idleTime>true</idleTime>
            <connectTime>true</connectTime>
          </value>
        </objProp>
        <stringProp name="filename">aggregate.csv</stringProp>
        <boolProp name="useGroupName">true</boolProp>
      </ResultCollector>
      <hashTree/>
      <ResultCollector guiclass="SimpleDataWriter" testclass="ResultCollector" testname="Simple Data Writer">
        <boolProp name="ResultCollector.error_logging">false</boolProp>
        <objProp>
          <name>saveConfig</name>
          <value class="SampleSaveConfiguration">
            <time>true</time>
            <latency>true</latency>
            <timestamp>true</timestamp>
            <success>true</success>
            <label>true</label>
            <code>true</code>
            <message>true</message>
            <threadName>true</threadName>
            <dataType>true</dataType>
            <encoding>false</encoding>
            <assertions>true</assertions>
            <subresults>true</subresults>
            <responseData>false</responseData>
            <samplerData>false</samplerData>
            <xml>false</xml>
            <fieldNames>true</fieldNames>
            <responseHeaders>false</responseHeaders>
            <requestHeaders>false</requestHeaders>
            <responseDataOnError>false</responseDataOnError>
            <saveAssertionResultsFailureMessage>true</saveAssertionResultsFailureMessage>
            <assertionsResultsToSave>0</assertionsResultsToSave>
            <bytes>true</bytes>
            <sentBytes>true</sentBytes>
            <url>true</url>
            <threadCounts>true</threadCounts>
            <idleTime>true</idleTime>
            <connectTime>true</connectTime>
          </value>
        </objProp>
        <stringProp name="filename">data.csv</stringProp>
      </ResultCollector>
      <hashTree/>
      <BackendListener guiclass="BackendListenerGui" testclass="BackendListener" testname="Backend Listener">
        <elementProp name="arguments" elementType="Arguments" guiclass="ArgumentsPanel" testclass="Arguments">
          <collectionProp name="Arguments.arguments">
            <elementProp name="graphiteMetricsSender" elementType="Argument">
              <stringProp name="Argument.name">graphiteMetricsSender</stringProp>
              <stringProp name="Argument.value">org.apache.jmeter.visualizers.backend.graphite.TextGraphiteMetricsSender</stringProp>
              <stringProp name="Argument.metadata">=</stringProp>
            </elementProp>
            <elementProp name="graphiteHost" elementType="Argument">
              <stringProp name="Argument.name">graphiteHost</stringProp>
              <stringProp name="Argument.value">localhost</stringProp>
              <stringProp name="Argument.metadata">=</stringProp>
            </elementProp>
            <elementProp name="graphitePort" elementType="Argument">
              <stringProp name="Argument.name">graphitePort</stringProp>
              <stringProp name="Argument.value">2003</stringProp>
              <stringProp name="Argument.metadata">=</stringProp>
            </elementProp>
          </collectionProp>
        </elementProp>
        <stringProp name="classname">org.apache.jmeter.visualizers.backend.graphite.GraphiteBackendListenerClient</stringProp>
        <stringProp name="QUEUE_SIZE">5000</stringProp>
      </BackendListener>
      <hashTree/>
    </hashTree>
  </hashTree>
</jmeterTestPlan>'''


parser1: TreeParser = get_configured_parser()
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