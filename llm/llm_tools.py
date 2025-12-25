from typing import Any

from langchain_core.tools import tool

from jmx_builder.models.tree import (
    TestPlan,
    ThreadGroup,
    TransactionController,
    HTTPSamplerProxy,
    HeaderManager,
    JSONPostProcessor,
    RegexExtractor,
    RegexField,
    CookieManager,
)
from traffic_builder.har_parsers.pydantic_models import HarFile


class JmxBuildContext:
    def __init__(self):
        self.root: TestPlan | None = None
        self.elements: dict[str, Any] = {}
        self.har: HarFile | None = None
        self.last_sampler: HTTPSamplerProxy | None = None
    
    def reset(self):
        self.root = None
        self.elements = {}
        self.last_sampler = None
    
    def set_har(self, har: HarFile):
        self.har = har
    
    def get_element(self, name: str) -> Any:
        return self.elements.get(name)
    
    def register_element(self, name: str, element: Any):
        self.elements[name] = element


_context = JmxBuildContext()


def get_context() -> JmxBuildContext:
    return _context


def reset_context():
    _context.reset()


def set_har(har: HarFile):
    _context.set_har(har)


def get_result() -> TestPlan | None:
    return _context.root


@tool
def create_test_plan(name: str) -> str:
    """Создаёт корневой TestPlan. Это первый элемент, который нужно создать.
    
    Args:
        name: Имя тест-плана
    """
    test_plan = TestPlan.create_default(testname=name)
    _context.root = test_plan
    _context.register_element(name, test_plan)
    return f"TestPlan '{name}' создан"


@tool
def create_thread_group(name: str, parent: str, threads: int = 1, ramp_up: int = 1, loops: int = 1) -> str:
    """Создаёт ThreadGroup (группу потоков) внутри указанного родителя.
    
    Args:
        name: Имя ThreadGroup
        parent: Имя родительского элемента (обычно TestPlan)
        threads: Количество потоков (виртуальных пользователей)
        ramp_up: Время разгона в секундах
        loops: Количество итераций (-1 для бесконечного)
    """
    parent_element = _context.get_element(parent)
    if not parent_element:
        return f"Ошибка: родитель '{parent}' не найден"
    
    thread_group = ThreadGroup.create_default(testname=name)
    thread_group.set_num_threads(threads)
    thread_group.set_ramp_time(ramp_up)
    if loops == -1:
        thread_group.set_loop_count(-1)
        thread_group.set_continue_forever(True)
    else:
        thread_group.set_loop_count(loops)
    
    parent_element.children.append(thread_group)
    _context.register_element(name, thread_group)
    return f"ThreadGroup '{name}' создан в '{parent}'"


@tool
def create_transaction(name: str, parent: str, generate_parent_sample: bool = True) -> str:
    """Создаёт TransactionController для группировки запросов в логический шаг.
    
    Args:
        name: Имя транзакции (например S01_01_OpenHomePage)
        parent: Имя родительского элемента (ThreadGroup или другой контроллер)
        generate_parent_sample: Генерировать родительский sample в результатах
    """
    parent_element = _context.get_element(parent)
    if not parent_element:
        return f"Ошибка: родитель '{parent}' не найден"
    
    transaction = TransactionController.create_default(testname=name)
    transaction.set_generate_parent_sample(generate_parent_sample)
    
    parent_element.children.append(transaction)
    _context.register_element(name, transaction)
    return f"Transaction '{name}' создана в '{parent}'"


@tool
def create_http_sampler_from_entry(entry_index: int, parent: str, name: str | None = None) -> str:
    """Создаёт HTTP запрос из записанного трафика по индексу entry.
    
    Args:
        entry_index: Индекс записи в HAR файле
        parent: Имя родительского элемента (Transaction или ThreadGroup)
        name: Опциональное имя для sampler (по умолчанию из URL)
    """
    if not _context.har:
        return "Ошибка: HAR файл не загружен"
    
    if entry_index < 0 or entry_index >= len(_context.har.log.entries):
        return f"Ошибка: индекс {entry_index} вне диапазона"
    
    parent_element = _context.get_element(parent)
    if not parent_element:
        return f"Ошибка: родитель '{parent}' не найден"
    
    entry = _context.har.log.entries[entry_index]
    request = entry.request
    
    from urllib.parse import urlparse, parse_qs
    parsed = urlparse(request.url)
    
    sampler_name = name or f"{request.method} {parsed.path[:50]}"
    
    sampler = HTTPSamplerProxy.create_default(testname=sampler_name)
    sampler.set_protocol(parsed.scheme)
    sampler.set_domain(parsed.netloc.split(':')[0])
    if ':' in parsed.netloc:
        sampler.set_port(parsed.netloc.split(':')[1])
    sampler.set_path(parsed.path)
    sampler.set_method_raw(request.method)
    
    if parsed.query:
        for param in request.query_string:
            sampler.add_argument(param.name, param.value)
    
    if request.post_data:
        if request.post_data.params:
            for param in request.post_data.params:
                sampler.add_argument(param.name, param.value or "")
        elif request.post_data.text:
            sampler.set_body_data(request.post_data.text)
    
    parent_element.children.append(sampler)
    
    sampler_key = f"sampler_{entry_index}"
    _context.register_element(sampler_key, sampler)
    _context.last_sampler = sampler
    
    return f"HTTP Sampler '{sampler_name}' создан из entry #{entry_index} в '{parent}'"


@tool
def create_header_manager_from_entry(entry_index: int, parent: str) -> str:
    """Создаёт HeaderManager с заголовками из записанного трафика.
    
    Args:
        entry_index: Индекс записи в HAR файле
        parent: Имя родительского элемента (обычно sampler)
    """
    if not _context.har:
        return "Ошибка: HAR файл не загружен"
    
    if entry_index < 0 or entry_index >= len(_context.har.log.entries):
        return f"Ошибка: индекс {entry_index} вне диапазона"
    
    parent_element = _context.get_element(parent)
    if not parent_element:
        sampler_key = f"sampler_{entry_index}"
        parent_element = _context.get_element(sampler_key)
    
    if not parent_element:
        return f"Ошибка: родитель '{parent}' не найден"
    
    entry = _context.har.log.entries[entry_index]
    
    skip_headers = {
        'host', 'content-length', 'connection', 'accept-encoding',
        'cookie', 'sec-ch-ua', 'sec-ch-ua-mobile', 'sec-ch-ua-platform',
        'sec-fetch-dest', 'sec-fetch-mode', 'sec-fetch-site', 'sec-fetch-user',
        'upgrade-insecure-requests', 'priority',
    }
    
    header_manager = HeaderManager.create_default()
    
    for header in entry.request.headers:
        if header.name.lower() not in skip_headers:
            header_manager.add_header(header.name, header.value)
    
    parent_element.children.append(header_manager)
    return f"HeaderManager создан для entry #{entry_index}"


@tool
def add_json_extractor(
    variable_name: str,
    json_path: str,
    parent: str | None = None,
    match_nr: int = 1,
    default_value: str = ""
) -> str:
    """Добавляет JSON экстрактор для извлечения данных из ответа.
    
    Args:
        variable_name: Имя переменной для сохранения результата
        json_path: JSONPath выражение (например $.data.token)
        parent: Имя родительского sampler (если None - последний созданный)
        match_nr: Номер совпадения (1 - первое, -1 - все)
        default_value: Значение по умолчанию если не найдено
    """
    parent_element = None
    if parent:
        parent_element = _context.get_element(parent)
        if not parent_element:
            parent_element = _context.get_element(f"sampler_{parent}")
    
    if not parent_element:
        parent_element = _context.last_sampler
    
    if not parent_element:
        return "Ошибка: не указан родитель и нет последнего sampler"
    
    extractor = JSONPostProcessor.create_default(testname=f"Extract {variable_name}")
    extractor.set_reference_names(variable_name)
    extractor.set_json_path_exprs(json_path)
    extractor.set_match_numbers(str(match_nr))
    extractor.set_default_values(default_value)
    
    parent_element.children.append(extractor)
    return f"JSON Extractor '{variable_name}' добавлен с JSONPath: {json_path}"


@tool
def add_regex_extractor(
    variable_name: str,
    regex: str,
    parent: str | None = None,
    template: str = "$1$",
    match_nr: int = 1,
    default_value: str = "",
    field: str = "body"
) -> str:
    """Добавляет Regex экстрактор для извлечения данных из ответа.
    
    Args:
        variable_name: Имя переменной для сохранения результата
        regex: Регулярное выражение с группой захвата
        parent: Имя родительского sampler (если None - последний созданный)
        template: Шаблон результата (по умолчанию $1$)
        match_nr: Номер совпадения (1 - первое, -1 - все)
        default_value: Значение по умолчанию если не найдено
        field: Где искать: body, headers, url, code, message
    """
    parent_element = None
    if parent:
        parent_element = _context.get_element(parent)
        if not parent_element:
            parent_element = _context.get_element(f"sampler_{parent}")
    
    if not parent_element:
        parent_element = _context.last_sampler
    
    if not parent_element:
        return "Ошибка: не указан родитель и нет последнего sampler"
    
    extractor = RegexExtractor.create_default(testname=f"Extract {variable_name}")
    extractor.set_refname(variable_name)
    extractor.set_regex(regex)
    extractor.set_template(template)
    extractor.set_match_number(match_nr)
    extractor.set_default(default_value)
    
    field_mapping = {
        "body": RegexField.BODY,
        "headers": RegexField.RESPONSE_HEADERS,
        "url": RegexField.URL,
        "code": RegexField.RESPONSE_CODE,
        "message": RegexField.RESPONSE_MESSAGE,
    }
    if field.lower() in field_mapping:
        extractor.set_field(field_mapping[field.lower()])
    
    parent_element.children.append(extractor)
    return f"Regex Extractor '{variable_name}' добавлен с regex: {regex}"


@tool
def add_cookie_manager(parent: str, clear_each_iteration: bool = True) -> str:
    """Добавляет CookieManager для автоматического управления cookies.
    
    Args:
        parent: Имя родительского элемента (обычно ThreadGroup)
        clear_each_iteration: Очищать cookies каждую итерацию
    """
    parent_element = _context.get_element(parent)
    if not parent_element:
        return f"Ошибка: родитель '{parent}' не найден"
    
    cookie_manager = CookieManager.create_default()
    cookie_manager.set_clear_each_iteration(clear_each_iteration)
    
    parent_element.children.append(cookie_manager)
    return f"CookieManager добавлен в '{parent}'"


@tool
def set_variable_in_sampler(entry_index: int, param_name: str, variable_name: str, location: str) -> str:
    """Заменяет значение параметра на переменную ${variable_name}.
    
    Args:
        entry_index: Индекс sampler (entry)
        param_name: Имя параметра для замены
        variable_name: Имя переменной (без ${})
        location: Где заменить: query_param, form_param, header, path
    """
    sampler_key = f"sampler_{entry_index}"
    sampler = _context.get_element(sampler_key)
    
    if not sampler:
        return f"Ошибка: sampler для entry #{entry_index} не найден"
    
    variable_ref = f"${{{variable_name}}}"
    
    if location == "header":
        for child in sampler.children:
            if isinstance(child, HeaderManager):
                if child.change_header(param_name, new_value=variable_ref):
                    return f"Заголовок '{param_name}' заменён на {variable_ref}"
    
    elif location in ("query_param", "form_param"):
        args_data = sampler.get_arguments_data()
        for arg in args_data:
            if arg.name == param_name:
                arg.value = variable_ref
                sampler.set_arguments_data(args_data)
                return f"Параметр '{param_name}' заменён на {variable_ref}"
    
    elif location == "path":
        current_path = sampler.path.value
        new_path = current_path.replace(param_name, variable_ref)
        sampler.set_path(new_path)
        return f"Path обновлён: {param_name} -> {variable_ref}"
    
    return f"Не удалось найти '{param_name}' в {location}"


def get_all_tools() -> list:
    return [
        create_test_plan,
        create_thread_group,
        create_transaction,
        create_http_sampler_from_entry,
        create_header_manager_from_entry,
        add_json_extractor,
        add_regex_extractor,
        add_cookie_manager,
        set_variable_in_sampler,
    ]