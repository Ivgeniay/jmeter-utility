from jmx_builder.models.tree import HTTPSamplerProxy, HeaderManager, TreeElement
from traffic_builder.har_parsers.pydantic_models import Entry, HarFile
from urllib.parse import urlparse


def create_header_manager_from_har(har_entry: Entry) -> HeaderManager:
    header_manager = HeaderManager.create_default()
    
    for header in har_entry.request.headers:
        header_manager.add_header(header.name, header.value)
    
    return header_manager


def create_http_sampler_from_har(har_entry: Entry) -> HTTPSamplerProxy:
    request = har_entry.request
    parsed_url = urlparse(request.url)
    
    protocol = parsed_url.scheme
    domain = parsed_url.hostname or ""
    port = parsed_url.port or ""
    path = parsed_url.path or "/"
    
    testname = f"{request.method} {path}"
    
    sampler = HTTPSamplerProxy.create_default(testname=testname)
    sampler.set_protocol(protocol)
    sampler.set_domain(domain)
    sampler.set_port(port)
    sampler.set_path(path)
    sampler.set_method_raw(request.method)
    
    if request.query_string:
        for query_param in request.query_string:
            sampler.add_argument(query_param.name, query_param.value)
    
    if request.post_data:
        if request.post_data.params:
            for param in request.post_data.params:
                sampler.add_argument(param.name, param.value)
        elif request.post_data.text:
            sampler.set_body_data(request.post_data.text)
    
    return sampler

def add_har_to_scope(root: TreeElement, har_file: HarFile) -> None:
    for entry in har_file.log.entries:
        http_sampler = create_http_sampler_from_har(entry)
        header_manager = create_header_manager_from_har(entry)
        
        http_sampler.add_child(header_manager)
        root.add_child(http_sampler)
        
