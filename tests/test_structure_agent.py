from llm.agents.base_agent import run_with_validation
from llm.agents.validators.structure_validator import StructureValidator
from llm.agents.workers.structure_worker import StructureWorker
from llm.models.structure import EntryInfo, StructureInput
from payloads.console import SLog
from traffic_builder.har_parsers.har_parser import parse_har


def har_to_entries(har) -> list[EntryInfo]:
    entries = []
    for i, entry in enumerate(har.log.entries):
        req = entry.request
        resp = entry.response
        
        path = req.url
        if "://" in path:
            path = "/" + path.split("://", 1)[1].split("/", 1)[-1]
        
        entries.append(EntryInfo(
            index=i,
            method=req.method,
            path=path,
            status_code=resp.status,
        ))
    return entries



def start_test_structure_agent(har_path: str, user_hints: str | None = None):
    har = parse_har(har_path)
    entries = har_to_entries(har)
    
    SLog.log(f"Загружено {len(entries)} entries из HAR")
    SLog.log(f"Первые 5:")
    for e in entries[:5]:
        SLog.log(f"  [{e.index}] {e.method} {e.path} → {e.status_code}")
    SLog.log("")
    
    input_data = StructureInput(
        entries=entries,
        scenario_number=1,
        user_hints=user_hints,
    )
    
    worker = StructureWorker()
    validator = StructureValidator(
        original_input=input_data,
        worker_system_prompt=StructureWorker.SYSTEM_PROMPT,
    )
    
    output, is_valid = run_with_validation(
        worker=worker,
        validator=validator,
        input_data=input_data,
        max_iterations=3,
        verbose=True,
        mega_verbose=True
    )
    
    SLog.log("")
    SLog.log("=" * 60)
    SLog.log("РЕЗУЛЬТАТ")
    SLog.log("=" * 60)
    SLog.log(f"Валидация пройдена: {is_valid}")
    SLog.log(f"Транзакций: {len(output.transactions)}")
    SLog.log("")
    
    for tx in output.transactions:
        SLog.log(f"  {tx.name}: entries {tx.start_index}-{tx.end_index} ({tx.entry_count} шт)")
        if tx.description:
            SLog.log(f"    {tx.description}")
    
    return output


def t1():
    hints = """
        1. Открытие главной страницы
        2. Логин
        3. Открытие галереи
        4. Выбор альбома
        5. Просмотр фото
        """
        
    start_test_structure_agent('/opt/Fiddler/fiddler_classic_setup/Capturies/1_browser_1_step_har/All.har', user_hints=hints)