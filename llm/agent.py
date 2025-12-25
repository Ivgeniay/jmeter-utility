import json

from langchain_core.language_models import BaseChatModel
from langgraph.prebuilt import create_react_agent

from llm.llm_tools import get_all_tools, get_result, reset_context, set_har
from llm.traffic_preparator import prepare_full_context, context_to_dict
from llm.transaction_splitter import get_llm

from traffic_analizator.models import AnalysisReport
from traffic_builder.har_parsers.pydantic_models import HarFile
from jmx_builder.models.tree import TestPlan


SYSTEM_PROMPT = """Ты эксперт по созданию JMeter скриптов для нагрузочного тестирования.

У тебя есть набор инструментов для построения JMX скрипта и данные о записанном HTTP трафике.

Правила создания скрипта:
1. Сначала создай TestPlan
2. Затем создай ThreadGroup внутри TestPlan
3. Добавь CookieManager в ThreadGroup для управления сессией
4. Создай TransactionController для каждого логического шага
5. Внутри каждой транзакции создай HTTP Sampler'ы из указанных entry
6. Для каждого sampler'а создай HeaderManager
7. Добавь экстракторы для корреляций (JSON или Regex)
8. Замени параметризуемые значения на переменные

Формат имён транзакций: S{сценарий}_{шаг}_{Действие}
Например: S01_01_OpenHomePage, S01_02_Login

При создании элементов всегда указывай правильного родителя (parent).
Используй entry_index из предоставленных данных о трафике.

Для корреляций:
- source_index — это entry где нужно добавить экстрактор
- target_index — это entry где нужно заменить значение на переменную
- extractor показывает какой тип экстрактора использовать (JSONPath или Regex)
"""


def run_jmx_agent(
    har: HarFile,
    report: AnalysisReport,
    user_prompt: str,
    llm: BaseChatModel | None = None,
    model: str = "gpt-4o-mini",
    verbose: bool = True,
) -> TestPlan | None:
    reset_context()
    set_har(har)
    
    context = prepare_full_context(har, report)
    context_json = json.dumps(context_to_dict(context), indent=2, ensure_ascii=False)
    
    if llm is None:
        llm = get_llm(model)
    
    tools = get_all_tools()
    
    agent = create_react_agent(llm, tools)
    
    full_message = f"""{SYSTEM_PROMPT}

Данные о трафике:

{context_json}

Задача:
{user_prompt}

Используй инструменты для создания JMX скрипта."""

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
    if steps_description:
        user_prompt = f"""
Создай JMeter скрипт для сценария #{scenario_number} "{scenario_name}".

Описание шагов:
{steps_description}

Требования:
1. Создай TestPlan с именем "{scenario_name}"
2. Создай ThreadGroup
3. Создай транзакции для каждого шага из описания
4. Добавь HTTP Sampler'ы для каждой транзакции (используй entry_index из трафика)
5. Добавь все необходимые корреляции из списка correlations
"""
    else:
        user_prompt = f"""
Создай JMeter скрипт для сценария #{scenario_number} "{scenario_name}".

Проанализируй трафик и:
1. Создай TestPlan с именем "{scenario_name}"
2. Создай ThreadGroup
3. Определи логические шаги и создай транзакции
4. Добавь HTTP Sampler'ы (используй entry_index из трафика)
5. Добавь все необходимые корреляции из списка correlations
"""
    
    return run_jmx_agent(
        har=har,
        report=report,
        user_prompt=user_prompt,
        llm=llm,
        model=model,
        verbose=verbose,
    )