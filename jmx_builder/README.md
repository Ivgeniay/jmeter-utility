# jmx_builder

Пакет для программного создания, редактирования и парсинга JMeter JMX файлов.

## Архитектура

Пакет состоит из двух основных частей: **модели** и **парсеры**.

### Модели

Модели представляют объектную структуру JMX файла.

| Файл | Описание |
|------|----------|
| [models/base.py](models/base.py) | Базовые абстрактные классы `JMXElement` и `IHierarchable` |
| [models/props.py](models/props.py) | Классы для XML пропов (stringProp, boolProp, elementProp, etc.) |
| [models/tree.py](models/tree.py) | Классы для элементов дерева JMX (TestPlan, ThreadGroup, etc.) |

### Парсеры

Парсеры преобразуют XML в объектную модель.

| Файл | Описание |
|------|----------|
| [parsers/const.py](parsers/const.py) | Константы для имён пропов и атрибутов |
| [parsers/tree_parser.py](parsers/tree_parser.py) | Главный парсер — разбирает XML структуру и делегирует парсинг элементов |
| [parsers/elements/base.py](parsers/elements/base.py) | Базовый класс `TreeElementParser` с вспомогательными методами |
| [parsers/elements/](parsers/elements/) | Парсеры для конкретных элементов |

## Примеры использования

### Создание JMX программно

```python
from jmx_builder.models.tree import JMeterTestPlan, TestPlan, ThreadGroup, TransactionController

jmeter = JMeterTestPlan()

test_plan = TestPlan("My Load Test")
test_plan.add_variable("host", "api.example.com")
test_plan.add_variable("port", "443")

thread_group = ThreadGroup("Users")
thread_group.set_num_threads(100)
thread_group.set_ramp_time(60)
thread_group.set_loop_count(10)

tx_login = TransactionController("S1_01_Login")
tx_login.set_generate_parent_sample(True)

thread_group.add_child(tx_login)
test_plan.add_child(thread_group)
jmeter.add_child(test_plan)

print(jmeter.to_xml())
```

### Парсинг JMX файла

```python
from jmx_builder.parsers.tree_parser import TreeParser
from jmx_builder.parsers.elements.test_plan_parser import TestPlanParser
from jmx_builder.parsers.elements.thread_group_parser import ThreadGroupParser
from jmx_builder.parsers.elements.transaction_controller_parser import TransactionControllerParser

parser = TreeParser()
parser.register_parser("TestPlan", TestPlanParser)
parser.register_parser("ThreadGroup", ThreadGroupParser)
parser.register_parser("TransactionController", TransactionControllerParser)

with open("test.jmx", "r", encoding="utf-8") as f:
    xml_content = f.read()

test_plan = parser.parse(xml_content)
test_plan.print_info()

test_plan.change_name("Modified Test Plan")
test_plan.add_variable("new_var", "new_value")

with open("modified.jmx", "w", encoding="utf-8") as f:
    f.write(test_plan.to_xml())
```

### Отладка

```python
from console import SLog, ConsoleLog

SLog.register_logger(ConsoleLog())
test_plan.print_info()
```

## Чеклист для добавления нового элемента

- [ ] Изучить XML структуру элемента в JMeter
- [ ] Добавить константы в `parsers/const.py`
- [ ] Создать класс модели в `models/tree.py`
  - [ ] Определить `tag_name`, `guiclass`, `testclass`
  - [ ] Создать пропы как поля класса
  - [ ] Добавить методы-сеттеры
  - [ ] Реализовать `print_info()`
- [ ] Создать парсер в `parsers/elements/`
  - [ ] Наследовать от `TreeElementParser`
  - [ ] Реализовать статический метод `parse()`
- [ ] Зарегистрировать парсер в `TreeParser`
- [ ] Написать тесты