from llm.agents.base_agent import run_with_validation
from llm.agents.validators.correlation_validator import CorrelationValidator
from llm.agents.workers.correlation_worker import CorrelationWorker
from llm.models.correlation import CorrelationInput, CorrelationOutput
from payloads.console import SLog

from traffic_analizator.analyzer import analyze_har
from traffic_analizator.correlation_input import group_correlations
from traffic_builder.har_parsers.har_parser import parse_har

def run_full_pipeline(har_path: str, verbose: bool = True, mega_verbose: bool = False):
    SLog.log("=" * 70)
    SLog.log("ПОЛНЫЙ ПАЙПЛАЙН: HAR → TrafficAnalyzer → LLM Agents")
    SLog.log("=" * 70)
    SLog.log("")
    
    SLog.log(f"[1/4] Загрузка HAR: {har_path}")
    har = parse_har(har_path)
    SLog.log(f"      Загружено {len(har.log.entries)} entries")
    SLog.log("")
    
    SLog.log("[2/4] Анализ трафика (TrafficAnalyzer)...")
    report = analyze_har(har, min_value_length=4, ignore_cookies=True)
    SLog.log(f"      Найдено корреляций: {len(report.correlations)}")
    SLog.log(f"      Не разрешено: {len(report.unresolved)}")
    SLog.log("")
    
    SLog.log("[3/4] Группировка корреляций для LLM...")
    correlation_inputs = group_correlations(report, har)
    SLog.log(f"      Сгруппировано в {len(correlation_inputs)} CorrelationInput")
    SLog.log("")
    
    if not correlation_inputs:
        SLog.log("      Нет корреляций для обработки!")
        return []
    
    SLog.log("-" * 70)
    SLog.log("НАЙДЕННЫЕ КОРРЕЛЯЦИИ:")
    SLog.log("-" * 70)
    for i, ci in enumerate(correlation_inputs, 1):
        SLog.log(f"\n{i}. Source: entry #{ci.source_entry_index}")
        SLog.log(f"   Path hint: {ci.value_path_hint}")
        SLog.log(f"   Sample: {ci.value_sample[:50]}...")
        SLog.log(f"   Values total: {ci.values_total}")
        SLog.log(f"   Targets: {len(ci.target_usages)}")
        for t in ci.target_usages[:3]:
            SLog.log(f"     - entry #{t.entry_index}: {t.parameter_name} ({t.usage_type.value}), values: {t.values_in_request}")
        if len(ci.target_usages) > 3:
            SLog.log(f"     ... и ещё {len(ci.target_usages) - 3}")
    SLog.log("")
    
    SLog.log("[4/4] Обработка LLM агентами...")
    SLog.log("-" * 70)
    
    results: list[tuple[CorrelationInput, CorrelationOutput, bool]] = []
    
    for i, corr_input in enumerate(correlation_inputs, 1):
        SLog.log(f"\n>>> Корреляция {i}/{len(correlation_inputs)}: {corr_input.value_path_hint}")
        
        worker = CorrelationWorker()
        validator = CorrelationValidator(
            original_input=corr_input,
            worker_system_prompt=CorrelationWorker.SYSTEM_PROMPT,
        )
        
        try:
            output, is_valid = run_with_validation(
                worker=worker,
                validator=validator,
                input_data=corr_input,
                max_iterations=3,
                verbose=verbose,
                mega_verbose=mega_verbose,
            )
            results.append((corr_input, output, is_valid))
            
            SLog.log(f"\n    Результат: {'✓ VALID' if is_valid else '✗ INVALID'}")
            SLog.log(f"    Complexity: {output.complexity}")
            SLog.log(f"    Extractor: {output.extractor.type.value} → {output.extractor.expression}")
            if output.controller:
                SLog.log(f"    Controller: {output.controller.type.value}")
            if output.entries_to_remove:
                SLog.log(f"    Entries to remove: {output.entries_to_remove}")
                
        except Exception as e:
            SLog.log(f"\n    ✗ ОШИБКА: {e}")
            results.append((corr_input, None, False))
    
    SLog.log("")
    SLog.log("=" * 70)
    SLog.log("ИТОГОВЫЙ ОТЧЁТ")
    SLog.log("=" * 70)
    
    valid_count = sum(1 for _, _, is_valid in results if is_valid)
    SLog.log(f"Обработано: {len(results)}")
    SLog.log(f"Успешно: {valid_count}")
    SLog.log(f"С ошибками: {len(results) - valid_count}")
    SLog.log("")
    
    for i, (corr_input, output, is_valid) in enumerate(results, 1):
        status = "✓" if is_valid else "✗"
        if output:
            SLog.log(f"{status} {i}. {corr_input.value_path_hint}")
            SLog.log(f"      → {output.extractor.variable_name} ({output.complexity})")
        else:
            SLog.log(f"{status} {i}. {corr_input.value_path_hint} — ОШИБКА")
    
    return results


def run_single_correlation(
    har_path: str, 
    correlation_index: int = 0,
    mega_verbose: bool = True
) -> CorrelationOutput | None:
    SLog.log(f"Загрузка HAR: {har_path}")
    har = parse_har(har_path)
    
    SLog.log("Анализ трафика...")
    report = analyze_har(har, min_value_length=3, ignore_cookies=True)
    
    SLog.log("Группировка...")
    correlation_inputs = group_correlations(report, har)
    
    if correlation_index >= len(correlation_inputs):
        SLog.log(f"Корреляция #{correlation_index} не найдена (всего {len(correlation_inputs)})")
        return None
    
    corr_input = correlation_inputs[correlation_index]
    
    SLog.log(f"\nОбработка корреляции #{correlation_index}:")
    SLog.log(f"  Source: entry #{corr_input.source_entry_index}")
    SLog.log(f"  Path: {corr_input.value_path_hint}")
    SLog.log(f"  Values: {corr_input.values_total}")
    SLog.log(f"  Targets: {len(corr_input.target_usages)}")
    SLog.log("")
    
    worker = CorrelationWorker()
    validator = CorrelationValidator(
        original_input=corr_input,
        worker_system_prompt=CorrelationWorker.SYSTEM_PROMPT,
    )
    
    output, is_valid = run_with_validation(
        worker=worker,
        validator=validator,
        input_data=corr_input,
        max_iterations=3,
        verbose=True,
        mega_verbose=mega_verbose,
    )
    
    return output


def t3(har_path: str):
    results = run_full_pipeline(har_path, verbose=True, mega_verbose=True)