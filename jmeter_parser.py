import re
from models import Request, Record, PostData
from scope import extract_scope_by_element_name


def parse_jmeter(filepath: str, scope: str | None = None) -> list[Request]:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if scope:
        scope_result = extract_scope_by_element_name(content, scope)
        if not scope_result.found:
            raise ValueError(f'Element "{scope}" not found')
        content = scope_result.content
    
    requests = []
    
    sampler_regex = r'<HTTPSamplerProxy[^>]*>.*?</HTTPSamplerProxy>'
    samplers = re.findall(sampler_regex, content, flags=re.DOTALL)
    
    for sampler in samplers:
        request = parse_sampler(sampler)
        if request:
            requests.append(request)
    
    return requests


def parse_sampler(sampler: str) -> Request | None:
    method = extract_prop(sampler, 'HTTPSampler.method')
    path = extract_prop(sampler, 'HTTPSampler.path')
    
    if not method or not path:
        return None
    
    query_string = parse_arguments(sampler)
    headers = parse_headers(sampler)
    post_data = parse_post_data(sampler)
    
    return Request(
        method=method,
        url=path,
        query_string=query_string,
        headers=headers,
        post_data=post_data
    )


def extract_prop(content: str, prop_name: str) -> str:
    regex = rf'<stringProp name="{prop_name}">([^<]*)</stringProp>'
    match = re.search(regex, content)
    return match.group(1) if match else ''


def parse_arguments(sampler: str) -> list[Record]:
    arguments = []
    
    args_block_regex = r'<elementProp name="HTTPsampler\.Arguments"[^>]*>.*?</elementProp>'
    args_block_match = re.search(args_block_regex, sampler, flags=re.DOTALL)
    
    if not args_block_match:
        return arguments
    
    args_block = args_block_match.group(0)
    
    arg_regex = r'<elementProp name="([^"]*)" elementType="HTTPArgument">.*?</elementProp>'
    arg_matches = re.findall(arg_regex, args_block, flags=re.DOTALL)
    
    for arg_match in re.finditer(arg_regex, args_block, flags=re.DOTALL):
        arg_content = arg_match.group(0)
        name = extract_prop(arg_content, 'Argument.name')
        value = extract_prop(arg_content, 'Argument.value')
        arguments.append(Record(name=name, value=value))
    
    return arguments


def parse_headers(sampler: str) -> list[Record]:
    # TODO: реализовать если нужно
    return []


def parse_post_data(sampler: str) -> PostData | None:
    is_raw = extract_bool_prop(sampler, 'HTTPSampler.postBodyRaw')
    
    if not is_raw:
        return None
    
    args_block_regex = r'<elementProp name="HTTPsampler\.Arguments"[^>]*>.*?</elementProp>'
    args_block_match = re.search(args_block_regex, sampler, flags=re.DOTALL)
    
    if not args_block_match:
        return None
    
    body = extract_prop(args_block_match.group(0), 'Argument.value')
    
    if body:
        return PostData(mime_type='', text=body)
    
    return None


def extract_bool_prop(content: str, prop_name: str) -> bool:
    regex = rf'<boolProp name="{prop_name}">([^<]*)</boolProp>'
    match = re.search(regex, content)
    return match.group(1).lower() == 'true' if match else False