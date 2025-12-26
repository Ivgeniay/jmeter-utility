from llm.agents.base_agent import run_with_validation
from llm.agents.validators.correlation_validator import CorrelationValidator
from llm.agents.workers.correlation_worker import CorrelationWorker
from llm.models.correlation import CorrelationInput, CorrelationOutput, TargetUsage, UsageType
from payloads.console import SLog

def test_simple_correlation():
    SLog.log("=" * 60)
    SLog.log("Тест 1: Простое извлечение токена")
    SLog.log("=" * 60)
    
    input_data = CorrelationInput(
        source_entry_index=5,
        source_request_path="POST /api/auth/login",
        source_response_body='{"token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...", "user": {"id": 123}}',
        source_content_type="application/json",
        target_usages=[
            TargetUsage(
                entry_index=10,
                parameter_name="Authorization",
                usage_type=UsageType.HEADER,
                values_in_request=1,
                raw_value="Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            )
        ],
        value_sample="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        value_path_hint="$.token",
        values_total=1,
        usage_count=1,
        transaction_name="S01_02_Login",
    )
    
    return _run_test(input_data)


def test_chunked_correlation():
    SLog.log("=" * 60)
    SLog.log("Тест 2: Чанки по 7 штук (как в твоём примере)")
    SLog.log("=" * 60)
    
    response_body = '''
{
    "files": [
        {"path": "Photos/Coast.jpg", "nodeid": 610, "mtime": 1765222498},
        {"path": "Photos/Hummingbird.jpg", "nodeid": 611, "mtime": 1765222499},
        {"path": "Photos/Desert.jpg", "nodeid": 612, "mtime": 1765222500},
        {"path": "Photos/Jellyfish.jpg", "nodeid": 613, "mtime": 1765222501},
        {"path": "Photos/Koala.jpg", "nodeid": 614, "mtime": 1765222502},
        {"path": "Photos/Lighthouse.jpg", "nodeid": 615, "mtime": 1765222503},
        {"path": "Photos/Penguins.jpg", "nodeid": 616, "mtime": 1765222504},
        {"path": "Photos/Tulips.jpg", "nodeid": 617, "mtime": 1765222505},
        {"path": "Photos/Chrysanthemum.jpg", "nodeid": 618, "mtime": 1765222506},
        {"path": "Photos/Hydrangeas.jpg", "nodeid": 619, "mtime": 1765222507},
        {"path": "Photos/Forest.jpg", "nodeid": 620, "mtime": 1765222508},
        {"path": "Photos/Lake.jpg", "nodeid": 621, "mtime": 1765222509},
        {"path": "Photos/Mountain.jpg", "nodeid": 622, "mtime": 1765222510},
        {"path": "Photos/River.jpg", "nodeid": 623, "mtime": 1765222511},
        {"path": "Photos/Sunset.jpg", "nodeid": 624, "mtime": 1765222512},
        {"path": "Photos/Valley.jpg", "nodeid": 625, "mtime": 1765222513},
        {"path": "Photos/Waterfall.jpg", "nodeid": 626, "mtime": 1765222514},
        {"path": "Photos/Beach.jpg", "nodeid": 627, "mtime": 1765222515},
        {"path": "Photos/Canyon.jpg", "nodeid": 628, "mtime": 1765222516},
        {"path": "Photos/Cliff.jpg", "nodeid": 629, "mtime": 1765222517},
        {"path": "Photos/Island.jpg", "nodeid": 630, "mtime": 1765222518}
    ],
    "albuminfo": {"path": "/Photos", "id": 159}
}
'''
    
    input_data = CorrelationInput(
        source_entry_index=50,
        source_request_path="GET /index.php/apps/gallery/files/159",
        source_response_body=response_body,
        source_content_type="application/json",
        target_usages=[
            TargetUsage(
                entry_index=55,
                parameter_name="ids",
                usage_type=UsageType.QUERY,
                values_in_request=7,
                raw_value="610;611;612;613;614;615;616",
            ),
            TargetUsage(
                entry_index=60,
                parameter_name="ids",
                usage_type=UsageType.QUERY,
                values_in_request=7,
                raw_value="617;618;619;620;621;622;623",
            ),
            TargetUsage(
                entry_index=65,
                parameter_name="ids",
                usage_type=UsageType.QUERY,
                values_in_request=7,
                raw_value="624;625;626;627;628;629;630",
            ),
        ],
        value_sample="610",
        value_path_hint="$.files[*].nodeid",
        values_total=21,
        usage_count=3,
        transaction_name="S01_03_OpenGallery",
    )
    
    return _run_test(input_data)


def test_foreach_correlation():
    SLog.log("=" * 60)
    SLog.log("Тест 3: ForEach — каждый ID отдельно")
    SLog.log("=" * 60)
    
    response_body = '''
{
    "items": [
        {"id": "abc-123", "name": "Item 1"},
        {"id": "def-456", "name": "Item 2"},
        {"id": "ghi-789", "name": "Item 3"}
    ]
}
'''
    
    input_data = CorrelationInput(
        source_entry_index=20,
        source_request_path="GET /api/items",
        source_response_body=response_body,
        source_content_type="application/json",
        target_usages=[
            TargetUsage(
                entry_index=21,
                parameter_name="id",
                usage_type=UsageType.PATH,
                values_in_request=1,
                raw_value="abc-123",
            ),
            TargetUsage(
                entry_index=22,
                parameter_name="id",
                usage_type=UsageType.PATH,
                values_in_request=1,
                raw_value="def-456",
            ),
            TargetUsage(
                entry_index=23,
                parameter_name="id",
                usage_type=UsageType.PATH,
                values_in_request=1,
                raw_value="ghi-789",
            ),
        ],
        value_sample="abc-123",
        value_path_hint="$.items[*].id",
        values_total=3,
        usage_count=3,
        transaction_name="S01_04_ProcessItems",
    )
    
    return _run_test(input_data)


def _run_test(input_data: CorrelationInput) -> CorrelationOutput:
    worker = CorrelationWorker()
    validator = CorrelationValidator(
        original_input=input_data,
        worker_system_prompt=CorrelationWorker.SYSTEM_PROMPT,
    )
    
    output, is_valid = run_with_validation(
        worker=worker,
        validator=validator,
        input_data=input_data,
        max_iterations=3,
        verbose=True,
        mega_verbose=True,
    )
    
    SLog.log("")
    SLog.log("=" * 60)
    SLog.log("РЕЗУЛЬТАТ:")
    SLog.log("=" * 60)
    SLog.log(f"  Валидация: {'✓ PASSED' if is_valid else '✗ FAILED'}")
    SLog.log(f"  Complexity: {output.complexity}")
    SLog.log("")
    SLog.log(f"  Extractor:")
    SLog.log(f"    Type: {output.extractor.type.value}")
    SLog.log(f"    Expression: {output.extractor.expression}")
    SLog.log(f"    Variable: {output.extractor.variable_name}")
    SLog.log(f"    Match NR: {output.extractor.match_nr}")
    
    if output.post_processing:
        SLog.log(f"")
        SLog.log(f"  Post-processing: {output.post_processing.type.value}")
        if output.post_processing.chunk_size:
            SLog.log(f"    Chunk size: {output.post_processing.chunk_size}")
        SLog.log(f"    Input var: {output.post_processing.input_variable}")
        SLog.log(f"    Output var: {output.post_processing.output_variable}")
        if output.post_processing.script_code:
            SLog.log(f"    Script: {output.post_processing.script_code[:100]}...")
    
    if output.controller:
        SLog.log(f"")
        SLog.log(f"  Controller: {output.controller.type.value}")
        SLog.log(f"    Name: {output.controller.controller_name}")
        if output.controller.loop_count_variable:
            SLog.log(f"    Loop count var: {output.controller.loop_count_variable}")
        if output.controller.foreach_input_variable:
            SLog.log(f"    ForEach input: {output.controller.foreach_input_variable}")
        if output.controller.foreach_output_variable:
            SLog.log(f"    ForEach output: {output.controller.foreach_output_variable}")
    
    SLog.log(f"")
    SLog.log(f"  Replacements: {len(output.parameter_replacements)}")
    for rep in output.parameter_replacements:
        SLog.log(f"    Entry {rep.entry_index}: {rep.parameter_name} ({rep.usage_type.value}) → {rep.variable_reference}")
    
    if output.entries_to_remove:
        SLog.log(f"")
        SLog.log(f"  Entries to remove: {output.entries_to_remove}")
    
    SLog.log(f"")
    SLog.log(f"  Reasoning: {output.reasoning}")
    SLog.log("")
    
    return output


def t2():
    # test_simple_correlation()
    test_chunked_correlation()
    test_foreach_correlation()