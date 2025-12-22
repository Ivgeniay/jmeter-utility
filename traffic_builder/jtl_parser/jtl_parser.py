import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from traffic_builder.jtl_parser.models import TestResults, HttpSample, AssertionResult


def _parse_http_sample(element: ET.Element) -> HttpSample:
    data = dict(element.attrib)
    
    for child in element:
        tag = child.tag
        
        if tag == "httpSample":
            if "httpSample" not in data:
                data["httpSample"] = []
            data["httpSample"].append(_parse_http_sample(child))
        
        elif tag == "assertionResult":
            if "assertionResult" not in data:
                data["assertionResult"] = []
            assertion_data = dict(child.attrib)
            for assertion_child in child:
                assertion_data[assertion_child.tag] = assertion_child.text or ""
            data["assertionResult"].append(assertion_data)
        
        else:
            text_value = child.text or ""
            data[tag] = text_value
    
    return HttpSample.model_validate(data)


def _parse_assertion_result(element: ET.Element) -> AssertionResult:
    data = dict(element.attrib)
    
    for child in element:
        data[child.tag] = child.text or ""
    
    return AssertionResult.model_validate(data)


def parse_jtl(filepath: str | Path) -> TestResults:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    content = re.sub(r'<responseData[^>]*>.*?</responseData>', 
                     '<responseData class="java.lang.String"></responseData>', 
                     content, flags=re.DOTALL)
    
    root = ET.fromstring(content)
    
    data = {
        "version": root.attrib.get("version", "1.2"),
        "httpSample": []
    }
    
    for child in root:
        if child.tag == "httpSample":
            data["httpSample"].append(_parse_http_sample(child))
    
    return TestResults.model_validate(data)


def parse_jtl_from_string(content: str) -> TestResults:
    root = ET.fromstring(content)
    
    data = {
        "version": root.attrib.get("version", "1.2"),
        "httpSample": []
    }
    
    for child in root:
        if child.tag == "httpSample":
            data["httpSample"].append(_parse_http_sample(child))
    
    return TestResults.model_validate(data)


def get_all_samples(test_results: TestResults, include_sub_samples: bool = True) -> list[HttpSample]:
    samples = []
    
    def collect_samples(sample: HttpSample):
        samples.append(sample)
        if include_sub_samples:
            for sub_sample in sample.http_sample:
                collect_samples(sub_sample)
    
    for sample in test_results.http_sample:
        collect_samples(sample)
    
    return samples


def get_top_level_samples(test_results: TestResults) -> list[HttpSample]:
    return test_results.http_sample


def get_failed_samples(test_results: TestResults) -> list[HttpSample]:
    all_samples = get_all_samples(test_results)
    return [sample for sample in all_samples if not sample.success]