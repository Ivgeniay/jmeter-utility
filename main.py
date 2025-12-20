import argparse;
import sys;
import re

from jmeter_runner import run_and_collect
from console import CompositeLog, ConsoleLog, Log, SLog
from scope import extract_scope_by_element_name
from har_parser import parse_har
from jmeter_parser import parse_jmeter
from comparer import SimpleComparer, TransactionComparer



def remove_suffix(
        logger: Log,
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
                    logger.log(f'{testname} -> {new_testname}')
            return result
        
        regex = r'<HTTPSamplerProxy[^>]*testname=\"([^\"]*)\"[^>]*>'

        if scope:
            scope_result = extract_scope_by_element_name(content, scope)
            if not scope_result.found:
                logger.log(f'Element "{scope}" not found')
                return 1
            modified_scope = re.sub(regex, replacer, scope_result.content)
            new_content = content[:scope_result.start_pos] + modified_scope + content[scope_result.end_pos:]
        else:
            new_content = re.sub(regex, replacer, content)

        target_path = output if output else filepath
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        if verbose:
            logger.log(f'Number of modified lines: {change_counter}')


    except Exception as ex:
        logger.log(ex)
        return 1
    

    return 0

def add_methods(
        logger: Log,
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
                logger.log(f'{testname} -> {new_testname}')
            
            return result
        
        regex = r'<HTTPSamplerProxy[^>]*testname="([^"]*)"[^>]*>.*?<stringProp name="HTTPSampler\.method">([^<]*)</stringProp>.*?</HTTPSamplerProxy>'
        if scope:
            scope_result = extract_scope_by_element_name(content, scope)
            if not scope_result.found:
                logger.log(f'Element "{scope}" not found')
                return 1
            modified_scope = re.sub(regex, replacer, scope_result.content, flags=re.DOTALL)
            new_content = content[:scope_result.start_pos] + modified_scope + content[scope_result.end_pos:]
        else:
            new_content = re.sub(regex, replacer, content, flags=re.DOTALL)

        target_path = output if output else filepath
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        if verbose:
            logger.log(f'Number of modified lines: {change_counter}')

    except Exception as ex:
        logger.log(ex)
        return 1
    
    return 0

def compare_traffic(
        logger: Log,
        jmeter_path: str, 
        har_path: str, 
        scope: str | None, 
        difficult: str,
        verbose: bool) -> int:
    try:
        har_requests = parse_har(har_path)
        jmeter_requests = parse_jmeter(jmeter_path, scope)
        
        if difficult == 'simple':
            comparer = SimpleComparer(logger)
        else:
            logger.log(f'There is no {difficult}. Chech --help')
            exit(1)
        
        result = comparer.compare(har_requests, jmeter_requests)
        
        result.print_summary()
        
        if verbose:
            result.print_details()
        
        return 0
    
    except ValueError as ex:
        logger.log(ex)
        return 1
    except Exception as ex:
        logger.log(f'Error: {ex}')
        return 1

def run_and_compare(log: Log, jmeter_path: str, jmx_path: str, har_path: str, difficult: str, verbose: bool) -> int:
    try:
        har_requests = parse_har(har_path)
        if verbose:
            log.log(f'Parsed {len(har_requests)} requests from HAR')

        jmeter_result = run_and_collect(jmeter_path, jmx_path, log)
        if verbose:
            log.log(f'Collected {len(jmeter_result.all_requests)} requests in {len(jmeter_result.transactions)} transactions')

        if difficult == 'simple':
            base_comparer = SimpleComparer(log)
        else:
            log.log(f'Unknown comparison method: {difficult}. Check --help')
            return 1

        if jmeter_result.transactions:
            comparer = TransactionComparer(base_comparer, log)
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
        log.log(f'Error: {ex}')
        return 1
    except Exception as ex:
        log.log(f'Error: {ex}')
        return 1


consLog = ConsoleLog()
logger: CompositeLog = CompositeLog(consLog)
SLog.register_logger(logger)






if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Utilities for Automatic Http Request Processing in JMeter'
    )

    parser.add_argument('-i', '--input', help='Path to jmx file')
    parser.add_argument('-o', '--output', help='Path to output file. By default input file will be overrided')
    parser.add_argument('-v', '--verbose', help='Includes a detailed description of the changes', action='store_true')
    parser.add_argument('-p', '--prefix', help='Removes prefixes that JMeter creates while recording traffic in Http Requsets.', action='store_true')
    parser.add_argument('-m', '--method', help='Adds the method name to the Http Request name (/index.html -> GET /index.html)', action='store_true')
    parser.add_argument('-s', '--scope', help='Name of the element in the tree')
    parser.add_argument('-c', '--compare', help='Path to HAR file for comparison')
    parser.add_argument('-d', '--difficult', help='Comparison method. Available options: [simple]', default='simple')
    parser.add_argument('-r', '--run-compare', help='Run JMeter and compare with HAR. Requires --jmeter-path')
    parser.add_argument('-g', '--jmeter-path', help='Path to JMeter executable (jmeter, jmeter.sh, jmeter.bat)')


    args = parser.parse_args()


    if (args.prefix):
        if not args.input:
            logger.log('Error: --input is required for comparison')
            exit(1)
        remove_suffix(logger, args.input, args.verbose, args.output, args.scope)

    if (args.method):
        if not args.input:
            logger.log('Error: --input is required for comparison')
            exit(1)
        add_methods(logger, args.input, args.verbose, args.output, args.scope)
        exit(0)

    if (args.compare):
        if not args.input:
            logger.log('Error: --input is required for comparison')
            exit(1)
        result = compare_traffic(logger, args.input, args.compare, args.scope, args.difficult, args.verbose)
        exit(result)

    if args.run_compare:
        if not args.input:
            logger.log('Error: --input is required for run-compare')
            exit(1)
        if not args.jmeter_path:
            logger.log('Error: --jmeter-path is required for run-compare')
            exit(1)
        result = run_and_compare(logger, args.jmeter_path, args.input, args.run_compare, args.difficult, args.verbose)
        exit(result)
    

    parser.print_help()