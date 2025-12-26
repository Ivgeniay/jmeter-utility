from dataclasses import dataclass, field
from enum import Enum


class ExtractionMethod(Enum):
    JSONPATH = "jsonpath"
    REGEX = "regex"
    XPATH = "xpath"
    BOUNDARY = "boundary"


class UsageType(Enum):
    QUERY = "query"
    PATH = "path"
    BODY = "body"
    HEADER = "header"


class ControllerType(Enum):
    NONE = "none"
    LOOP = "loop"
    FOREACH = "foreach"
    WHILE = "while"


class PostProcessingType(Enum):
    NONE = "none"
    CHUNK_SPLIT = "chunk_split"
    JOIN_VALUES = "join_values"
    CUSTOM_SCRIPT = "custom_script"


@dataclass
class TargetUsage:
    entry_index: int
    parameter_name: str
    usage_type: UsageType
    values_in_request: int
    raw_value: str = ""


@dataclass
class CorrelationInput:
    source_entry_index: int
    source_request_path: str
    source_response_body: str
    source_content_type: str
    
    target_usages: list[TargetUsage]
    
    value_sample: str
    value_path_hint: str
    values_total: int
    usage_count: int
    
    transaction_name: str = ""


@dataclass
class JMeterExtractor:
    type: ExtractionMethod
    variable_name: str
    expression: str
    match_nr: str = "1"
    default_value: str = ""
    target_entry_index: int = -1
    
    def to_dict(self) -> dict:
        return {
            "type": self.type.value,
            "variable_name": self.variable_name,
            "expression": self.expression,
            "match_nr": self.match_nr,
            "default_value": self.default_value,
            "target_entry_index": self.target_entry_index,
        }


@dataclass
class PostProcessingStep:
    type: PostProcessingType
    script_language: str = "groovy"
    script_code: str = ""
    description: str = ""
    
    chunk_size: int = 0
    delimiter: str = ";"
    input_variable: str = ""
    output_variable: str = ""
    
    def to_dict(self) -> dict:
        return {
            "type": self.type.value,
            "script_language": self.script_language,
            "script_code": self.script_code,
            "description": self.description,
            "chunk_size": self.chunk_size,
            "delimiter": self.delimiter,
            "input_variable": self.input_variable,
            "output_variable": self.output_variable,
        }


@dataclass
class ControllerStep:
    type: ControllerType
    controller_name: str = ""
    loop_count_variable: str = ""
    foreach_input_variable: str = ""
    foreach_output_variable: str = ""
    description: str = ""
    
    def to_dict(self) -> dict:
        return {
            "type": self.type.value,
            "controller_name": self.controller_name,
            "loop_count_variable": self.loop_count_variable,
            "foreach_input_variable": self.foreach_input_variable,
            "foreach_output_variable": self.foreach_output_variable,
            "description": self.description,
        }


@dataclass
class ParameterReplacement:
    entry_index: int
    parameter_name: str
    usage_type: UsageType
    variable_reference: str
    
    def to_dict(self) -> dict:
        return {
            "entry_index": self.entry_index,
            "parameter_name": self.parameter_name,
            "usage_type": self.usage_type.value,
            "variable_reference": self.variable_reference,
        }


@dataclass
class CorrelationOutput:
    extractor: JMeterExtractor
    
    post_processing: PostProcessingStep | None = None
    controller: ControllerStep | None = None
    
    parameter_replacements: list[ParameterReplacement] = field(default_factory=list)
    entries_to_remove: list[int] = field(default_factory=list)
    
    reasoning: str = ""
    complexity: str = "simple"
    
    def to_dict(self) -> dict:
        result = {
            "extractor": self.extractor.to_dict(),
            "post_processing": self.post_processing.to_dict() if self.post_processing else None,
            "controller": self.controller.to_dict() if self.controller else None,
            "parameter_replacements": [p.to_dict() for p in self.parameter_replacements],
            "entries_to_remove": self.entries_to_remove,
            "reasoning": self.reasoning,
            "complexity": self.complexity,
        }
        return result
    
    def to_json(self) -> dict:
        return self.to_dict()