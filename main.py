import argparse;
import sys;
import re
from typing import Callable, Literal

from payloads.console import CompositeLog, ConsoleLog, SLog 
from jmx_builder.models.tree import Arguments, CategoryElement, HTTPSamplerProxy, HeaderManager, TestAction, TreeElement, UniformRandomTimer
from jmx_builder.utility.console import print_path, print_paths, print_tree
from jmx_builder.utility.jmx_builder_parser_export import get_configured_parser
from jmx_builder.utility.search import search_element, search_elements
from jmx_builder.parsers.tree_parser import TreeParser 
from payloads.har_saz_payloads import SazGroupingMode, add_har_to_scope, add_saz_to_scope
from traffic_analizator.analyzer import TrafficAnalyzer
from traffic_builder.converters_to_har.jtl_to_har_conterter import convert_jtl_to_har, save_har
from traffic_builder.converters_to_har.saz_to_har_converter import convert_saz_to_har
from traffic_builder.har_parsers.har_parser import parse_har
from traffic_builder.saz_parser.saz_parser import parse_saz 


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
        
        parser1: TreeParser = get_configured_parser()
        test_plan = parser1.parse(content)
        
        if scope:
            scope_element = search_element(test_plan, lambda e: e.testname == scope)
            if scope_element:
                samplers: list[HTTPSamplerProxy] = search_elements(scope_element, lambda e: isinstance(e, HTTPSamplerProxy))
                for el in samplers:
                    change_counter = change_counter + 1
                    el.testname = remove_jmeter_suffix(el.testname)
            else:
                SLog.log(f'Element "{scope}" not found')
                return 1
        else:
            samplers: list[HTTPSamplerProxy] = search_elements(test_plan, lambda e: isinstance(e, HTTPSamplerProxy))
            for el in samplers:
                change_counter = change_counter + 1
                el.testname = remove_jmeter_suffix(el.testname)

        new_content = test_plan.to_xml()
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
        
        def replacer(match: HTTPSamplerProxy) -> None:
            nonlocal change_counter
            
            if match.testname.startswith(match.method.value + ' '):
                return
            
            old_testname = match.method.value
            new_testname = f'{match.method.value} {match.testname}'
            match.testname = new_testname
            change_counter = change_counter + 1

            if verbose:
                SLog.log(f'{old_testname} -> {new_testname}')
        
        parser1: TreeParser = get_configured_parser()
        test_plan = parser1.parse(content)
        
        if scope:
            scope_element = search_element(test_plan, lambda e: e.testname == scope)
            if scope_element:
                samplers: list[HTTPSamplerProxy] = search_elements(scope_element, lambda e: isinstance(e, HTTPSamplerProxy))
                for el in samplers:
                    replacer(el)
            else:
                SLog.log(f'Element "{scope}" not found')
                return 1
        else:
            samplers: list[HTTPSamplerProxy] = search_elements(test_plan, lambda e: isinstance(e, HTTPSamplerProxy))
            for el in samplers:
                replacer(el)

        new_content = test_plan.to_xml()

        target_path = output if output else filepath
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        if verbose:
            SLog.log(f'Number of modified lines: {change_counter}')

    except Exception as ex:
        SLog.log(ex)
        return 1
    
    return 0

def har_injection(        
        file_path: str, 
        verbose: bool, 
        output: str | None, 
        scope: str | None,
        har_path: str
        ) -> int:
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            xml = f.read()
        
        parser1: TreeParser = get_configured_parser()
        test_plan = parser1.parse(xml)
        scope_e = search_element(test_plan, lambda e: e.testname == scope)
        if not scope_e:
            SLog.log(f"There is no element {scope}")
            exit(1)
        har = parse_har(har_path)
        add_har_to_scope(scope_e, har)
        new_content = test_plan.to_xml()
        
        out = output if output else file_path
        with open(out, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
    except Exception as ex:
        SLog.log(ex)
        return 1
    
    return 0

def saz_injection(       
        file_path: str, 
        verbose: bool, 
        output: str | None, 
        scope: str | None,
        saz_path: str,
        group_mode: str = SazGroupingMode.BY_UNIQUE_COLORS.value
        ) -> int:
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            xml = f.read()
        
        parser1: TreeParser = get_configured_parser()
        test_plan = parser1.parse(xml)
        scope_e = search_element(test_plan, lambda e: e.testname == scope)
        
        if not scope_e:
            SLog.log(f"There is no element {scope}")
            exit(1)
            
        saz = parse_saz(saz_path)
        add_saz_to_scope(scope_e, saz, group_mode)
        new_content = test_plan.to_xml()
        
        out = output if output else file_path
        with open(out, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
    except Exception as ex:
        SLog.log(ex)
        return 1
    
    return 0

def insert_varible(
        file_path: str, 
        verbose: bool, 
        attribute: str,
        output: str | None, 
        scope: str | None
        ) -> None:
    
    with open(file=file_path, mode = 'r', encoding="utf-8") as f:
        xml = f.read()
        
    parser1: TreeParser = get_configured_parser()
    test_plan = parser1.parse(xml)
    user_vars: Arguments = search_element(test_plan, lambda e: e.category == CategoryElement.CONFIG_ELEMENT and e.testclass == 'Arguments')
    if not user_vars:
        SLog.log('User Defined Variables is not found')
        exit(1)
        
    atrb_value = user_vars.get_variable_value(attribute)
    if not atrb_value:
        SLog.log(f'Var "{attribute}" not defined in User Defined Variables')
        exit(1)
    
    scope_el: TreeElement = None 
    if scope:
        scope_el = search_element(test_plan, lambda e: e.testname == scope)
        if not scope_el:
            SLog.log(f'Not founded {scope}')
            exit(1)
    else:
        scope_el = test_plan
    
    http_req: list[HTTPSamplerProxy] = search_elements(scope_el, lambda e: isinstance(e, HTTPSamplerProxy) and e.get_argument(attribute) is not None)
    headers_: list[HeaderManager] = search_elements(scope_el, lambda e: isinstance(e, HeaderManager) and e.get_header(attribute) is not None)
    
    for el in http_req:
        was_change = False
        arguments_data = el.get_arguments_data()
        for arg in arguments_data:
            if arg.name == attribute:
                old_value = arg.value 
                arg.value = atrb_value
                was_change = True
                SLog.log(f'{el.testname}: {attribute} {old_value} -> {arg.value}')
        if was_change:
            el.set_arguments_data(arguments_data)
            
    for h in headers_:
        was_change = False
        headers_data = h.get_headers_data()
        for data in headers_data:
            if data.name == attribute:
                old_value = data.value
                data.value = atrb_value
                was_change = True
                SLog.log(f'{h.testname}: {attribute} {old_value} -> {data.value}')
        if was_change:
            h.set_headers_data(headers_data)
    
    new_content = test_plan.to_xml()
    out = output if output else file_path
    with open(out, 'w', encoding='utf-8') as f:
        f.write(new_content)

def find_disabled(
    file_path: str, 
    verbose: bool,  
    scope: str | None
) -> None:
    with open(file=file_path, mode = 'r', encoding="utf-8") as f:
        xml = f.read()
        
    parser1: TreeParser = get_configured_parser()
    test_plan = parser1.parse(xml)
    
    scope_el: TreeElement = None 
    if scope:
        scope_el = search_element(test_plan, lambda e: e.testname == scope)
        if not scope_el:
            SLog.log(f'Not founded {scope}')
    else:
        scope_el = test_plan
    
    disabled_el : list[TreeElement] = search_elements(scope_el, lambda e: e.enabled == False, True)
    SLog.log(f"Disabled list:")
    for e in disabled_el:
        SLog.log(print_path(test_plan, e))

def enable_all_timers(
    file_path: str, 
    verbose: bool,  
    output: str | None, 
    scope: str | None
) -> None:
    
    with open(file=file_path, mode = 'r', encoding="utf-8") as f:
        xml = f.read()
        
    parser1: TreeParser = get_configured_parser()
    test_plan = parser1.parse(xml)
    
    scope_el: TreeElement = None 
    if scope:
        scope_el = search_element(test_plan, lambda e: e.testname == scope)
        if not scope_el:
            SLog.log(f'Not founded {scope}')
    else:
        scope_el = test_plan
    
    timers: list[TreeElement] = search_elements(scope_el, lambda e: e.category == CategoryElement.TIMER)
    for timer in timers:
        bread_crumbs = print_path(test_plan, timer).split(" -> ")
        for crumb in bread_crumbs:
            el = search_element(test_plan, predicate= lambda e: e.testname == crumb)
            if el:
                el.enabled = True
    
    new_content = test_plan.to_xml()
    out = output if output else file_path
    with open(out, 'w', encoding='utf-8') as f:
        f.write(new_content)



consLog = ConsoleLog()
logger: CompositeLog = CompositeLog(consLog)
SLog.register_logger(logger)

# enable_all_timers(
#     file_path='/opt/apache-jmeter-5.6.3/bin/TEST22_TEST.jmx',
#     verbose=True,
#     output='/opt/apache-jmeter-5.6.3/bin/TEST22_TEST.jmx',
#     scope='Regular User2'
# )

# insert_varible(
#     file_path='/opt/apache-jmeter-5.6.3/bin/TEST22_TEST.jmx',
#     verbose=True,
#     attribute='requesttoken',
#     output='/opt/apache-jmeter-5.6.3/bin/TEST22_TEST2.jmx',
#     scope='Regular User2'
# )

har = parse_har('/opt/Fiddler/fiddler_classic_setup/Capturies/1_browser_1_step_har/S1_3.har')
analyzer : TrafficAnalyzer = TrafficAnalyzer(ignore_cookies=True)
result = analyzer.analyze(har)
report = result.to_str()
path = './test.log'
with open(path, mode='w', encoding="utf-8") as f:
    f.write(report)
SLog.log(f'Report was saved in {path}')
# request = har.log.entries[0].request

# xml= '''<?xml version="1.0" encoding="UTF-8"?>
# <jmeterTestPlan version="1.2" properties="5.0" jmeter="5.6.3">
#   <hashTree>
#     <TestPlan guiclass="TestPlanGui" testclass="TestPlan" testname="Test Plan">
#       <boolProp name="TestPlan.tearDown_on_shutdown">true</boolProp>
#       <elementProp name="TestPlan.user_defined_variables" elementType="Arguments" guiclass="ArgumentsPanel" testclass="Arguments" testname="User Defined Variables">
#         <collectionProp name="Arguments.arguments"/>
#       </elementProp>
#     </TestPlan>
#     <hashTree>
#       <ThreadGroup guiclass="ThreadGroupGui" testclass="ThreadGroup" testname="Regural User">
#         <intProp name="ThreadGroup.num_threads">1</intProp>
#         <intProp name="ThreadGroup.ramp_time">1</intProp>
#         <longProp name="ThreadGroup.duration">0</longProp>
#         <longProp name="ThreadGroup.delay">0</longProp>
#         <boolProp name="ThreadGroup.same_user_on_next_iteration">false</boolProp>
#         <stringProp name="ThreadGroup.on_sample_error">continue</stringProp>
#         <elementProp name="ThreadGroup.main_controller" elementType="LoopController" guiclass="LoopControlPanel" testclass="LoopController" testname="Loop Controller">
#           <stringProp name="LoopController.loops">1</stringProp>
#           <boolProp name="LoopController.continue_forever">false</boolProp>
#         </elementProp>
#       </ThreadGroup>
#       <hashTree>
#         <TransactionController guiclass="TransactionControllerGui" testclass="TransactionController" testname="Recordt">
#           <boolProp name="TransactionController.includeTimers">false</boolProp>
#         </TransactionController>
#         <hashTree/>
#       </hashTree>
#     </hashTree>
#   </hashTree>
# </jmeterTestPlan>'''

# from traffic_builder.jtl_parser.jtl_parser import parse_jtl, get_all_samples

# test_results = parse_jtl('/opt/apache-jmeter-5.6.3/bin/traffic.xml')
# all_samples = get_all_samples(test_results)

# for sample in test_results.http_sample:
#     print(f"{sample.label}: {sample.response_code} ({sample.elapsed}ms)")

# har = convert_jtl_to_har(test_results, include_sub_samples=True)
# save_har(har, '/opt/apache-jmeter-5.6.3/bin/test_traffic.har')


# saz = parse_saz('/opt/Fiddler/fiddler_classic_setup/Capturies/1_browser/1.saz')
# har = convert_saz_to_har(saz, "JOP")
# save_har(har, '/opt/Fiddler/fiddler_classic_setup/Capturies/1_browser/1.har')



# parser1: TreeParser = get_configured_parser()
# test_plan = parser1.parse(xml)

# for child in test_plan.children[0].children:
#     child.print_info()

# target = test_plan, test_plan.children[0].children[5].children[0].children[0].children[5]
# path = print_path(test_plan, target[1])
# SLog.log(path)

# paths = print_paths(test_plan, lambda e: isinstance(e, HTTPSamplerProxy))
# for i in paths:
#     SLog.log(i)
    
# samplers: list[HTTPSamplerProxy] = search_elements(test_plan, lambda e: isinstance(e, HTTPSamplerProxy))
# for sample in samplers:
#     sample.print_info()


# res = test_plan.to_xml()
# SLog.log("=============================================")
# SLog.log(res)
# SLog.log("=============================================")



def consent_overwrite_file() -> Literal['y', 'n']:
    msg = "You did not specify the path to the output file (the -o option is used). Without this parameter, the current file will be overwritten. Do you agree to re-record? (y/n)"
    user_answer: str = ""
    while user_answer not in ('y', 'n'):
        user_answer = input(msg).lower().strip()
    return user_answer

def validating_overiting(o: str | None, function: Callable[[], None]) -> None:
    if not o:
        user_answer = consent_overwrite_file()
        if user_answer == 'n':
            exit(0)
        else:
            function()

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
        validating_overiting(args.output, lambda: remove_suffix(args.input, args.verbose, args.output, args.scope))
        exit(0)

    if (args.method):
        if not args.input:
            SLog.log('Error: --input is required for comparison')
            exit(1)
        validating_overiting(args.output, lambda: add_methods(args.input, args.verbose, args.output, args.scope))
        exit(0)

    if (args.compare):
        if not args.input:
            SLog.log('Error: --input is required for comparison')
            exit(1)
        #result = compare_traffic(args.input, args.compare, args.scope, args.difficult, args.verbose)
        exit(0)

    if args.run_compare:
        if not args.input:
            SLog.log('Error: --input is required for run-compare')
            exit(1)
        if not args.jmeter_path:
            SLog.log('Error: --jmeter-path is required for run-compare')
            exit(1)
        #result = run_and_compare(args.jmeter_path, args.input, args.run_compare, args.difficult, args.verbose)
        exit(0)
    

    args_parser.print_help()