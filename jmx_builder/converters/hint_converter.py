from traffic_analizator.extractors.base import ExtractorHint
from traffic_analizator.extractors.cookie_extractor import CookieExtractorHint
from traffic_analizator.extractors.header_extractor import HeaderExtractorHint
from traffic_analizator.extractors.json_extractor import JsonExtractorHint
from traffic_analizator.extractors.regex_extractor import RegexExtractorHint

from jmx_builder.models.tree import (
    TreeElement,
    JSONPostProcessor,
    RegexExtractor,
    RegexField,
)


class ExtractorHintConverter:
    
    @staticmethod
    def convert(hint: ExtractorHint) -> TreeElement:
        if isinstance(hint, JsonExtractorHint):
            return ExtractorHintConverter._convert_json(hint)
        elif isinstance(hint, RegexExtractorHint):
            return ExtractorHintConverter._convert_regex(hint)
        elif isinstance(hint, HeaderExtractorHint):
            return ExtractorHintConverter._convert_header(hint)
        elif isinstance(hint, CookieExtractorHint):
            return ExtractorHintConverter._convert_cookie(hint)
        else:
            raise ValueError(f"Unknown ExtractorHint type: {type(hint)}")
    
    @staticmethod
    def _convert_json(hint: JsonExtractorHint) -> JSONPostProcessor:
        variable_name = hint.variable_name or "extracted_json"
        
        extractor = JSONPostProcessor.create_default(testname=f"Extract {variable_name}")
        extractor.set_reference_names(variable_name)
        extractor.set_json_path_exprs(hint.json_path)
        extractor.set_match_numbers(str(hint.match_nr))
        extractor.set_default_values(hint.default_value)
        
        return extractor
    
    @staticmethod
    def _convert_regex(hint: RegexExtractorHint) -> RegexExtractor:
        variable_name = hint.variable_name or "extracted_regex"
        
        extractor = RegexExtractor.create_default(testname=f"Extract {variable_name}")
        extractor.set_refname(variable_name)
        extractor.set_regex(hint.pattern)
        extractor.set_template(f"${hint.group}$")
        extractor.set_match_number(hint.match_nr)
        extractor.set_default(hint.default_value)
        
        return extractor
    
    @staticmethod
    def _convert_header(hint: HeaderExtractorHint) -> RegexExtractor:
        variable_name = hint.variable_name or "extracted_header"
        
        extractor = RegexExtractor.create_default(testname=f"Extract {variable_name}")
        extractor.set_refname(variable_name)
        extractor.set_field(RegexField.RESPONSE_HEADERS)
        extractor.set_regex(f"{hint.header_name}: (.+)")
        extractor.set_template("$1$")
        extractor.set_match_number(1)
        
        return extractor
    
    @staticmethod
    def _convert_cookie(hint: CookieExtractorHint) -> RegexExtractor:
        variable_name = hint.variable_name or "extracted_cookie"
        
        extractor = RegexExtractor.create_default(testname=f"Extract {variable_name}")
        extractor.set_refname(variable_name)
        extractor.set_field(RegexField.RESPONSE_HEADERS)
        extractor.set_regex(f"Set-Cookie: {hint.cookie_name}=([^;]+)")
        extractor.set_template("$1$")
        extractor.set_match_number(1)
        
        return extractor


def convert_hint(hint: ExtractorHint) -> TreeElement:
    return ExtractorHintConverter.convert(hint)