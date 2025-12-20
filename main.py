import argparse;
import sys;
import re

from jmeter_runner import run_and_collect
from console import CompositeLog, ConsoleLog, Log, SLog
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
      <ThreadGroup guiclass="ThreadGroupGui" testclass="ThreadGroup" testname="Thread Group">
        <intProp name="ThreadGroup.num_threads">1</intProp>
        <intProp name="ThreadGroup.ramp_time">1</intProp>
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
        <hashTree/>
      </hashTree>
    </hashTree>
  </hashTree>
</jmeterTestPlan>'''

parser1: TreeParser = TreeParser()
parser1.register_parser("TestPlan", TestPlanParser)
parser1.register_parser("ThreadGroup", ThreadGroupParser)
parser1.register_parser("TransactionController", TransactionControllerParser)

test_plan = parser1.parse(xml)
res = test_plan.to_xml()
SLog.log(res)




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