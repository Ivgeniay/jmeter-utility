import argparse;
import sys;
import re
from typing import Callable, Literal

from console import CompositeLog, ConsoleLog, SLog 
from jmx_builder.models.tree import CategoryElement, HTTPSamplerProxy
from jmx_builder.utility.console import print_path, print_paths, print_tree
from jmx_builder.utility.jmx_builder_parser_export import get_configured_parser
from jmx_builder.utility.search import search_element, search_elements
from jmx_builder.parsers.tree_parser import TreeParser 
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


consLog = ConsoleLog()
logger: CompositeLog = CompositeLog(consLog)
SLog.register_logger(logger)

har = parse_har('/opt/Fiddler/fiddler_classic_setup/Capturies/1_browser_1_step_har/S1_1.har')
request = har.log.entries[0].request

xml= '''
'''

# from traffic_builder.jtl_parser.jtl_parser import parse_jtl, get_all_samples

# test_results = parse_jtl('/opt/apache-jmeter-5.6.3/bin/traffic.xml')
# all_samples = get_all_samples(test_results)

# for sample in test_results.http_sample:
#     print(f"{sample.label}: {sample.response_code} ({sample.elapsed}ms)")

# har = convert_jtl_to_har(test_results, include_sub_samples=True)
# save_har(har, '/opt/apache-jmeter-5.6.3/bin/test_traffic.har')


saz = parse_saz('/opt/Fiddler/fiddler_classic_setup/Capturies/1_browser/1.saz')
har = convert_saz_to_har(saz, "JOP")
save_har(har, '/opt/Fiddler/fiddler_classic_setup/Capturies/1_browser/1.har')



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