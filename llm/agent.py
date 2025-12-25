import json

from langchain_core.language_models import BaseChatModel
#from langgraph.prebuilt import create_react_agent
from langchain.agents import create_agent
 
from llm.llm_tools import get_all_tools, get_result, reset_context, set_har
from llm.traffic_preparator import prepare_full_context, context_to_dict
from llm.transaction_splitter import get_llm, get_transaction_breakdown, TransactionGroup

from traffic_analizator.models import AnalysisReport
from traffic_builder.har_parsers.pydantic_models import HarFile 
from jmx_builder.models.tree import TestPlan


SYSTEM_PROMPT = """Ты эксперт по созданию JMeter скриптов для нагрузочного тестирования.

У тебя есть инструменты для построения JMX скрипта и полные данные о HTTP трафике.

## Структура данных

1. **transactions** — список транзакций (логических шагов пользователя):
   - name: имя транзакции (S01_01_OpenHomePage)
   - entry_indices: список индексов entry, которые входят в эту транзакцию
   - anchor_index: главный запрос транзакции

2. **correlations** — параметры, которые нужно извлечь и использовать:
   - variable: имя переменной
   - extract_from: откуда извлечь (entry_index, transaction, extractor_type, extractor_expr)
   - use_in: где использовать (список с entry_index, transaction, location, param_name)

3. **entries** — HTTP запросы (только нестатические):
   - index: индекс для использования в инструментах
   - method, path: метод и путь запроса
   - transaction: к какой транзакции относится
   - is_anchor: является ли якорным запросом транзакции

## Алгоритм создания скрипта

1. Создай TestPlan с указанным именем
2. Создай ThreadGroup внутри TestPlan
3. Добавь CookieManager в ThreadGroup
4. Для КАЖДОЙ транзакции из списка transactions:
   a. Создай TransactionController с именем транзакции
   b. Для КАЖДОГО entry_index из entry_indices этой транзакции:
      - Создай HTTP Sampler через create_http_sampler_from_entry
      - Создай HeaderManager через create_header_manager_from_entry
5. Для КАЖДОЙ корреляции из списка correlations:
   a. Добавь экстрактор в sampler с entry_index = extract_from.entry_index
      - Если extractor_type = "JSONPath" → используй add_json_extractor
      - Если extractor_type = "Regex" → используй add_regex_extractor
   b. Для КАЖДОГО элемента в use_in:
      - Вызови set_variable_in_sampler с соответствующими параметрами

## Важно

- Создавай ВСЕ entry из entry_indices каждой транзакции, не пропускай
- Экстрактор добавляется ОДИН раз на переменную (в extract_from.entry_index)
- Каждый use_in — это отдельный вызов set_variable_in_sampler
- Используй точные entry_index из данных, не придумывай свои
"""


def run_jmx_agent(
    har: HarFile,
    report: AnalysisReport,
    transactions: list[TransactionGroup],
    user_prompt: str,
    llm: BaseChatModel | None = None,
    model: str = "gpt-4o-mini",
    verbose: bool = True,
) -> TestPlan | None:
    reset_context()
    set_har(har)
    
    context = prepare_full_context(har, report, transactions)
    context_json = json.dumps(context_to_dict(context), indent=2, ensure_ascii=False)
    
    if llm is None:
        llm = get_llm(model)
    
    tools = get_all_tools()
    
    # agent = create_react_agent(llm, tools)
    agent = create_agent(llm, tools)
    
    full_message = f"""{SYSTEM_PROMPT}

## Данные о трафике

{context_json}

## Задача

{user_prompt}

Следуй алгоритму из инструкции. Создай ВСЕ элементы."""

    input_messages = {"messages": [("human", full_message)]}
    
    if verbose:
        print("=" * 60)
        print("Запуск агента...")
        print("=" * 60)
    
    for chunk in agent.stream(input_messages, stream_mode="updates"):
        if verbose:
            for node_name, node_output in chunk.items():
                if node_name == "agent":
                    messages = node_output.get("messages", [])
                    for msg in messages:
                        if hasattr(msg, "tool_calls") and msg.tool_calls:
                            for tc in msg.tool_calls:
                                print(f"[CALL] {tc['name']}({tc['args']})")
                elif node_name == "tools":
                    messages = node_output.get("messages", [])
                    for msg in messages:
                        content = getattr(msg, "content", str(msg))
                        if len(content) > 100:
                            content = content[:100] + "..."
                        print(f"[RESULT] {content}")
    
    if verbose:
        print("=" * 60)
        print("Агент завершил работу")
        print("=" * 60)
    
    return get_result()


def build_script_with_llm(
    har: HarFile,
    report: AnalysisReport,
    scenario_number: int = 1,
    scenario_name: str = "MainScenario",
    steps_description: str | None = None,
    llm: BaseChatModel | None = None,
    model: str = "gpt-4o-mini",
    verbose: bool = True,
) -> TestPlan | None:
    if llm is None:
        llm = get_llm(model)
    
    if verbose:
        print("Определение транзакций...")
    
    transactions = get_transaction_breakdown(
        har=har,
        scenario_number=scenario_number,
        user_hints=steps_description,
        llm=llm,
        model=model,
    )
    
    if verbose:
        print(f"Найдено транзакций: {len(transactions)}")
        for tx in transactions:
            print(f"  {tx.name}: entries {tx.start_index}-{tx.end_index}")
    
    user_prompt = f"""Создай JMeter скрипт "{scenario_name}".

TestPlan: "{scenario_name}"
ThreadGroup: "Users"

Создай все транзакции, sampler'ы и корреляции согласно данным."""
    
    return run_jmx_agent(
        har=har,
        report=report,
        transactions=transactions,
        user_prompt=user_prompt,
        llm=llm,
        model=model,
        verbose=verbose,
    )