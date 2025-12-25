from jmx_builder.models.tree import HTTPSamplerProxy, HeaderManager, TransactionController, TreeElement
from traffic_builder.converters_to_har.saz_to_har_converter import convert_saz_to_har
from traffic_builder.har_parsers.pydantic_models import Entry, HarFile
from traffic_builder.saz_parser.models import SazArchive
from urllib.parse import urlparse
from enum import Enum



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


class SazGroupingMode(Enum):
    NO_GROUPING = "no_grouping"
    BY_UNIQUE_COLORS = "by_unique_colors"
    BY_COLOR_CHANGE = "by_color_change"


def add_saz_to_scope(
    root: TreeElement,
    saz_archive: SazArchive,
    grouping_mode: SazGroupingMode = SazGroupingMode.NO_GROUPING
) -> None:
    har_file = convert_saz_to_har(saz_archive)
    
    if grouping_mode == SazGroupingMode.NO_GROUPING:
        add_har_to_scope(root, har_file)
        return
    
    color_map = {}
    for i, session in enumerate(saz_archive.sessions):
        color = None
        for flag in session.metadata.flags:
            if flag.name == "ui-color":
                color = flag.value
                break
        color_map[i] = color
    
    if grouping_mode == SazGroupingMode.BY_UNIQUE_COLORS:
        _add_saz_by_unique_colors(root, har_file, color_map)
    elif grouping_mode == SazGroupingMode.BY_COLOR_CHANGE:
        _add_saz_by_color_change(root, har_file, color_map)


def _add_saz_by_unique_colors(root: TreeElement, har_file: HarFile, color_map: dict) -> None:
    color_groups = {}
    
    for i, entry in enumerate(har_file.log.entries):
        color = color_map.get(i)
        if color not in color_groups:
            color_groups[color] = []
        color_groups[color].append(entry)
    
    for color, entries in color_groups.items():
        if color is None:
            tc_name = "No Color"
        else:
            tc_name = f"{color} Requests"
        
        tc = TransactionController.create_default(tc_name)
        
        for entry in entries:
            http_sampler = create_http_sampler_from_har(entry)
            header_manager = create_header_manager_from_har(entry)
            http_sampler.add_child(header_manager)
            tc.add_child(http_sampler)
        
        root.add_child(tc)


def _add_saz_by_color_change(root: TreeElement, har_file: HarFile, color_map: dict) -> None:
    if not har_file.log.entries:
        return
    
    current_color = color_map.get(0)
    tc_counter = 1
    
    if current_color is None:
        tc_name = f"Transaction Controller {tc_counter} (No Color)"
    else:
        tc_name = f"Transaction Controller {tc_counter} ({current_color})"
    
    tc = TransactionController.create_default(tc_name)
    
    for i, entry in enumerate(har_file.log.entries):
        color = color_map.get(i)
        
        if color != current_color:
            root.add_child(tc)
            
            tc_counter += 1
            current_color = color
            
            if current_color is None:
                tc_name = f"Transaction Controller {tc_counter} (No Color)"
            else:
                tc_name = f"Transaction Controller {tc_counter} ({current_color})"
            
            tc = TransactionController.create_default(tc_name)
        
        http_sampler = create_http_sampler_from_har(entry)
        header_manager = create_header_manager_from_har(entry)
        http_sampler.add_child(header_manager)
        tc.add_child(http_sampler)
    
    root.add_child(tc)