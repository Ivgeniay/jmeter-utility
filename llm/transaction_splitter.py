import json
import os
from dataclasses import dataclass

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage

from llm.llm_helper import get_llm
from traffic_builder.har_parsers.pydantic_models import Entry, HarFile


load_dotenv()


@dataclass
class TransactionAnchor:
    name: str
    anchor_path: str
    anchor_method: str = "GET"


@dataclass
class TransactionGroup:
    name: str
    start_index: int
    end_index: int


SYSTEM_PROMPT = """Ты эксперт по анализу HTTP трафика и нагрузочному тестированию.

Твоя задача — определить логические транзакции (шаги пользователя) и найти "якорный" запрос для каждого шага.

Якорный запрос — это основной запрос, с которого начинается шаг. Обычно это:
- GET на HTML страницу (не статику)
- POST для отправки формы (login, submit)
- Первый API вызов для действия

Правила:
1. Каждая транзакция = одно действие пользователя
2. Имена транзакций в формате: S{scenario}_{step}_{ActionName}
3. Для якоря указывай path (без домена) и method
4. Игнорируй статику (js, css, img, fonts, svg)

Если пользователь указал конкретные шаги — следуй его указаниям.

Ответ строго в формате JSON без markdown:
[
    {"name": "S01_01_OpenHomePage", "anchor_path": "/index.php", "anchor_method": "GET"},
    {"name": "S01_02_Login", "anchor_path": "/login", "anchor_method": "POST"}
]"""



def get_transaction_breakdown(
    har: HarFile,
    scenario_number: int = 1,
    user_hints: str | None = None,
    llm: BaseChatModel | None = None,
    model: str = "gpt-4o-mini",
) -> list[TransactionGroup]:
    if llm is None:
        llm = get_llm(model)
    
    entries = har.log.entries
    
    requests_summary = _build_requests_summary(entries)
    
    prompt = f"""Определи логические шаги пользователя и якорные запросы для каждого.

Номер сценария: {scenario_number:02d}
Формат имени: S{scenario_number:02d}_XX_ActionName

Запросы:
{json.dumps(requests_summary, indent=2, ensure_ascii=False)}
"""

    if user_hints:
        prompt += f"""
Указания пользователя:
{user_hints}

Определи якорные запросы для указанных шагов.
"""

    prompt += "\nВерни JSON массив с якорями."

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=prompt),
    ]
    
    response = llm.invoke(messages)
    
    anchors = _parse_anchors_response(response.content, scenario_number)
    
    transactions = _build_transactions_from_anchors(entries, anchors)
    
    return transactions


def get_single_transaction(
    har: HarFile, 
    scenario_number: int = 1,
    step_number: int = 1,
    name: str = "MainFlow"
) -> list[TransactionGroup]:
    return [
        TransactionGroup(
            name=f"S{scenario_number:02d}_{step_number:02d}_{name}",
            start_index=0,
            end_index=len(har.log.entries) - 1,
        )
    ]


def _build_requests_summary(entries: list[Entry]) -> list[dict]:
    summary = []
    
    for i, entry in enumerate(entries):
        request = entry.request
        url = request.url
        
        path = _extract_path(url)
        
        if _is_static_resource(path):
            continue
        
        content_type = ""
        for header in entry.response.headers:
            if header.name.lower() == "content-type":
                content_type = header.value.split(";")[0].strip()
                break
        
        summary.append({
            "index": i,
            "method": request.method,
            "path": path,
            "response_type": content_type,
        })
    
    return summary


def _is_static_resource(path: str) -> bool:
    static_extensions = {
        '.js', '.css', '.png', '.jpg', '.jpeg', '.gif', '.svg', 
        '.ico', '.woff', '.woff2', '.ttf', '.eot', '.map'
    }
    path_lower = path.lower().split('?')[0]
    return any(path_lower.endswith(ext) for ext in static_extensions)


def _extract_path(url: str) -> str:
    from urllib.parse import urlparse
    parsed = urlparse(url)
    path = parsed.path
    if len(path) > 80:
        path = path[:77] + "..."
    return path


def _parse_anchors_response(content: str, scenario_number: int) -> list[TransactionAnchor]:
    content = content.strip()
    
    if content.startswith("```json"):
        content = content[7:]
    if content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    
    content = content.strip()
    
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        return [
            TransactionAnchor(
                name=f"S{scenario_number:02d}_01_MainFlow",
                anchor_path="/",
                anchor_method="GET",
            )
        ]
    
    anchors = []
    for i, item in enumerate(data):
        default_name = f"S{scenario_number:02d}_{i+1:02d}_Unknown"
        anchors.append(
            TransactionAnchor(
                name=item.get("name", default_name),
                anchor_path=item.get("anchor_path", "/"),
                anchor_method=item.get("anchor_method", "GET").upper(),
            )
        )
    
    if not anchors:
        return [
            TransactionAnchor(
                name=f"S{scenario_number:02d}_01_MainFlow",
                anchor_path="/",
                anchor_method="GET",
            )
        ]
    
    return anchors


def _build_transactions_from_anchors(
    entries: list[Entry], 
    anchors: list[TransactionAnchor]
) -> list[TransactionGroup]:
    transactions = []
    
    anchor_indices = []
    for anchor in anchors:
        index = _find_anchor_index(entries, anchor)
        if index is not None:
            anchor_indices.append((index, anchor))
    
    anchor_indices.sort(key=lambda x: x[0])
    
    for i, (start_index, anchor) in enumerate(anchor_indices):
        if i + 1 < len(anchor_indices):
            end_index = anchor_indices[i + 1][0] - 1
        else:
            end_index = len(entries) - 1
        
        transactions.append(
            TransactionGroup(
                name=anchor.name,
                start_index=start_index,
                end_index=end_index,
            )
        )
    
    return transactions


def _find_anchor_index(entries: list[Entry], anchor: TransactionAnchor) -> int | None:
    for i, entry in enumerate(entries):
        request = entry.request
        path = _extract_path(request.url)
        
        if request.method.upper() == anchor.anchor_method:
            if anchor.anchor_path in path:
                return i
    
    return None