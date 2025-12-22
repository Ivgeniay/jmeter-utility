import json
from pathlib import Path

from traffic_builder.har_parsers.pydantic_models import *


def parse_har(filepath: str | Path) -> HarFile:
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        data = json.load(f)
    
    return HarFile.model_validate(data)


def parse_har_from_string(content: str) -> HarFile:
    data = json.loads(content)
    return HarFile.model_validate(data)


def parse_har_from_dict(data: dict) -> HarFile:
    return HarFile.model_validate(data)


def get_requests(har: HarFile) -> list[Request]:
    return [entry.request for entry in har.log.entries]


def get_entries(har: HarFile) -> list[Entry]:
    return har.log.entries