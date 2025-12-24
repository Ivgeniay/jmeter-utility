from abc import abstractmethod
from jmx_builder.models.dto import HTTPArgumentData, HTTPFileData, HTTPSamplerData
from payloads.console import SLog
from jmx_builder.parsers.const import *
from jmx_builder.models.base import IHierarchable, JMXElement
from jmx_builder.models.props import *
import uuid
from enum import Enum


class CategoryElement(Enum):
    UNDEFINED = "Undefined"
    ROOT = "Root"
    TEST_PLAN = "Test Plan"
    THREADS = "Threads"
    CONFIG_ELEMENT = "Config Element"
    LISTENER = "Listener"
    TIMER = "Timer"
    PRE_PROCESSORS = "Pre Processors"
    POST_PROCESSORS= "Post Processors"
    ASSERTIONS = "Assertions"
    TEST_FRAGMENT = "Test Fragment"
    NON_TEST_ELEMENTS = "Non-Test Elements"
    SAMPLER = "Sampler"
    LOGIC_CONTROLLER = "Logic Controller"


################## GENERAL ######################

class TreeElement(JMXElement, IHierarchable):
    category: CategoryElement = CategoryElement.UNDEFINED
    
    def __init__(
        self,
        testname: str,
        enabled: bool = True,
        properties: list[PropElement] | None = None
    ):
        self.testname = testname
        self.enabled = enabled
        self.children: list[TreeElement] = []
        self.comment: StringProp = StringProp(TESTPLAN_COMMENTS, "")
        self.properties: list[PropElement] = [self.comment]
        if properties:
            self.properties.extend(properties)

    @staticmethod
    def is_numeric(value: str) -> bool:
        """Проверяет, является ли строка числом (включая отрицательные)"""
        return value.lstrip("-").isdigit()

    @staticmethod  
    def parse_int_or_raw(value: str) -> int | str:
        """Возвращает int если это число, иначе строку как есть"""
        if value.lstrip("-").isdigit():
            return int(value)
        return value

    @property
    @abstractmethod
    def guiclass(self) -> str:
        pass
    
    @property
    @abstractmethod
    def testclass(self) -> str:
        pass

    @abstractmethod
    def print_info(self) -> None:
        pass

    def change_comment(self, comment: str) -> None:
        self.comment.value = comment

    def change_name(self, newname: str) -> None:
        self.testname = newname
    
    def add_child(self, element: "TreeElement", index: int | None = None) -> None:
        if index is None:
            self.children.append(element)
        else:
            self.children.insert(index, element)
    
    def remove_child(self, element: "TreeElement") -> None:
        if element in self.children:
            self.children.remove(element)
    
    def reindex(self, element: "TreeElement", new_index: int) -> None:
        if element not in self.children:
            return
        
        self.children.remove(element)
        self.children.insert(new_index, element)
    
    def to_xml(self) -> str:
        attrs = [
            f'guiclass="{self.guiclass}"',
            f'testclass="{self.testclass}"',
            f'testname="{self.testname}"'
        ]
        
        if not self.enabled:
            attrs.append('enabled="false"')
        
        attr_str = " ".join(attrs)
        
        parts = []
        for prop in self.properties:
            parts.append(self._indent(prop.to_xml()))
        
        if parts:
            props_xml = "\n".join(parts)
            element_xml = f'<{self.tag_name} {attr_str}>\n{props_xml}\n</{self.tag_name}>'
        else:
            element_xml = f'<{self.tag_name} {attr_str}/>'
        
        if not self.children:
            hashtree_xml = "<hashTree/>"
        else:
            children_parts = []
            for child in self.children:
                children_parts.append(self._indent(child.to_xml()))
            children_xml = "\n".join(children_parts)
            hashtree_xml = f'<hashTree>\n{children_xml}\n</hashTree>'
        
        return f'{element_xml}\n{hashtree_xml}'


class JMeterTestPlan(JMXElement, IHierarchable):
    category: CategoryElement = CategoryElement.ROOT
    
    def __init__(
        self,
        version: str = "1.2",
        properties: str = "5.0",
        jmeter: str = "5.6.3"
    ):
        self.version = version
        self.properties = properties
        self.jmeter = jmeter
        self.children: list[TreeElement] = []
    
    @property
    def tag_name(self) -> str:
        return "jmeterTestPlan"
    
    def add_child(self, element: TreeElement, index: int | None = None) -> None:
        if index is None:
            self.children.append(element)
        else:
            self.children.insert(index, element)
    
    def remove_child(self, element: TreeElement) -> None:
        if element in self.children:
            self.children.remove(element)
    
    def reindex(self, element: TreeElement, new_index: int) -> None:
        if element not in self.children:
            return
        
        self.children.remove(element)
        self.children.insert(new_index, element)
    
    def to_xml(self) -> str:
        attrs = [
            f'version="{self.version}"',
            f'properties="{self.properties}"',
            f'jmeter="{self.jmeter}"'
        ]
        attr_str = " ".join(attrs)
        
        if self.children:
            children_parts = []
            for child in self.children:
                children_parts.append(self._indent(child.to_xml()))
            children_xml = "\n".join(children_parts)
            hashtree_content = f'\n  <hashTree>\n{children_xml}\n  </hashTree>\n'
        else:
            hashtree_content = '\n  <hashTree/>\n'
        
        return f'<?xml version="1.0" encoding="UTF-8"?>\n<{self.tag_name} {attr_str}>{hashtree_content}</{self.tag_name}>'


class TestPlan(TreeElement):
    category: CategoryElement = CategoryElement.TEST_PLAN
    
    def __init__(
        self,
        testname: str = "Test Plan",
        enabled: bool = True
    ):
        self.functional_mode: BoolProp = BoolProp(TESTPLAN_FUNCTIONAL_MODE, False)
        self.serialize_threadgroups: BoolProp = BoolProp(TESTPLAN_SERIALIZE_THREADGROUPS, False)
        self.teardown_on_shutdown: BoolProp = BoolProp(TESTPLAN_TEARDOWN_ON_SHUTDOWN, True)
        self.user_define_classpath: StringProp = StringProp(TESTPLAN_USER_DEFINE_CLASSPATH, "")
        
        self._variables: UserDefinedVariablesProp = UserDefinedVariablesProp()
        self._user_defined_variables: ElementProp = ElementProp(
            name=TESTPLAN_USER_DEFINED_VARIABLES,
            element_type="Arguments",
            guiclass="ArgumentsPanel",
            testclass="Arguments",
            testname="User Defined Variables",
            properties=[self._variables]
        )
        
        super().__init__(
            testname=testname,
            enabled=enabled,
            properties=[
                self.functional_mode,
                self.serialize_threadgroups,
                self.teardown_on_shutdown,
                self._user_defined_variables,
                self.user_define_classpath
            ]
        )
    
    @property
    def tag_name(self) -> str:
        return "TestPlan"
    
    @property
    def guiclass(self) -> str:
        return "TestPlanGui"
    
    @property
    def testclass(self) -> str:
        return "TestPlan"
    
    def create_default(testname: str = "Test Plan") -> "TestPlan":
        return TestPlan(testname=testname)
    
    def add_variable(self, name: str, value: str) -> None:
        self._variables.add_variable(name, value)
    
    def remove_variable(self, name: str) -> None:
        self._variables.remove_variable(name)
    
    def get_variable(self, name: str) -> ElementProp | None:
        return self._variables.get_variable(name)
    
    def change_variable(self, name: str, new_name: str | None = None, new_value: str | None = None) -> bool:
        return self._variables.change_variable(name, new_name, new_value)
    
    def get_variable_value(self, name: str) -> str | None:
        return self._variables.get_variable_value(name)

    def has_variable(self, name: str, value: str | None = None) -> bool:
        return self._variables.has_variable(name, value)

    def get_variables_data(self) -> list[ArgumentData]:
        return self._variables.to_data()

    def set_variables_data(self, data: list[ArgumentData]) -> None:
        self._variables.from_data(data)
    
    def print_info(self) -> None:
        SLog.log(f"=== TestPlan: {self.testname} ===")
        SLog.log(f"  enabled: {self.enabled}")
        SLog.log(f"  comment: {self.comment.value}")
        SLog.log(f"  functional_mode: {self.functional_mode.value}")
        SLog.log(f"  serialize_threadgroups: {self.serialize_threadgroups.value}")
        SLog.log(f"  teardown_on_shutdown: {self.teardown_on_shutdown.value}")
        SLog.log(f"  user_define_classpath: {self.user_define_classpath.value}")
        SLog.log(f"  variables: {len(self._variables.items)}")
        for var in self._variables.items:
            name_prop = next((p for p in var.properties if p.name == "Argument.name"), None)
            value_prop = next((p for p in var.properties if p.name == "Argument.value"), None)
            if name_prop and value_prop:
                SLog.log(f"    {name_prop.value} = {value_prop.value}")
        SLog.log(f"  children: {len(self.children)}")


################## THREADS ######################

class OnSampleError(Enum):
    CONTINUE = "continue"
    START_NEXT_LOOP = "startnextloop"
    STOP_THREAD = "stopthread"
    STOP_TEST = "stoptest"
    STOP_TEST_NOW = "stoptestnow"


class ThreadGroup(TreeElement):
    category: CategoryElement = CategoryElement.THREADS
    
    def __init__(
        self,
        testname: str = "Thread Group",
        enabled: bool = True
    ):
        self.delayed_start: BoolProp = BoolProp(THREADGROUP_DELAYED_START, False)
        self.num_threads: IntProp = IntProp(THREADGROUP_NUM_THREADS, 1)
        self.ramp_time: IntProp = IntProp(THREADGROUP_RAMP_TIME, 1)
        self.duration: LongProp = LongProp(THREADGROUP_DURATION, 0)
        self.delay: LongProp = LongProp(THREADGROUP_DELAY, 0)
        self.same_user_on_next_iteration: BoolProp = BoolProp(THREADGROUP_SAME_USER_ON_NEXT_ITERATION, True)
        self.scheduler: BoolProp = BoolProp(THREADGROUP_SCHEDULER, False)
        self._on_sample_error: StringProp = StringProp(THREADGROUP_ON_SAMPLE_ERROR, OnSampleError.CONTINUE.value)
        
        self._loop_count_infinite: bool = False
        self._loop_count_prop: IntProp | StringProp = StringProp(LOOPCONTROLLER_LOOPS, "1")
        self._continue_forever: BoolProp = BoolProp(LOOPCONTROLLER_CONTINUE_FOREVER, False)
        
        self._loop_controller: ElementProp = ElementProp(
            name=THREADGROUP_MAIN_CONTROLLER,
            element_type="LoopController",
            guiclass="LoopControlPanel",
            testclass="LoopController",
            testname="Loop Controller",
            properties=[self._loop_count_prop, self._continue_forever]
        )
        
        super().__init__(
            testname=testname,
            enabled=enabled,
            properties=[
                self.delayed_start,
                self.num_threads,
                self.ramp_time,
                self.duration,
                self.delay,
                self.same_user_on_next_iteration,
                self.scheduler,
                self._on_sample_error,
                self._loop_controller
            ]
        )
    
    @property
    def tag_name(self) -> str:
        return "ThreadGroup"
    
    @property
    def guiclass(self) -> str:
        return "ThreadGroupGui"
    
    @property
    def testclass(self) -> str:
        return "ThreadGroup"
    
    def create_default(testname: str = "Thread Group") -> "ThreadGroup":
        return ThreadGroup(testname=testname)
    
    def set_on_sample_error(self, value: OnSampleError) -> None:
        self._on_sample_error.value = value.value
    
    def set_on_sample_error_raw(self, value: str) -> None:
        self._on_sample_error.value = value
    
    def set_loop_count_raw(self, value: str) -> None:
        if self._loop_count_infinite:
            self._loop_count_prop = StringProp(LOOPCONTROLLER_LOOPS, value)
            self._loop_controller.properties[0] = self._loop_count_prop
            self._loop_count_infinite = False
        else:
            self._loop_count_prop.value = value
    
    def set_loop_count(self, count: int) -> None:
        if self._loop_count_infinite:
            self._loop_count_prop = StringProp("LoopController.loops", str(count))
            self._loop_controller.properties[0] = self._loop_count_prop
            self._loop_count_infinite = False
        else:
            self._loop_count_prop.value = str(count)
    
    def set_loop_count_infinite(self, enable: bool) -> None:
        if enable and not self._loop_count_infinite:
            self._loop_count_prop = IntProp("LoopController.loops", -1)
            self._loop_controller.properties[0] = self._loop_count_prop
            self._loop_count_infinite = True
        elif not enable and self._loop_count_infinite:
            self._loop_count_prop = StringProp("LoopController.loops", "1")
            self._loop_controller.properties[0] = self._loop_count_prop
            self._loop_count_infinite = False

    def set_num_threads(self, count: int) -> None:
        self.num_threads.value = count
    
    def set_ramp_time(self, seconds: int) -> None:
        self.ramp_time.value = seconds
    
    def set_duration(self, seconds: int) -> None:
        self.duration.value = seconds
    
    def set_delay(self, seconds: int) -> None:
        self.delay.value = seconds
    
    def set_delayed_start(self, enable: bool) -> None:
        self.delayed_start.value = enable
    
    def set_same_user_on_next_iteration(self, enable: bool) -> None:
        self.same_user_on_next_iteration.value = enable
    
    def set_scheduler(self, enable: bool) -> None:
        self.scheduler.value = enable
    
    def set_continue_forever(self, enable: bool) -> None:
        self._continue_forever.value = enable

    def print_info(self) -> None:
        SLog.log(f"=== ThreadGroup: {self.testname} ===")
        SLog.log(f"  enabled: {self.enabled}")
        SLog.log(f"  comment: {self.comment.value}")
        SLog.log(f"  num_threads: {self.num_threads.value}")
        SLog.log(f"  ramp_time: {self.ramp_time.value}")
        SLog.log(f"  duration: {self.duration.value}")
        SLog.log(f"  delay: {self.delay.value}")
        SLog.log(f"  delayed_start: {self.delayed_start.value}")
        SLog.log(f"  scheduler: {self.scheduler.value}")
        SLog.log(f"  same_user_on_next_iteration: {self.same_user_on_next_iteration.value}")
        SLog.log(f"  on_sample_error: {self._on_sample_error.value}")
        SLog.log(f"  loop_count_infinite: {self._loop_count_infinite}")
        SLog.log(f"  loop_count: {self._loop_count_prop.value}")
        SLog.log(f"  continue_forever: {self._continue_forever.value}")
        SLog.log(f"  children: {len(self.children)}")


################## LOGIC CONTROLLERS ######################

class TransactionController(TreeElement):
    category: CategoryElement = CategoryElement.LOGIC_CONTROLLER
    
    def __init__(
        self,
        testname: str = "Transaction Controller",
        enabled: bool = True
    ):
        self.generate_parent_sample: BoolProp = BoolProp(TRANSACTIONCONTROLLER_PARENT, False)
        self.include_timers: BoolProp = BoolProp(TRANSACTIONCONTROLLER_INCLUDE_TIMERS, False)
        
        super().__init__(
            testname=testname,
            enabled=enabled,
            properties=[
                self.generate_parent_sample,
                self.include_timers
            ]
        )
    
    @property
    def tag_name(self) -> str:
        return "TransactionController"
    
    @property
    def guiclass(self) -> str:
        return "TransactionControllerGui"
    
    @property
    def testclass(self) -> str:
        return "TransactionController"
    
    @staticmethod
    def create_default(testname: str = "Transaction Controller") -> "TransactionController":
        return TransactionController(testname=testname)
        
    def set_generate_parent_sample(self, enable: bool) -> None:
        self.generate_parent_sample.value = enable
    
    def set_include_timers(self, enable: bool) -> None:
        self.include_timers.value = enable
        
    def print_info(self) -> None:
        SLog.log(f"=== TransactionController: {self.testname} ===")
        SLog.log(f"  enabled: {self.enabled}")
        SLog.log(f"  comment: {self.comment.value}")
        SLog.log(f"  generate_parent_sample: {self.generate_parent_sample.value}")
        SLog.log(f"  include_timers: {self.include_timers.value}")
        SLog.log(f"  children: {len(self.children)}")


class IfController(TreeElement):
    category: CategoryElement = CategoryElement.LOGIC_CONTROLLER
    
    def __init__(
        self,
        testname: str = "If Controller",
        enabled: bool = True
    ):
        self.condition: StringProp = StringProp(IFCONTROLLER_CONDITION, "")
        self.evaluate_all: BoolProp = BoolProp(IFCONTROLLER_EVALUATE_ALL, False)
        self.use_expression: BoolProp = BoolProp(IFCONTROLLER_USE_EXPRESSION, True)
        
        super().__init__(
            testname=testname,
            enabled=enabled,
            properties=[
                self.condition,
                self.evaluate_all,
                self.use_expression
            ]
        )
    
    @property
    def tag_name(self) -> str:
        return "IfController"
    
    @property
    def guiclass(self) -> str:
        return "IfControllerPanel"
    
    @property
    def testclass(self) -> str:
        return "IfController"
    
    @staticmethod
    def create_default(testname: str = "If Controller") -> "IfController":
        return IfController(testname=testname)
    
    def set_condition(self, condition: str) -> None:
        self.condition.value = condition
    
    def set_evaluate_all(self, enable: bool) -> None:
        self.evaluate_all.value = enable
    
    def set_use_expression(self, enable: bool) -> None:
        self.use_expression.value = enable
    
    def print_info(self) -> None:
        SLog.log(f"=== IfController: {self.testname} ===")
        SLog.log(f"  enabled: {self.enabled}")
        SLog.log(f"  comment: {self.comment.value}")
        SLog.log(f"  condition: {self.condition.value}")
        SLog.log(f"  evaluate_all: {self.evaluate_all.value}")
        SLog.log(f"  use_expression: {self.use_expression.value}")
        SLog.log(f"  children: {len(self.children)}")


class LoopController(TreeElement):
    category: CategoryElement = CategoryElement.LOGIC_CONTROLLER
    
    def __init__(
        self,
        testname: str = "Loop Controller",
        enabled: bool = True
    ):
        self._loop_count_infinite: bool = False
        self._loop_count_prop: IntProp | StringProp = StringProp(LOOPCONTROLLER_LOOPS, "1")
        self._continue_forever: BoolProp = BoolProp(LOOPCONTROLLER_CONTINUE_FOREVER, True)
        
        super().__init__(
            testname=testname,
            enabled=enabled,
            properties=[
                self._loop_count_prop,
                self._continue_forever
            ]
        )
    
    @property
    def tag_name(self) -> str:
        return "LoopController"
    
    @property
    def guiclass(self) -> str:
        return "LoopControlPanel"
    
    @property
    def testclass(self) -> str:
        return "LoopController"
    
    @staticmethod
    def create_default(testname: str = "Loop Controller") -> "LoopController":
        return LoopController(testname=testname)
    
    def set_loop_count_raw(self, value: str) -> None:
        """Устанавливает значение loops как строку (для переменных типа ${var})"""
        if self._loop_count_infinite:
            new_prop = StringProp(LOOPCONTROLLER_LOOPS, value)
            self._replace_property(self._loop_count_prop, new_prop)
            self._loop_count_prop = new_prop
            self._loop_count_infinite = False
        else:
            self._loop_count_prop.value = value
    
    def set_loop_count(self, count: int) -> None:
        if self._loop_count_infinite:
            new_prop = StringProp(LOOPCONTROLLER_LOOPS, str(count))
            self._replace_property(self._loop_count_prop, new_prop)
            self._loop_count_prop = new_prop
            self._loop_count_infinite = False
        else:
            self._loop_count_prop.value = str(count)
    
    def set_loop_count_infinite(self, enable: bool) -> None:
        if enable and not self._loop_count_infinite:
            new_prop = IntProp(LOOPCONTROLLER_LOOPS, -1)
            self._replace_property(self._loop_count_prop, new_prop)
            self._loop_count_prop = new_prop
            self._loop_count_infinite = True
        elif not enable and self._loop_count_infinite:
            new_prop = StringProp(LOOPCONTROLLER_LOOPS, "1")
            self._replace_property(self._loop_count_prop, new_prop)
            self._loop_count_prop = new_prop
            self._loop_count_infinite = False
    
    def _replace_property(self, old_prop: PropElement, new_prop: PropElement) -> None:
        if old_prop in self.properties:
            index = self.properties.index(old_prop)
            self.properties[index] = new_prop
    
    def print_info(self) -> None:
        SLog.log(f"=== LoopController: {self.testname} ===")
        SLog.log(f"  enabled: {self.enabled}")
        SLog.log(f"  comment: {self.comment.value}")
        SLog.log(f"  loop_count_infinite: {self._loop_count_infinite}")
        SLog.log(f"  loop_count: {self._loop_count_prop.value}")
        SLog.log(f"  continue_forever: {self._continue_forever.value}")
        SLog.log(f"  children: {len(self.children)}")


class WhileController(TreeElement):
    category: CategoryElement = CategoryElement.LOGIC_CONTROLLER
    
    def __init__(
        self,
        testname: str = "While Controller",
        enabled: bool = True
    ):
        self.condition: StringProp = StringProp(WHILECONTROLLER_CONDITION, "")
        
        super().__init__(
            testname=testname,
            enabled=enabled,
            properties=[
                self.condition
            ]
        )
    
    @property
    def tag_name(self) -> str:
        return "WhileController"
    
    @property
    def guiclass(self) -> str:
        return "WhileControllerGui"
    
    @property
    def testclass(self) -> str:
        return "WhileController"
    
    @staticmethod
    def create_default(testname: str = "While Controller") -> "WhileController":
        return WhileController(testname=testname)
    
    def set_condition(self, condition: str) -> None:
        self.condition.value = condition
    
    def print_info(self) -> None:
        SLog.log(f"=== WhileController: {self.testname} ===")
        SLog.log(f"  enabled: {self.enabled}")
        SLog.log(f"  comment: {self.comment.value}")
        condition_preview = self.condition.value[:50] + "..." if len(self.condition.value) > 50 else self.condition.value
        SLog.log(f"  condition: {condition_preview}")
        SLog.log(f"  children: {len(self.children)}")


class CriticalSectionController(TreeElement):
    category: CategoryElement = CategoryElement.LOGIC_CONTROLLER
    
    def __init__(
        self,
        testname: str = "Critical Section Controller",
        enabled: bool = True
    ):
        self.lock_name: StringProp = StringProp(CRITICALSECTIONCONTROLLER_LOCK_NAME, "global_lock")
        
        super().__init__(
            testname=testname,
            enabled=enabled,
            properties=[
                self.lock_name
            ]
        )
    
    @property
    def tag_name(self) -> str:
        return "CriticalSectionController"
    
    @property
    def guiclass(self) -> str:
        return "CriticalSectionControllerGui"
    
    @property
    def testclass(self) -> str:
        return "CriticalSectionController"
    
    @staticmethod
    def create_default(testname: str = "Critical Section Controller") -> "CriticalSectionController":
        return CriticalSectionController(testname=testname)
    
    def set_lock_name(self, name: str) -> None:
        self.lock_name.value = name
    
    def print_info(self) -> None:
        SLog.log(f"=== CriticalSectionController: {self.testname} ===")
        SLog.log(f"  enabled: {self.enabled}")
        SLog.log(f"  comment: {self.comment.value}")
        SLog.log(f"  lock_name: {self.lock_name.value}")
        SLog.log(f"  children: {len(self.children)}")


class ForeachController(TreeElement):
    category: CategoryElement = CategoryElement.LOGIC_CONTROLLER
    
    def __init__(
        self,
        testname: str = "ForEach Controller",
        enabled: bool = True
    ):
        self.input_val: StringProp = StringProp(FOREACHCONTROLLER_INPUT_VAL, "")
        self.return_val: StringProp = StringProp(FOREACHCONTROLLER_RETURN_VAL, "")
        self.use_separator: BoolProp = BoolProp(FOREACHCONTROLLER_USE_SEPARATOR, True)
        self.start_index: StringProp = StringProp(FOREACHCONTROLLER_START_INDEX, "")
        self.end_index: StringProp = StringProp(FOREACHCONTROLLER_END_INDEX, "")
        
        super().__init__(
            testname=testname,
            enabled=enabled,
            properties=[
                self.input_val,
                self.return_val,
                self.use_separator,
                self.start_index,
                self.end_index
            ]
        )
    
    @property
    def tag_name(self) -> str:
        return "ForeachController"
    
    @property
    def guiclass(self) -> str:
        return "ForeachControlPanel"
    
    @property
    def testclass(self) -> str:
        return "ForeachController"
    
    @staticmethod
    def create_default(testname: str = "ForEach Controller") -> "ForeachController":
        return ForeachController(testname=testname)
    
    def set_input_variable(self, prefix: str) -> None:
        self.input_val.value = prefix
    
    def set_output_variable(self, name: str) -> None:
        self.return_val.value = name
    
    def set_use_separator(self, enable: bool) -> None:
        self.use_separator.value = enable
    
    def set_start_index(self, index: int) -> None:
        self.start_index.value = str(index)
    
    def set_start_index_raw(self, index: str) -> None:
        self.start_index.value = index
    
    def set_end_index(self, index: int) -> None:
        self.end_index.value = str(index)
    
    def set_end_index_raw(self, index: str) -> None:
        self.end_index.value = index
    
    def print_info(self) -> None:
        SLog.log(f"=== ForeachController: {self.testname} ===")
        SLog.log(f"  enabled: {self.enabled}")
        SLog.log(f"  comment: {self.comment.value}")
        SLog.log(f"  input_val: {self.input_val.value}")
        SLog.log(f"  return_val: {self.return_val.value}")
        SLog.log(f"  use_separator: {self.use_separator.value}")
        SLog.log(f"  start_index: {self.start_index.value}")
        SLog.log(f"  end_index: {self.end_index.value}")
        SLog.log(f"  children: {len(self.children)}")


class IncludeController(TreeElement):
    category: CategoryElement = CategoryElement.LOGIC_CONTROLLER
    
    def __init__(
        self,
        testname: str = "Include Controller",
        enabled: bool = True
    ):
        self.include_path: StringProp = StringProp(INCLUDECONTROLLER_INCLUDE_PATH, "")
        
        super().__init__(
            testname=testname,
            enabled=enabled,
            properties=[
                self.include_path
            ]
        )
    
    @property
    def tag_name(self) -> str:
        return "IncludeController"
    
    @property
    def guiclass(self) -> str:
        return "IncludeControllerGui"
    
    @property
    def testclass(self) -> str:
        return "IncludeController"
    
    @staticmethod
    def create_default(testname: str = "Include Controller") -> "IncludeController":
        return IncludeController(testname=testname)
    
    def set_include_path(self, path: str) -> None:
        self.include_path.value = path
    
    def print_info(self) -> None:
        SLog.log(f"=== IncludeController: {self.testname} ===")
        SLog.log(f"  enabled: {self.enabled}")
        SLog.log(f"  comment: {self.comment.value}")
        SLog.log(f"  include_path: {self.include_path.value}")
        SLog.log(f"  children: {len(self.children)}")


class OnceOnlyController(TreeElement):
    category: CategoryElement = CategoryElement.LOGIC_CONTROLLER
    
    def __init__(
        self,
        testname: str = "Once Only Controller",
        enabled: bool = True
    ):
        super().__init__(
            testname=testname,
            enabled=enabled,
            properties=[]
        )
    
    @property
    def tag_name(self) -> str:
        return "OnceOnlyController"
    
    @property
    def guiclass(self) -> str:
        return "OnceOnlyControllerGui"
    
    @property
    def testclass(self) -> str:
        return "OnceOnlyController"
    
    @staticmethod
    def create_default(testname: str = "Once Only Controller") -> "OnceOnlyController":
        return OnceOnlyController(testname=testname)
    
    def print_info(self) -> None:
        SLog.log(f"=== OnceOnlyController: {self.testname} ===")
        SLog.log(f"  enabled: {self.enabled}")
        SLog.log(f"  comment: {self.comment.value}")
        SLog.log(f"  children: {len(self.children)}")


class InterleaveStyle(Enum):
    IGNORE_SUB_CONTROLLERS = 0
    INTERLEAVE_SUB_CONTROLLERS = 1


class InterleaveControl(TreeElement):
    category: CategoryElement = CategoryElement.LOGIC_CONTROLLER
    
    def __init__(
        self,
        testname: str = "Interleave Controller",
        enabled: bool = True
    ):
        self.style: IntProp = IntProp(INTERLEAVECONTROL_STYLE, InterleaveStyle.IGNORE_SUB_CONTROLLERS.value)
        self.accross_threads: BoolProp = BoolProp(INTERLEAVECONTROL_ACCROSS_THREADS, False)
        
        super().__init__(
            testname=testname,
            enabled=enabled,
            properties=[
                self.style,
                self.accross_threads
            ]
        )
    
    @property
    def tag_name(self) -> str:
        return "InterleaveControl"
    
    @property
    def guiclass(self) -> str:
        return "InterleaveControlGui"
    
    @property
    def testclass(self) -> str:
        return "InterleaveControl"
    
    @staticmethod
    def create_default(testname: str = "Interleave Controller") -> "InterleaveControl":
        return InterleaveControl(testname=testname)
    
    def set_style(self, style: InterleaveStyle) -> None:
        self.style.value = style.value
    
    def set_style_raw(self, style: int) -> None:
        self.style.value = style
    
    def set_accross_threads(self, enable: bool) -> None:
        self.accross_threads.value = enable
    
    def print_info(self) -> None:
        SLog.log(f"=== InterleaveControl: {self.testname} ===")
        SLog.log(f"  enabled: {self.enabled}")
        SLog.log(f"  comment: {self.comment.value}")
        
        style_name = "unknown"
        for s in InterleaveStyle:
            if s.value == self.style.value:
                style_name = s.name
                break
        SLog.log(f"  style: {self.style.value} ({style_name})")
        SLog.log(f"  accross_threads: {self.accross_threads.value}")
        SLog.log(f"  children: {len(self.children)}")


class RandomController(TreeElement):
    category: CategoryElement = CategoryElement.LOGIC_CONTROLLER
    
    def __init__(
        self,
        testname: str = "Random Controller",
        enabled: bool = True
    ):
        self.style: IntProp = IntProp(INTERLEAVECONTROL_STYLE, InterleaveStyle.IGNORE_SUB_CONTROLLERS.value)
        
        super().__init__(
            testname=testname,
            enabled=enabled,
            properties=[
                self.style
            ]
        )
    
    @property
    def tag_name(self) -> str:
        return "RandomController"
    
    @property
    def guiclass(self) -> str:
        return "RandomControlGui"
    
    @property
    def testclass(self) -> str:
        return "RandomController"
    
    @staticmethod
    def create_default(testname: str = "Random Controller") -> "RandomController":
        return RandomController(testname=testname)
    
    def set_style(self, style: InterleaveStyle) -> None:
        self.style.value = style.value
    
    def set_style_raw(self, style: int) -> None:
        self.style.value = style
    
    def print_info(self) -> None:
        SLog.log(f"=== RandomController: {self.testname} ===")
        SLog.log(f"  enabled: {self.enabled}")
        SLog.log(f"  comment: {self.comment.value}")
        
        style_name = "unknown"
        for s in InterleaveStyle:
            if s.value == self.style.value:
                style_name = s.name
                break
        SLog.log(f"  style: {self.style.value} ({style_name})")
        SLog.log(f"  children: {len(self.children)}")


class RandomOrderController(TreeElement):
    category: CategoryElement = CategoryElement.LOGIC_CONTROLLER
    
    def __init__(
        self,
        testname: str = "Random Order Controller",
        enabled: bool = True
    ):
        super().__init__(
            testname=testname,
            enabled=enabled,
            properties=[]
        )
    
    @property
    def tag_name(self) -> str:
        return "RandomOrderController"
    
    @property
    def guiclass(self) -> str:
        return "RandomOrderControllerGui"
    
    @property
    def testclass(self) -> str:
        return "RandomOrderController"
    
    @staticmethod
    def create_default(testname: str = "Random Order Controller") -> "RandomOrderController":
        return RandomOrderController(testname=testname)
    
    def print_info(self) -> None:
        SLog.log(f"=== RandomOrderController: {self.testname} ===")
        SLog.log(f"  enabled: {self.enabled}")
        SLog.log(f"  comment: {self.comment.value}")
        SLog.log(f"  children: {len(self.children)}")


class RecordingController(TreeElement):
    category: CategoryElement = CategoryElement.LOGIC_CONTROLLER
    
    def __init__(
        self,
        testname: str = "Recording Controller",
        enabled: bool = True
    ):
        super().__init__(
            testname=testname,
            enabled=enabled,
            properties=[]
        )
    
    @property
    def tag_name(self) -> str:
        return "RecordingController"
    
    @property
    def guiclass(self) -> str:
        return "RecordController"
    
    @property
    def testclass(self) -> str:
        return "RecordingController"
    
    @staticmethod
    def create_default(testname: str = "Recording Controller") -> "RecordingController":
        return RecordingController(testname=testname)
    
    def print_info(self) -> None:
        SLog.log(f"=== RecordingController: {self.testname} ===")
        SLog.log(f"  enabled: {self.enabled}")
        SLog.log(f"  comment: {self.comment.value}")
        SLog.log(f"  children: {len(self.children)}")


class RunTime(TreeElement):
    category: CategoryElement = CategoryElement.LOGIC_CONTROLLER
    
    def __init__(
        self,
        testname: str = "Runtime Controller",
        enabled: bool = True
    ):
        self.seconds: StringProp = StringProp(RUNTIME_SECONDS, "1")
        
        super().__init__(
            testname=testname,
            enabled=enabled,
            properties=[
                self.seconds
            ]
        )
    
    @property
    def tag_name(self) -> str:
        return "RunTime"
    
    @property
    def guiclass(self) -> str:
        return "RunTimeGui"
    
    @property
    def testclass(self) -> str:
        return "RunTime"
    
    @staticmethod
    def create_default(testname: str = "Runtime Controller") -> "RunTime":
        return RunTime(testname=testname)
    
    def set_seconds(self, seconds: int) -> None:
        self.seconds.value = str(seconds)
    
    def set_seconds_raw(self, seconds: str) -> None:
        self.seconds.value = seconds
    
    def print_info(self) -> None:
        SLog.log(f"=== RunTime: {self.testname} ===")
        SLog.log(f"  enabled: {self.enabled}")
        SLog.log(f"  comment: {self.comment.value}")
        SLog.log(f"  seconds: {self.seconds.value}")
        SLog.log(f"  children: {len(self.children)}")


class GenericController(TreeElement):
    category: CategoryElement = CategoryElement.LOGIC_CONTROLLER
    
    def __init__(
        self,
        testname: str = "Simple Controller",
        enabled: bool = True
    ):
        super().__init__(
            testname=testname,
            enabled=enabled,
            properties=[]
        )
    
    @property
    def tag_name(self) -> str:
        return "GenericController"
    
    @property
    def guiclass(self) -> str:
        return "LogicControllerGui"
    
    @property
    def testclass(self) -> str:
        return "GenericController"
    
    @staticmethod
    def create_default(testname: str = "Simple Controller") -> "GenericController":
        return GenericController(testname=testname)
    
    def print_info(self) -> None:
        SLog.log(f"=== GenericController: {self.testname} ===")
        SLog.log(f"  enabled: {self.enabled}")
        SLog.log(f"  comment: {self.comment.value}")
        SLog.log(f"  children: {len(self.children)}")


class ThroughputControllerStyle(Enum):
    TOTAL_EXECUTIONS = 0
    PERCENT_EXECUTIONS = 1


class ThroughputController(TreeElement):
    category: CategoryElement = CategoryElement.LOGIC_CONTROLLER
    
    def __init__(
        self,
        testname: str = "Throughput Controller",
        enabled: bool = True
    ):
        self.style: IntProp = IntProp(THROUGHPUTCONTROLLER_STYLE, ThroughputControllerStyle.TOTAL_EXECUTIONS.value)
        self.per_thread: BoolProp = BoolProp(THROUGHPUTCONTROLLER_PER_THREAD, False)
        self.max_throughput: IntProp = IntProp(THROUGHPUTCONTROLLER_MAX_THROUGHPUT, 1)
        self.percent_throughput: FloatProperty = FloatProperty(THROUGHPUTCONTROLLER_PERCENT_THROUGHPUT, 100.0)
        
        super().__init__(
            testname=testname,
            enabled=enabled,
            properties=[
                self.style,
                self.per_thread,
                self.max_throughput,
                self.percent_throughput
            ]
        )
    
    @property
    def tag_name(self) -> str:
        return "ThroughputController"
    
    @property
    def guiclass(self) -> str:
        return "ThroughputControllerGui"
    
    @property
    def testclass(self) -> str:
        return "ThroughputController"
    
    @staticmethod
    def create_default(testname: str = "Throughput Controller") -> "ThroughputController":
        return ThroughputController(testname=testname)
    
    def set_style(self, style: ThroughputControllerStyle) -> None:
        self.style.value = style.value
    
    def set_style_raw(self, style: int) -> None:
        self.style.value = style
    
    def set_per_thread(self, enable: bool) -> None:
        self.per_thread.value = enable
    
    def set_max_throughput(self, count: int) -> None:
        self.max_throughput.value = count
    
    def set_percent_throughput(self, percent: float) -> None:
        self.percent_throughput.value = percent
    
    def print_info(self) -> None:
        SLog.log(f"=== ThroughputController: {self.testname} ===")
        SLog.log(f"  enabled: {self.enabled}")
        SLog.log(f"  comment: {self.comment.value}")
        
        style_name = "unknown"
        for s in ThroughputControllerStyle:
            if s.value == self.style.value:
                style_name = s.name
                break
        SLog.log(f"  style: {self.style.value} ({style_name})")
        SLog.log(f"  per_thread: {self.per_thread.value}")
        SLog.log(f"  max_throughput: {self.max_throughput.value}")
        SLog.log(f"  percent_throughput: {self.percent_throughput.value}")
        SLog.log(f"  children: {len(self.children)}")


class SwitchController(TreeElement):
    category: CategoryElement = CategoryElement.LOGIC_CONTROLLER
    
    def __init__(
        self,
        testname: str = "Switch Controller",
        enabled: bool = True
    ):
        self.switch_value: StringProp = StringProp(SWITCHCONTROLLER_VALUE, "")
        
        super().__init__(
            testname=testname,
            enabled=enabled,
            properties=[
                self.switch_value
            ]
        )
    
    @property
    def tag_name(self) -> str:
        return "SwitchController"
    
    @property
    def guiclass(self) -> str:
        return "SwitchControllerGui"
    
    @property
    def testclass(self) -> str:
        return "SwitchController"
    
    @staticmethod
    def create_default(testname: str = "Switch Controller") -> "SwitchController":
        return SwitchController(testname=testname)
    
    def set_switch_value(self, value: str) -> None:
        self.switch_value.value = value
    
    def print_info(self) -> None:
        SLog.log(f"=== SwitchController: {self.testname} ===")
        SLog.log(f"  enabled: {self.enabled}")
        SLog.log(f"  comment: {self.comment.value}")
        SLog.log(f"  switch_value: {self.switch_value.value}")
        SLog.log(f"  children: {len(self.children)}")


class ModuleController(TreeElement):
    category: CategoryElement = CategoryElement.LOGIC_CONTROLLER
    
    def __init__(
        self,
        testname: str = "Module Controller",
        enabled: bool = True
    ):
        self._node_path: list[str] = []
        self._node_path_prop: CollectionProp = CollectionProp(MODULECONTROLLER_NODE_PATH)
        
        super().__init__(
            testname=testname,
            enabled=enabled,
            properties=[]
        )
    
    @property
    def tag_name(self) -> str:
        return "ModuleController"
    
    @property
    def guiclass(self) -> str:
        return "ModuleControllerGui"
    
    @property
    def testclass(self) -> str:
        return "ModuleController"
    
    @staticmethod
    def create_default(testname: str = "Module Controller") -> "ModuleController":
        return ModuleController(testname=testname)
    
    def set_module_path(self, path: str, separator: str = "/") -> None:
        """
        Устанавливает путь к модулю в дереве JMeter.
        
        Путь задаётся строкой с разделителем (по умолчанию "/").
        Пример: "Test Plan/My Test Plan/Thread Group/If Controller"
        
        Также поддерживается "\\" как разделитель.
        """
        path_list = [p.strip() for p in path.split(separator) if p.strip()]
        self.set_module_path_list(path_list)
    
    def set_module_path_list(self, path_list: list[str]) -> None:
        """
        Устанавливает путь к модулю как список элементов дерева.
        
        Пример: ["Test Plan", "My Test Plan", "Thread Group", "If Controller"]
        """
        self._node_path = path_list
        self._node_path_prop.items = []
        
        for item in path_list:
            hash_value = hash(item) & 0xFFFFFFFF
            if hash_value > 0x7FFFFFFF:
                hash_value -= 0x100000000
            self._node_path_prop.items.append(StringProp(str(hash_value), item))
        
        if path_list:
            self._ensure_property(self._node_path_prop)
        else:
            self._remove_property(self._node_path_prop)
    
    def get_module_path(self) -> list[str]:
        """Возвращает путь к модулю как список."""
        return self._node_path.copy()
    
    def clear_module_path(self) -> None:
        """Очищает путь к модулю."""
        self._node_path = []
        self._node_path_prop.items = []
        self._remove_property(self._node_path_prop)
    
    def _ensure_property(self, prop: PropElement) -> None:
        if prop not in self.properties:
            self.properties.append(prop)
    
    def _remove_property(self, prop: PropElement) -> None:
        if prop in self.properties:
            self.properties.remove(prop)
    
    def print_info(self) -> None:
        SLog.log(f"=== ModuleController: {self.testname} ===")
        SLog.log(f"  enabled: {self.enabled}")
        SLog.log(f"  comment: {self.comment.value}")
        SLog.log(f"  module_path: {' / '.join(self._node_path) if self._node_path else '(not set)'}")
        SLog.log(f"  children: {len(self.children)}")


################## CONFIGURE ELEMENTS ######################

class HttpMethod(Enum):
    GET = "GET"
    POST = "POST"
    HEAD = "HEAD"
    PUT = "PUT"
    OPTIONS = "OPTIONS"
    TRACE = "TRACE"
    DELETE = "DELETE"
    PATCH = "PATCH"
    PROPFIND = "PROPFIND"
    PROPPATCH = "PROPPATCH"
    MKCOL = "MKCOL"
    COPY = "COPY"
    MOVE = "MOVE"
    LOCK = "LOCK"
    UNLOCK = "UNLOCK"
    REPORT = "REPORT"
    SEARCH = "SEARCH"
    MKCALENDAR = "MKCALENDAR"


class HttpImplementation(Enum):
    HTTP_CLIENT4 = "HttpClient4"
    JAVA = "Java"


class IpSourceType(Enum):
    IP_HOSTNAME = 0
    DEVICE = 1
    DEVICE_IPV4 = 2
    DEVICE_IPV6 = 3


class RedirectType(Enum):
    NONE = "none"
    FOLLOW_REDIRECTS = "follow"
    AUTO_REDIRECTS = "auto"


class CookieManagerPolicy(Enum):
    STANDARD = "standard"
    STANDARD_STRICT = "standard-strict"
    IGNORE_COOKIES = "ignoreCookies"
    NETSCAPE = "netscape"
    DEFAULT = "default"
    RFC2109 = "rfc2109"
    RFC2965 = "rfc2965"
    BEST_MATCH = "best-match"
    COMPATIBILITY = "compatibility"


class CookieManager(TreeElement):
    category: CategoryElement = CategoryElement.CONFIG_ELEMENT
    
    def __init__(
        self,
        testname: str = "HTTP Cookie Manager",
        enabled: bool = True
    ):
        self.clear_each_iteration: BoolProp = BoolProp(COOKIEMANAGER_CLEAR_EACH_ITERATION, False)
        self.controlled_by_threadgroup: BoolProp = BoolProp(COOKIEMANAGER_CONTROLLED_BY_THREADGROUP, False)
        self.policy: StringProp = StringProp(COOKIEMANAGER_POLICY, "standard")
        self._cookies: CookiesProp = CookiesProp(COOKIEMANAGER_COOKIES)
        
        super().__init__(
            testname=testname,
            enabled=enabled,
            properties=[
                self._cookies,
                self.clear_each_iteration,
                self.controlled_by_threadgroup,
                self.policy
            ]
        )

    
    @property
    def tag_name(self) -> str:
        return "CookieManager"
    
    @property
    def guiclass(self) -> str:
        return "CookiePanel"
    
    @property
    def testclass(self) -> str:
        return "CookieManager"
    
    @staticmethod
    def create_default(testname: str = "HTTP Cookie Manager") -> "CookieManager":
        return CookieManager(testname=testname)

    def add_cookie(
        self,
        name: str,
        value: str,
        domain: str,
        path: str = "/",
        secure: bool = False,
        expires: int = 0,
        path_specified: bool = True,
        domain_specified: bool = True
    ) -> None:
        self._cookies.add_cookie(
            name, value, domain, path, secure, expires, path_specified, domain_specified
        )
    
    def set_cookie_manager_policy(self, policy: str) -> None:
        if not self.policy:
            self.policy: StringProp = StringProp(COOKIEMANAGER_POLICY, policy)
            self.properties.append(self.policy)
        else:
            self.policy.value = policy

    def set_cookie_manager_policy_typed(self, policy: CookieManagerPolicy) -> None:
        if not self.policy:
            self.policy: StringProp = StringProp(COOKIEMANAGER_POLICY, policy.value)
            self.properties.append(self.policy)
        else:
            self.policy.value = policy.value

    def remove_cookie(self, name: str) -> None:
        self._cookies.remove_cookie(name)
    
    def get_cookie(self, name: str) -> ElementProp | None:
        return self._cookies.get_cookie(name)
    
    def get_cookie_value(self, name: str) -> str | None:
        return self._cookies.get_cookie_value(name)

    def get_cookie_domain(self, name: str) -> str | None:
        return self._cookies.get_cookie_domain(name)

    def has_cookie(self, name: str, value: str | None = None) -> bool:
        return self._cookies.has_cookie(name, value)

    def get_cookies_data(self) -> list[CookieData]:
        return self._cookies.to_data()

    def set_cookies_data(self, data: list[CookieData]) -> None:
        self._cookies.from_data(data)
    
    def clear_cookies(self) -> None:
        self._cookies.clear()
    
    def set_clear_each_iteration(self, enable: bool) -> None:
        self.clear_each_iteration.value = enable
    
    def set_controlled_by_threadgroup(self, enable: bool) -> None:
        self.controlled_by_threadgroup.value = enable

    
    def print_info(self) -> None:
        SLog.log(f"=== CookieManager: {self.testname} ===")
        SLog.log(f"  enabled: {self.enabled}")
        SLog.log(f"  comment: {self.comment.value}")
        SLog.log(f"  clear_each_iteration: {self.clear_each_iteration.value}")
        SLog.log(f"  controlled_by_threadgroup: {self.controlled_by_threadgroup.value}")
        if self.policy:
            SLog.log(f"  policy: {self.policy.value}")
        SLog.log(f"  cookies: {len(self._cookies.items)}")
        for cookie in self._cookies.items:
            value_prop = next((p for p in cookie.properties if p.name == COOKIE_VALUE), None)
            domain_prop = next((p for p in cookie.properties if p.name == COOKIE_DOMAIN), None)
            path_prop = next((p for p in cookie.properties if p.name == COOKIE_PATH), None)
            if value_prop and domain_prop:
                path_str = path_prop.value if path_prop else "/"
                SLog.log(f"    {cookie.name} = {value_prop.value} (domain: {domain_prop.value}, path: {path_str})")
        SLog.log(f"  children: {len(self.children)}")


class CacheManager(TreeElement):
    category: CategoryElement = CategoryElement.CONFIG_ELEMENT
    
    def __init__(
        self,
        testname: str = "HTTP Cache Manager",
        enabled: bool = True
    ):
        self.clear_each_iteration: BoolProp = BoolProp(CACHEMANAGER_CLEAR_EACH_ITERATION, False)
        self.use_expires: BoolProp = BoolProp(CACHEMANAGER_USE_EXPIRES, False)
        self.controlled_by_thread: BoolProp = BoolProp(CACHEMANAGER_CONTROLLED_BY_THREAD, False)
        self.max_size: IntProp = IntProp(CACHEMANAGER_MAX_SIZE, 5000)
        
        super().__init__(
            testname=testname,
            enabled=enabled,
            properties=[
                self.clear_each_iteration,
                self.use_expires,
                self.controlled_by_thread,
                self.max_size
            ]
        )
    
    @property
    def tag_name(self) -> str:
        return "CacheManager"
    
    @property
    def guiclass(self) -> str:
        return "CacheManagerGui"
    
    @property
    def testclass(self) -> str:
        return "CacheManager"
    
    @staticmethod
    def create_default(testname: str = "HTTP Cache Manager") -> "CacheManager":
        return CacheManager(testname=testname)
    
    def set_clear_each_iteration(self, enable: bool) -> None:
        self.clear_each_iteration.value = enable
    
    def set_use_expires(self, enable: bool) -> None:
        self.use_expires.value = enable
    
    def set_controlled_by_thread(self, enable: bool) -> None:
        self.controlled_by_thread.value = enable
    
    def set_max_size(self, size: int) -> None:
        self.max_size.value = size
    
    def print_info(self) -> None:
        SLog.log(f"=== CacheManager: {self.testname} ===")
        SLog.log(f"  enabled: {self.enabled}")
        SLog.log(f"  comment: {self.comment.value}")
        SLog.log(f"  clear_each_iteration: {self.clear_each_iteration.value}")
        SLog.log(f"  use_expires: {self.use_expires.value}")
        SLog.log(f"  controlled_by_thread: {self.controlled_by_thread.value}")
        SLog.log(f"  max_size: {self.max_size.value}")
        SLog.log(f"  children: {len(self.children)}")


class Arguments(TreeElement):
    category: CategoryElement = CategoryElement.CONFIG_ELEMENT
    
    def __init__(
        self,
        testname: str = "User Defined Variables",
        enabled: bool = True
    ):
        self._variables: UserDefinedVariablesWithDescProp = UserDefinedVariablesWithDescProp()
        
        super().__init__(
            testname=testname,
            enabled=enabled,
            properties=[
                self._variables
            ]
        )
    
    @property
    def tag_name(self) -> str:
        return "Arguments"
    
    @property
    def guiclass(self) -> str:
        return "ArgumentsPanel"
    
    @property
    def testclass(self) -> str:
        return "Arguments"
    
    @staticmethod
    def create_default(testname: str = "User Defined Variables") -> "Arguments":
        return Arguments(testname=testname)
    
    def add_variable(self, name: str, value: str, description: str = "") -> None:
        self._variables.add_variable(name, value, description)
    
    def remove_variable(self, name: str) -> None:
        self._variables.remove_variable(name)
    
    def get_variable(self, name: str) -> ElementProp | None:
        return self._variables.get_variable(name)
    
    def get_variables(self) -> UserDefinedVariablesWithDescProp:
        return self._variables
    
    def change_variable(
        self,
        name: str,
        new_name: str | None = None,
        new_value: str | None = None,
        new_description: str | None = None
    ) -> bool:
        return self._variables.change_variable(name, new_name, new_value, new_description)
    
    def clear_variables(self) -> None:
        self._variables.items = []
    
    def get_variable_value(self, name: str) -> str | None:
        return self._variables.get_variable_value(name)

    def has_variable(self, name: str, value: str | None = None) -> bool:
        return self._variables.has_variable(name, value)

    def get_variables_data(self) -> list[ArgumentWithDescData]:
        return self._variables.to_data()

    def set_variables_data(self, data: list[ArgumentWithDescData]) -> None:
        self._variables.from_data(data)
    
    def print_info(self) -> None:
        SLog.log(f"=== Arguments: {self.testname} ===")
        SLog.log(f"  enabled: {self.enabled}")
        SLog.log(f"  comment: {self.comment.value}")
        SLog.log(f"  variables: {len(self._variables.items)}")
        for var in self._variables.items:
            name_prop = next((p for p in var.properties if p.name == ARGUMENT_NAME), None)
            value_prop = next((p for p in var.properties if p.name == ARGUMENT_VALUE), None)
            desc_prop = next((p for p in var.properties if p.name == ARGUMENT_DESC), None)
            if name_prop and value_prop:
                desc_str = f" ({desc_prop.value})" if desc_prop and desc_prop.value else ""
                SLog.log(f"    {name_prop.value} = {value_prop.value}{desc_str}")
        SLog.log(f"  children: {len(self.children)}")


class HeaderManager(TreeElement):
    category: CategoryElement = CategoryElement.CONFIG_ELEMENT
    
    def __init__(
        self,
        testname: str = "HTTP Header Manager",
        enabled: bool = True
    ):
        self._headers: HeadersProp = HeadersProp(HEADERMANAGER_HEADERS)
        
        super().__init__(
            testname=testname,
            enabled=enabled,
            properties=[
                self._headers
            ]
        )
    
    @property
    def tag_name(self) -> str:
        return "HeaderManager"
    
    @property
    def guiclass(self) -> str:
        return "HeaderPanel"
    
    @property
    def testclass(self) -> str:
        return "HeaderManager"
    
    @staticmethod
    def create_default(testname: str = "HTTP Header Manager") -> "HeaderManager":
        return HeaderManager(testname=testname)
    
    def add_header(self, name: str, value: str) -> None:
        self._headers.add_header(name, value)
    
    def remove_header(self, name: str) -> None:
        self._headers.remove_header(name)
    
    def get_header(self, name: str) -> ElementProp | None:
        return self._headers.get_header(name)
    
    def change_header(
        self,
        name: str,
        new_name: str | None = None,
        new_value: str | None = None
    ) -> bool:
        return self._headers.change_header(name, new_name, new_value)
    
    def get_header_value(self, name: str) -> str | None:
        return self._headers.get_header_value(name)

    def has_header(self, name: str, value: str | None = None) -> bool:
        return self._headers.has_header(name, value)

    def get_headers_data(self) -> list[HeaderData]:
        return self._headers.to_data()

    def set_headers_data(self, data: list[HeaderData]) -> None:
        self._headers.from_data(data)
    
    def clear_headers(self) -> None:
        self._headers.clear()
    
    def print_info(self) -> None:
        SLog.log(f"=== HeaderManager: {self.testname} ===")
        SLog.log(f"  enabled: {self.enabled}")
        SLog.log(f"  comment: {self.comment.value}")
        SLog.log(f"  headers: {len(self._headers.items)}")
        for header in self._headers.items:
            name_prop = next((p for p in header.properties if p.name == HEADER_NAME), None)
            value_prop = next((p for p in header.properties if p.name == HEADER_VALUE), None)
            if name_prop and value_prop:
                SLog.log(f"    {name_prop.value}: {value_prop.value}")
        SLog.log(f"  children: {len(self.children)}")


class CSVShareMode(Enum):
    ALL = "shareMode.all"
    GROUP = "shareMode.group"
    THREAD = "shareMode.thread"


class CSVFileEncoding(Enum):
    UTF_8 = "UTF-8"
    UTF_16 = "UTF-16"
    ISO_8859_15 = "ISO-8859-15"
    US_ASCII = "US-ASCII"


class CSVDataSet(TreeElement):
    category: CategoryElement = CategoryElement.CONFIG_ELEMENT
    
    def __init__(
        self,
        testname: str = "CSV Data Set Config",
        enabled: bool = True
    ):
        self.filename: StringProp = StringProp(CSVDATASET_FILENAME, "")
        self.file_encoding: StringProp = StringProp(CSVDATASET_FILE_ENCODING, "")
        self.variable_names: StringProp = StringProp(CSVDATASET_VARIABLE_NAMES, "")
        self.ignore_first_line: BoolProp = BoolProp(CSVDATASET_IGNORE_FIRST_LINE, False)
        self.delimiter: StringProp = StringProp(CSVDATASET_DELIMITER, ",")
        self.quoted_data: BoolProp = BoolProp(CSVDATASET_QUOTED_DATA, False)
        self.recycle: BoolProp = BoolProp(CSVDATASET_RECYCLE, True)
        self.stop_thread: BoolProp = BoolProp(CSVDATASET_STOP_THREAD, False)
        self.share_mode: StringProp = StringProp(CSVDATASET_SHARE_MODE, CSVShareMode.ALL.value)
        
        super().__init__(
            testname=testname,
            enabled=enabled,
            properties=[
                self.filename,
                self.file_encoding,
                self.variable_names,
                self.ignore_first_line,
                self.delimiter,
                self.quoted_data,
                self.recycle,
                self.stop_thread,
                self.share_mode
            ]
        )
    
    @property
    def tag_name(self) -> str:
        return "CSVDataSet"
    
    @property
    def guiclass(self) -> str:
        return "TestBeanGUI"
    
    @property
    def testclass(self) -> str:
        return "CSVDataSet"
    
    @staticmethod
    def create_default(testname: str = "CSV Data Set Config") -> "CSVDataSet":
        return CSVDataSet(testname=testname)
    
    def set_filename(self, filename: str) -> None:
        self.filename.value = filename
    
    def set_file_encoding(self, encoding: str) -> None:
        self.file_encoding.value = encoding
    
    def set_file_encoding_typed(self, encoding: CSVFileEncoding) -> None:
        self.file_encoding.value = encoding.value
    
    def set_variable_names(self, names: str) -> None:
        self.variable_names.value = names
    
    def set_variable_names_list(self, names: list[str]) -> None:
        self.variable_names.value = ",".join(names)
    
    def set_ignore_first_line(self, ignore: bool) -> None:
        self.ignore_first_line.value = ignore
    
    def set_delimiter(self, delimiter: str) -> None:
        self.delimiter.value = delimiter
    
    def set_quoted_data(self, quoted: bool) -> None:
        self.quoted_data.value = quoted
    
    def set_recycle(self, recycle: bool) -> None:
        self.recycle.value = recycle
    
    def set_stop_thread(self, stop: bool) -> None:
        self.stop_thread.value = stop
    
    def set_share_mode(self, mode: str) -> None:
        self.share_mode.value = mode
    
    def set_share_mode_typed(self, mode: CSVShareMode) -> None:
        self.share_mode.value = mode.value
    
    def print_info(self) -> None:
        SLog.log(f"=== CSVDataSet: {self.testname} ===")
        SLog.log(f"  enabled: {self.enabled}")
        SLog.log(f"  comment: {self.comment.value}")
        SLog.log(f"  filename: {self.filename.value}")
        SLog.log(f"  file_encoding: {self.file_encoding.value}")
        SLog.log(f"  variable_names: {self.variable_names.value}")
        SLog.log(f"  ignore_first_line: {self.ignore_first_line.value}")
        SLog.log(f"  delimiter: {self.delimiter.value}")
        SLog.log(f"  quoted_data: {self.quoted_data.value}")
        SLog.log(f"  recycle: {self.recycle.value}")
        SLog.log(f"  stop_thread: {self.stop_thread.value}")
        SLog.log(f"  share_mode: {self.share_mode.value}")
        SLog.log(f"  children: {len(self.children)}")


class BoltConnectionElement(TreeElement):
    category: CategoryElement = CategoryElement.CONFIG_ELEMENT
    
    def __init__(
        self,
        testname: str = "Bolt Connection Configuration",
        enabled: bool = True
    ):
        self.bolt_uri: StringProp = StringProp(BOLTCONNECTION_URI, "bolt://localhost:7687")
        self.max_connection_pool_size: IntProp = IntProp(BOLTCONNECTION_MAX_POOL_SIZE, 100)
        self.password: StringProp = StringProp(BOLTCONNECTION_PASSWORD, "")
        self.username: StringProp = StringProp(BOLTCONNECTION_USERNAME, "neo4j")
        
        super().__init__(
            testname=testname,
            enabled=enabled,
            properties=[
                self.bolt_uri,
                self.max_connection_pool_size,
                self.password,
                self.username
            ]
        )
    
    @property
    def tag_name(self) -> str:
        return "BoltConnectionElement"
    
    @property
    def guiclass(self) -> str:
        return "TestBeanGUI"
    
    @property
    def testclass(self) -> str:
        return "BoltConnectionElement"
    
    @staticmethod
    def create_default(testname: str = "Bolt Connection Configuration") -> "BoltConnectionElement":
        return BoltConnectionElement(testname=testname)
    
    def set_bolt_uri(self, uri: str) -> None:
        self.bolt_uri.value = uri
    
    def set_max_connection_pool_size(self, size: int) -> None:
        self.max_connection_pool_size.value = size
    
    def set_password(self, password: str) -> None:
        self.password.value = password
    
    def set_username(self, username: str) -> None:
        self.username.value = username
    
    def print_info(self) -> None:
        SLog.log(f"=== BoltConnectionElement: {self.testname} ===")
        SLog.log(f"  enabled: {self.enabled}")
        SLog.log(f"  comment: {self.comment.value}")
        SLog.log(f"  bolt_uri: {self.bolt_uri.value}")
        SLog.log(f"  max_connection_pool_size: {self.max_connection_pool_size.value}")
        SLog.log(f"  username: {self.username.value}")
        SLog.log(f"  password: {'*' * len(self.password.value) if self.password.value else '(empty)'}")
        SLog.log(f"  children: {len(self.children)}")


class CounterConfig(TreeElement):
    category: CategoryElement = CategoryElement.CONFIG_ELEMENT
    
    def __init__(
        self,
        testname: str = "Counter",
        enabled: bool = True
    ):
        self.start: StringProp = StringProp(COUNTERCONFIG_START, "")
        self.end: StringProp = StringProp(COUNTERCONFIG_END, "")
        self.incr: StringProp = StringProp(COUNTERCONFIG_INCR, "1")
        self.variable_name: StringProp = StringProp(COUNTERCONFIG_NAME, "")
        self.format: StringProp = StringProp(COUNTERCONFIG_FORMAT, "")
        self.per_user: BoolProp = BoolProp(COUNTERCONFIG_PER_USER, False)
        self.reset_on_tg_iteration: BoolProp = BoolProp(COUNTERCONFIG_RESET_ON_TG_ITERATION, False)
        
        super().__init__(
            testname=testname,
            enabled=enabled,
            properties=[
                self.start,
                self.end,
                self.incr,
                self.variable_name,
                self.format,
                self.per_user,
                self.reset_on_tg_iteration
            ]
        )
    
    @property
    def tag_name(self) -> str:
        return "CounterConfig"
    
    @property
    def guiclass(self) -> str:
        return "CounterConfigGui"
    
    @property
    def testclass(self) -> str:
        return "CounterConfig"
    
    @staticmethod
    def create_default(testname: str = "Counter") -> "CounterConfig":
        return CounterConfig(testname=testname)
    
    def set_start(self, start: str) -> None:
        self.start.value = start
    
    def set_end(self, end: str) -> None:
        self.end.value = end
    
    def set_incr(self, incr: str) -> None:
        self.incr.value = incr
    
    def set_variable_name(self, name: str) -> None:
        self.variable_name.value = name
    
    def set_format(self, format: str) -> None:
        self.format.value = format
    
    def set_per_user(self, per_user: bool) -> None:
        self.per_user.value = per_user
    
    def set_reset_on_tg_iteration(self, reset: bool) -> None:
        self.reset_on_tg_iteration.value = reset
    
    def print_info(self) -> None:
        SLog.log(f"=== CounterConfig: {self.testname} ===")
        SLog.log(f"  enabled: {self.enabled}")
        SLog.log(f"  comment: {self.comment.value}")
        SLog.log(f"  start: {self.start.value}")
        SLog.log(f"  end: {self.end.value}")
        SLog.log(f"  incr: {self.incr.value}")
        SLog.log(f"  variable_name: {self.variable_name.value}")
        SLog.log(f"  format: {self.format.value}")
        SLog.log(f"  per_user: {self.per_user.value}")
        SLog.log(f"  reset_on_tg_iteration: {self.reset_on_tg_iteration.value}")
        SLog.log(f"  children: {len(self.children)}")


class RandomVariableConfig(TreeElement):
    category: CategoryElement = CategoryElement.CONFIG_ELEMENT
    
    def __init__(
        self,
        testname: str = "Random Variable",
        enabled: bool = True
    ):
        self.maximum_value: StringProp = StringProp(RANDOMVARIABLE_MAXIMUM_VALUE, "")
        self.minimum_value: StringProp = StringProp(RANDOMVARIABLE_MINIMUM_VALUE, "")
        self.output_format: StringProp = StringProp(RANDOMVARIABLE_OUTPUT_FORMAT, "")
        self.per_thread: BoolProp = BoolProp(RANDOMVARIABLE_PER_THREAD, False)
        self.random_seed: StringProp = StringProp(RANDOMVARIABLE_RANDOM_SEED, "")
        self.variable_name: StringProp = StringProp(RANDOMVARIABLE_VARIABLE_NAME, "")
        
        super().__init__(
            testname=testname,
            enabled=enabled,
            properties=[
                self.maximum_value,
                self.minimum_value,
                self.output_format,
                self.per_thread,
                self.random_seed,
                self.variable_name
            ]
        )
    
    @property
    def tag_name(self) -> str:
        return "RandomVariableConfig"
    
    @property
    def guiclass(self) -> str:
        return "TestBeanGUI"
    
    @property
    def testclass(self) -> str:
        return "RandomVariableConfig"
    
    @staticmethod
    def create_default(testname: str = "Random Variable") -> "RandomVariableConfig":
        return RandomVariableConfig(testname=testname)
    
    def set_maximum_value(self, value: str) -> None:
        self.maximum_value.value = value
    
    def set_minimum_value(self, value: str) -> None:
        self.minimum_value.value = value
    
    def set_output_format(self, format: str) -> None:
        self.output_format.value = format
    
    def set_per_thread(self, per_thread: bool) -> None:
        self.per_thread.value = per_thread
    
    def set_random_seed(self, seed: str) -> None:
        self.random_seed.value = seed
    
    def set_variable_name(self, name: str) -> None:
        self.variable_name.value = name
    
    def print_info(self) -> None:
        SLog.log(f"=== RandomVariableConfig: {self.testname} ===")
        SLog.log(f"  enabled: {self.enabled}")
        SLog.log(f"  comment: {self.comment.value}")
        SLog.log(f"  minimum_value: {self.minimum_value.value}")
        SLog.log(f"  maximum_value: {self.maximum_value.value}")
        SLog.log(f"  output_format: {self.output_format.value}")
        SLog.log(f"  per_thread: {self.per_thread.value}")
        SLog.log(f"  random_seed: {self.random_seed.value}")
        SLog.log(f"  variable_name: {self.variable_name.value}")
        SLog.log(f"  children: {len(self.children)}")


class LdapExtRequestDefaults(TreeElement):
    category: CategoryElement = CategoryElement.CONFIG_ELEMENT
    
    def __init__(
        self,
        testname: str = "LDAP Extended Request Defaults",
        enabled: bool = True
    ):
        self.servername: StringProp = StringProp(LDAPEXT_SERVERNAME, "")
        self.port: StringProp = StringProp(LDAPEXT_PORT, "")
        self.rootdn: StringProp = StringProp(LDAPEXT_ROOTDN, "")
        self.scope: StringProp = StringProp(LDAPEXT_SCOPE, "2")
        self.countlimit: StringProp = StringProp(LDAPEXT_COUNTLIMIT, "")
        self.timelimit: StringProp = StringProp(LDAPEXT_TIMELIMIT, "")
        self.attributes: StringProp = StringProp(LDAPEXT_ATTRIBUTES, "")
        self.return_object: StringProp = StringProp(LDAPEXT_RETURN_OBJECT, "false")
        self.deref_aliases: StringProp = StringProp(LDAPEXT_DEREF_ALIASES, "false")
        self.connection_timeout: StringProp = StringProp(LDAPEXT_CONNECTION_TIMEOUT, "")
        self.parseflag: StringProp = StringProp(LDAPEXT_PARSEFLAG, "false")
        self.secure: StringProp = StringProp(LDAPEXT_SECURE, "false")
        self.trustall: StringProp = StringProp(LDAPEXT_TRUSTALL, "false")
        self.user_dn: StringProp = StringProp(LDAPEXT_USER_DN, "")
        self.user_pw: StringProp = StringProp(LDAPEXT_USER_PW, "")
        self.comparedn: StringProp = StringProp(LDAPEXT_COMPAREDN, "")
        self.comparefilt: StringProp = StringProp(LDAPEXT_COMPAREFILT, "")
        self.modddn: StringProp = StringProp(LDAPEXT_MODDDN, "")
        self.newdn: StringProp = StringProp(LDAPEXT_NEWDN, "")
        self.test: StringProp = StringProp(LDAPEXT_TEST, "")
        
        super().__init__(
            testname=testname,
            enabled=enabled,
            properties=[
                self.servername,
                self.port,
                self.rootdn,
                self.scope,
                self.countlimit,
                self.timelimit,
                self.attributes,
                self.return_object,
                self.deref_aliases,
                self.connection_timeout,
                self.parseflag,
                self.secure,
                self.trustall,
                self.user_dn,
                self.user_pw,
                self.comparedn,
                self.comparefilt,
                self.modddn,
                self.newdn,
                self.test
            ]
        )
    
    @property
    def tag_name(self) -> str:
        return "ConfigTestElement"
    
    @property
    def guiclass(self) -> str:
        return "LdapExtConfigGui"
    
    @property
    def testclass(self) -> str:
        return "ConfigTestElement"
    
    @staticmethod
    def create_default(testname: str = "LDAP Extended Request Defaults") -> "LdapExtRequestDefaults":
        return LdapExtRequestDefaults(testname=testname)
    
    def set_servername(self, servername: str) -> None:
        self.servername.value = servername
    
    def set_port(self, port: str) -> None:
        self.port.value = port
    
    def set_rootdn(self, rootdn: str) -> None:
        self.rootdn.value = rootdn
    
    def set_scope(self, scope: str) -> None:
        self.scope.value = scope
    
    def set_countlimit(self, countlimit: str) -> None:
        self.countlimit.value = countlimit
    
    def set_timelimit(self, timelimit: str) -> None:
        self.timelimit.value = timelimit
    
    def set_attributes(self, attributes: str) -> None:
        self.attributes.value = attributes
    
    def set_return_object(self, return_object: bool) -> None:
        self.return_object.value = str(return_object).lower()
    
    def set_deref_aliases(self, deref_aliases: bool) -> None:
        self.deref_aliases.value = str(deref_aliases).lower()
    
    def set_connection_timeout(self, timeout: str) -> None:
        self.connection_timeout.value = timeout
    
    def set_parseflag(self, parseflag: bool) -> None:
        self.parseflag.value = str(parseflag).lower()
    
    def set_secure(self, secure: bool) -> None:
        self.secure.value = str(secure).lower()
    
    def set_trustall(self, trustall: bool) -> None:
        self.trustall.value = str(trustall).lower()
    
    def set_user_dn(self, user_dn: str) -> None:
        self.user_dn.value = user_dn
    
    def set_user_pw(self, user_pw: str) -> None:
        self.user_pw.value = user_pw
    
    def set_comparedn(self, comparedn: str) -> None:
        self.comparedn.value = comparedn
    
    def set_comparefilt(self, comparefilt: str) -> None:
        self.comparefilt.value = comparefilt
    
    def set_modddn(self, modddn: str) -> None:
        self.modddn.value = modddn
    
    def set_newdn(self, newdn: str) -> None:
        self.newdn.value = newdn
    
    def set_test(self, test: str) -> None:
        self.test.value = test
    
    def print_info(self) -> None:
        SLog.log(f"=== LdapExtRequestDefaults: {self.testname} ===")
        SLog.log(f"  enabled: {self.enabled}")
        SLog.log(f"  comment: {self.comment.value}")
        SLog.log(f"  servername: {self.servername.value}")
        SLog.log(f"  port: {self.port.value}")
        SLog.log(f"  rootdn: {self.rootdn.value}")
        SLog.log(f"  scope: {self.scope.value}")
        SLog.log(f"  countlimit: {self.countlimit.value}")
        SLog.log(f"  timelimit: {self.timelimit.value}")
        SLog.log(f"  attributes: {self.attributes.value}")
        SLog.log(f"  return_object: {self.return_object.value}")
        SLog.log(f"  deref_aliases: {self.deref_aliases.value}")
        SLog.log(f"  connection_timeout: {self.connection_timeout.value}")
        SLog.log(f"  parseflag: {self.parseflag.value}")
        SLog.log(f"  secure: {self.secure.value}")
        SLog.log(f"  trustall: {self.trustall.value}")
        SLog.log(f"  user_dn: {self.user_dn.value}")
        SLog.log(f"  user_pw: {'*' * len(self.user_pw.value) if self.user_pw.value else '(empty)'}")
        SLog.log(f"  comparedn: {self.comparedn.value}")
        SLog.log(f"  comparefilt: {self.comparefilt.value}")
        SLog.log(f"  modddn: {self.modddn.value}")
        SLog.log(f"  newdn: {self.newdn.value}")
        SLog.log(f"  test: {self.test.value}")
        SLog.log(f"  children: {len(self.children)}")


class FtpRequestDefaults(TreeElement):
    category: CategoryElement = CategoryElement.CONFIG_ELEMENT
    
    def __init__(
        self,
        testname: str = "FTP Request Defaults",
        enabled: bool = True
    ):
        self.server: StringProp = StringProp(FTPSAMPLER_SERVER, "")
        self.port: StringProp = StringProp(FTPSAMPLER_PORT, "")
        self.filename: StringProp = StringProp(FTPSAMPLER_FILENAME, "")
        self.localfilename: StringProp = StringProp(FTPSAMPLER_LOCALFILENAME, "")
        self.inputdata: StringProp = StringProp(FTPSAMPLER_INPUTDATA, "")
        self.binarymode: BoolProp = BoolProp(FTPSAMPLER_BINARYMODE, False)
        self.saveresponse: BoolProp = BoolProp(FTPSAMPLER_SAVERESPONSE, False)
        self.upload: BoolProp = BoolProp(FTPSAMPLER_UPLOAD, False)
        
        super().__init__(
            testname=testname,
            enabled=enabled,
            properties=[
                self.server,
                self.port,
                self.filename,
                self.localfilename,
                self.inputdata,
                self.binarymode,
                self.saveresponse,
                self.upload
            ]
        )
    
    @property
    def tag_name(self) -> str:
        return "ConfigTestElement"
    
    @property
    def guiclass(self) -> str:
        return "FtpConfigGui"
    
    @property
    def testclass(self) -> str:
        return "ConfigTestElement"
    
    @staticmethod
    def create_default(testname: str = "FTP Request Defaults") -> "FtpRequestDefaults":
        return FtpRequestDefaults(testname=testname)
    
    def set_server(self, server: str) -> None:
        self.server.value = server
    
    def set_port(self, port: str) -> None:
        self.port.value = port
    
    def set_filename(self, filename: str) -> None:
        self.filename.value = filename
    
    def set_localfilename(self, localfilename: str) -> None:
        self.localfilename.value = localfilename
    
    def set_inputdata(self, inputdata: str) -> None:
        self.inputdata.value = inputdata
    
    def set_binarymode(self, binarymode: bool) -> None:
        self.binarymode.value = binarymode
    
    def set_saveresponse(self, saveresponse: bool) -> None:
        self.saveresponse.value = saveresponse
    
    def set_upload(self, upload: bool) -> None:
        self.upload.value = upload
    
    def print_info(self) -> None:
        SLog.log(f"=== FtpRequestDefaults: {self.testname} ===")
        SLog.log(f"  enabled: {self.enabled}")
        SLog.log(f"  comment: {self.comment.value}")
        SLog.log(f"  server: {self.server.value}")
        SLog.log(f"  port: {self.port.value}")
        SLog.log(f"  filename: {self.filename.value}")
        SLog.log(f"  localfilename: {self.localfilename.value}")
        SLog.log(f"  inputdata: {self.inputdata.value}")
        SLog.log(f"  binarymode: {self.binarymode.value}")
        SLog.log(f"  saveresponse: {self.saveresponse.value}")
        SLog.log(f"  upload: {self.upload.value}")
        SLog.log(f"  children: {len(self.children)}")


class LdapRequestDefaults(TreeElement):
    category: CategoryElement = CategoryElement.CONFIG_ELEMENT
    
    def __init__(
        self,
        testname: str = "LDAP Request Defaults",
        enabled: bool = True
    ):
        self.servername: StringProp = StringProp(LDAP_SERVERNAME, "")
        self.port: StringProp = StringProp(LDAP_PORT, "")
        self.rootdn: StringProp = StringProp(LDAP_ROOTDN, "")
        self.user_defined: BoolProp = BoolProp(LDAP_USER_DEFINED, False)
        self.test: StringProp = StringProp(LDAP_TEST, "")
        self.base_entry_dn: StringProp = StringProp(LDAP_BASE_ENTRY_DN, "")
        self._arguments_collection: ArgumentsProp = ArgumentsProp()
        self._arguments: ElementProp = ElementProp(
            name=LDAP_ARGUMENTS,
            element_type="Arguments",
            guiclass="ArgumentsPanel",
            testclass="Arguments",
            testname="User Defined Variables",
            properties=[self._arguments_collection]
        )
        
        super().__init__(
            testname=testname,
            enabled=enabled,
            properties=[
                self.servername,
                self.port,
                self.rootdn,
                self.user_defined,
                self.test,
                self.base_entry_dn,
                self._arguments
            ]
        )
    
    @property
    def tag_name(self) -> str:
        return "ConfigTestElement"
    
    @property
    def guiclass(self) -> str:
        return "LdapConfigGui"
    
    @property
    def testclass(self) -> str:
        return "ConfigTestElement"
    
    @staticmethod
    def create_default(testname: str = "LDAP Request Defaults") -> "LdapRequestDefaults":
        return LdapRequestDefaults(testname=testname)
    
    def set_servername(self, servername: str) -> None:
        self.servername.value = servername
    
    def set_port(self, port: str) -> None:
        self.port.value = port
    
    def set_rootdn(self, rootdn: str) -> None:
        self.rootdn.value = rootdn
    
    def set_user_defined(self, user_defined: bool) -> None:
        self.user_defined.value = user_defined
    
    def set_test(self, test: str) -> None:
        self.test.value = test
    
    def set_base_entry_dn(self, base_entry_dn: str) -> None:
        self.base_entry_dn.value = base_entry_dn
    
    def add_argument(self, name: str, value: str) -> None:
        self._arguments_collection.add_argument(name, value)
    
    def remove_argument(self, name: str) -> None:
        self._arguments_collection.remove_argument(name)
    
    def get_argument(self, name: str) -> ElementProp | None:
        return self._arguments_collection.get_argument(name)
    
    def get_argument_value(self, name: str) -> str | None:
        return self._arguments_collection.get_argument_value(name)

    def has_argument(self, name: str, value: str | None = None) -> bool:
        return self._arguments_collection.has_argument(name, value)

    def get_arguments_data(self) -> list[ArgumentData]:
        return self._arguments_collection.to_data()

    def set_arguments_data(self, data: list[ArgumentData]) -> None:
        self._arguments_collection.from_data(data)
    
    def set_argument(self, name: str, value: str) -> bool:
        return self._arguments_collection.set_argument(name, value)
    
    def clear_arguments(self) -> None:
        self._arguments_collection.clear()
    
    def print_info(self) -> None:
        SLog.log(f"=== LdapRequestDefaults: {self.testname} ===")
        SLog.log(f"  enabled: {self.enabled}")
        SLog.log(f"  comment: {self.comment.value}")
        SLog.log(f"  servername: {self.servername.value}")
        SLog.log(f"  port: {self.port.value}")
        SLog.log(f"  rootdn: {self.rootdn.value}")
        SLog.log(f"  user_defined: {self.user_defined.value}")
        SLog.log(f"  test: {self.test.value}")
        SLog.log(f"  base_entry_dn: {self.base_entry_dn.value}")
        SLog.log(f"  arguments: {len(self._arguments_collection.items)}")
        for arg in self._arguments_collection.items:
            name_prop = next((p for p in arg.properties if p.name == ARGUMENT_NAME), None)
            value_prop = next((p for p in arg.properties if p.name == ARGUMENT_VALUE), None)
            if name_prop and value_prop:
                SLog.log(f"    {name_prop.value} = {value_prop.value}")
        SLog.log(f"  children: {len(self.children)}")


class LoginConfigElement(TreeElement):
    category: CategoryElement = CategoryElement.CONFIG_ELEMENT
    
    def __init__(
        self,
        testname: str = "Login Config Element",
        enabled: bool = True
    ):
        self.username: StringProp = StringProp(LOGINCONFIG_USERNAME, "")
        self.password: StringProp = StringProp(LOGINCONFIG_PASSWORD, "")
        
        super().__init__(
            testname=testname,
            enabled=enabled,
            properties=[
                self.username,
                self.password
            ]
        )
    
    @property
    def tag_name(self) -> str:
        return "ConfigTestElement"
    
    @property
    def guiclass(self) -> str:
        return "LoginConfigGui"
    
    @property
    def testclass(self) -> str:
        return "ConfigTestElement"
    
    @staticmethod
    def create_default(testname: str = "Login Config Element") -> "LoginConfigElement":
        return LoginConfigElement(testname=testname)
    
    def set_username(self, username: str) -> None:
        self.username.value = username
    
    def set_password(self, password: str) -> None:
        self.password.value = password
    
    def print_info(self) -> None:
        SLog.log(f"=== LoginConfigElement: {self.testname} ===")
        SLog.log(f"  enabled: {self.enabled}")
        SLog.log(f"  comment: {self.comment.value}")
        SLog.log(f"  username: {self.username.value}")
        SLog.log(f"  password: {'*' * len(self.password.value) if self.password.value else '(empty)'}")
        SLog.log(f"  children: {len(self.children)}")


class SimpleConfigElement(TreeElement):
    category: CategoryElement = CategoryElement.CONFIG_ELEMENT
    
    def __init__(
        self,
        testname: str = "Simple Config Element",
        enabled: bool = True
    ):
        self._custom_props: dict[str, StringProp] = {}
        
        super().__init__(
            testname=testname,
            enabled=enabled,
            properties=[]
        )
    
    @property
    def tag_name(self) -> str:
        return "ConfigTestElement"
    
    @property
    def guiclass(self) -> str:
        return "SimpleConfigGui"
    
    @property
    def testclass(self) -> str:
        return "ConfigTestElement"
    
    @staticmethod
    def create_default(testname: str = "Simple Config Element") -> "SimpleConfigElement":
        return SimpleConfigElement(testname=testname)
    
    def add_property(self, name: str, value: str) -> None:
        if name in self._custom_props:
            self._custom_props[name].value = value
        else:
            prop = StringProp(name, value)
            self._custom_props[name] = prop
            self.properties.append(prop)
    
    def remove_property(self, name: str) -> None:
        if name in self._custom_props:
            prop = self._custom_props.pop(name)
            self.properties.remove(prop)
    
    def get_property(self, name: str) -> str | None:
        if name in self._custom_props:
            return self._custom_props[name].value
        return None
    
    def get_all_properties(self) -> dict[str, str]:
        return {name: prop.value for name, prop in self._custom_props.items()}
    
    def clear_properties(self) -> None:
        for prop in self._custom_props.values():
            self.properties.remove(prop)
        self._custom_props.clear()
    
    def print_info(self) -> None:
        SLog.log(f"=== SimpleConfigElement: {self.testname} ===")
        SLog.log(f"  enabled: {self.enabled}")
        SLog.log(f"  comment: {self.comment.value}")
        SLog.log(f"  custom properties: {len(self._custom_props)}")
        for name, prop in self._custom_props.items():
            SLog.log(f"    {name} = {prop.value}")
        SLog.log(f"  children: {len(self.children)}")


class TcpSamplerConfig(TreeElement):
    category: CategoryElement = CategoryElement.CONFIG_ELEMENT
    
    def __init__(
        self,
        testname: str = "TCP Sampler Config",
        enabled: bool = True
    ):
        self.server: StringProp = StringProp(TCPSAMPLER_SERVER, "")
        self.port: StringProp = StringProp(TCPSAMPLER_PORT, "")
        self.reuse_connection: BoolProp = BoolProp(TCPSAMPLER_REUSE_CONNECTION, True)
        self.nodelay: BoolProp = BoolProp(TCPSAMPLER_NODELAY, False)
        self.timeout: StringProp = StringProp(TCPSAMPLER_TIMEOUT, "")
        self.request: StringProp = StringProp(TCPSAMPLER_REQUEST, "")
        self.close_connection: BoolProp = BoolProp(TCPSAMPLER_CLOSE_CONNECTION, False)
        self.classname: StringProp = StringProp(TCPSAMPLER_CLASSNAME, "")
        self.ctimeout: StringProp = StringProp(TCPSAMPLER_CTIMEOUT, "")
        self.so_linger: StringProp = StringProp(TCPSAMPLER_SO_LINGER, "")
        self.eol_byte: StringProp = StringProp(TCPSAMPLER_EOL_BYTE, "")
        
        super().__init__(
            testname=testname,
            enabled=enabled,
            properties=[
                self.server,
                self.reuse_connection,
                self.port,
                self.nodelay,
                self.timeout,
                self.request,
                self.close_connection,
                self.classname,
                self.ctimeout,
                self.so_linger,
                self.eol_byte
            ]
        )
    
    @property
    def tag_name(self) -> str:
        return "ConfigTestElement"
    
    @property
    def guiclass(self) -> str:
        return "TCPConfigGui"
    
    @property
    def testclass(self) -> str:
        return "ConfigTestElement"
    
    @staticmethod
    def create_default(testname: str = "TCP Sampler Config") -> "TcpSamplerConfig":
        return TcpSamplerConfig(testname=testname)
    
    def set_server(self, server: str) -> None:
        self.server.value = server
    
    def set_port(self, port: str) -> None:
        self.port.value = port
    
    def set_reuse_connection(self, reuse: bool) -> None:
        self.reuse_connection.value = reuse
    
    def set_nodelay(self, nodelay: bool) -> None:
        self.nodelay.value = nodelay
    
    def set_timeout(self, timeout: str) -> None:
        self.timeout.value = timeout
    
    def set_request(self, request: str) -> None:
        self.request.value = request
    
    def set_close_connection(self, close: bool) -> None:
        self.close_connection.value = close
    
    def set_classname(self, classname: str) -> None:
        self.classname.value = classname
    
    def set_ctimeout(self, ctimeout: str) -> None:
        self.ctimeout.value = ctimeout
    
    def set_so_linger(self, so_linger: str) -> None:
        self.so_linger.value = so_linger
    
    def set_eol_byte(self, eol_byte: str) -> None:
        self.eol_byte.value = eol_byte
    
    def print_info(self) -> None:
        SLog.log(f"=== TcpSamplerConfig: {self.testname} ===")
        SLog.log(f"  enabled: {self.enabled}")
        SLog.log(f"  comment: {self.comment.value}")
        SLog.log(f"  server: {self.server.value}")
        SLog.log(f"  port: {self.port.value}")
        SLog.log(f"  reuse_connection: {self.reuse_connection.value}")
        SLog.log(f"  nodelay: {self.nodelay.value}")
        SLog.log(f"  timeout: {self.timeout.value}")
        SLog.log(f"  request: {self.request.value}")
        SLog.log(f"  close_connection: {self.close_connection.value}")
        SLog.log(f"  classname: {self.classname.value}")
        SLog.log(f"  ctimeout: {self.ctimeout.value}")
        SLog.log(f"  so_linger: {self.so_linger.value}")
        SLog.log(f"  eol_byte: {self.eol_byte.value}")
        SLog.log(f"  children: {len(self.children)}")


class KeystoreConfig(TreeElement):
    category: CategoryElement = CategoryElement.CONFIG_ELEMENT
    
    def __init__(
        self,
        testname: str = "Keystore Configuration",
        enabled: bool = True
    ):
        self.client_cert_alias_var_name: StringProp = StringProp(KEYSTORECONFIG_CLIENT_CERT_ALIAS_VAR_NAME, "")
        self.end_index: StringProp = StringProp(KEYSTORECONFIG_END_INDEX, "")
        self.preload: StringProp = StringProp(KEYSTORECONFIG_PRELOAD, "True")
        self.start_index: StringProp = StringProp(KEYSTORECONFIG_START_INDEX, "")
        
        super().__init__(
            testname=testname,
            enabled=enabled,
            properties=[
                self.client_cert_alias_var_name,
                self.end_index,
                self.preload,
                self.start_index
            ]
        )
    
    @property
    def tag_name(self) -> str:
        return "KeystoreConfig"
    
    @property
    def guiclass(self) -> str:
        return "TestBeanGUI"
    
    @property
    def testclass(self) -> str:
        return "KeystoreConfig"
    
    @staticmethod
    def create_default(testname: str = "Keystore Configuration") -> "KeystoreConfig":
        return KeystoreConfig(testname=testname)
    
    def set_client_cert_alias_var_name(self, var_name: str) -> None:
        self.client_cert_alias_var_name.value = var_name
    
    def set_end_index(self, end_index: str) -> None:
        self.end_index.value = end_index
    
    def set_preload(self, preload: bool) -> None:
        self.preload.value = str(preload)
    
    def set_start_index(self, start_index: str) -> None:
        self.start_index.value = start_index
    
    def print_info(self) -> None:
        SLog.log(f"=== KeystoreConfig: {self.testname} ===")
        SLog.log(f"  enabled: {self.enabled}")
        SLog.log(f"  comment: {self.comment.value}")
        SLog.log(f"  client_cert_alias_var_name: {self.client_cert_alias_var_name.value}")
        SLog.log(f"  start_index: {self.start_index.value}")
        SLog.log(f"  end_index: {self.end_index.value}")
        SLog.log(f"  preload: {self.preload.value}")
        SLog.log(f"  children: {len(self.children)}")


class AuthorizationMechanism(Enum):
    BASIC = "BASIC"
    BASIC_DIGEST = "BASIC_DIGEST"
    DIGEST = "DIGEST"
    KERBEROS = "KERBEROS"
    

class AuthManager(TreeElement):
    category: CategoryElement = CategoryElement.CONFIG_ELEMENT
    
    def __init__(
        self,
        testname: str = "HTTP Authorization Manager",
        enabled: bool = True
    ):
        self._auth_list: AuthorizationsProp = AuthorizationsProp(AUTHMANAGER_AUTH_LIST)
        self.controlled_by_threadgroup: BoolProp = BoolProp(AUTHMANAGER_CONTROLLED_BY_THREADGROUP, False)
        self.clear_each_iteration: BoolProp = BoolProp(AUTHMANAGER_CLEAR_EACH_ITERATION, False)
        
        super().__init__(
            testname=testname,
            enabled=enabled,
            properties=[
                self._auth_list,
                self.controlled_by_threadgroup,
                self.clear_each_iteration
            ]
        )
    
    @property
    def tag_name(self) -> str:
        return "AuthManager"
    
    @property
    def guiclass(self) -> str:
        return "AuthPanel"
    
    @property
    def testclass(self) -> str:
        return "AuthManager"
    
    @staticmethod
    def create_default(testname: str = "HTTP Authorization Manager") -> "AuthManager":
        return AuthManager(testname=testname)
    
    def add_authorization(
        self,
        url: str,
        username: str,
        password: str,
        domain: str = "",
        realm: str = "",
        mechanism: str = "BASIC"
    ) -> None:
        self._auth_list.add_authorization(url, username, password, domain, realm, mechanism)
    
    def add_authorization_typed(
        self,
        url: str,
        username: str,
        password: str,
        domain: str = "",
        realm: str = "",
        mechanism: AuthorizationMechanism = AuthorizationMechanism.BASIC
    ) -> None:
        self._auth_list.add_authorization(url, username, password, domain, realm, mechanism.value)
    
    def remove_authorization(self, url: str) -> None:
        self._auth_list.remove_authorization(url)
    
    def get_authorization(self, url: str) -> ElementProp | None:
        return self._auth_list.get_authorization(url)
    
    def get_authorization_username(self, url: str) -> str | None:
        return self._auth_list.get_authorization_username(url)

    def get_authorization_mechanism(self, url: str) -> str | None:
        return self._auth_list.get_authorization_mechanism(url)

    def has_authorization(self, url: str) -> bool:
        return self._auth_list.has_authorization(url)

    def get_authorizations_data(self) -> list[AuthorizationData]:
        return self._auth_list.to_data()

    def set_authorizations_data(self, data: list[AuthorizationData]) -> None:
        self._auth_list.from_data(data)
    
    def clear_authorizations(self) -> None:
        self._auth_list.clear()
    
    def set_controlled_by_threadgroup(self, controlled: bool) -> None:
        self.controlled_by_threadgroup.value = controlled
    
    def set_clear_each_iteration(self, clear: bool) -> None:
        self.clear_each_iteration.value = clear
    
    def print_info(self) -> None:
        SLog.log(f"=== AuthManager: {self.testname} ===")
        SLog.log(f"  enabled: {self.enabled}")
        SLog.log(f"  comment: {self.comment.value}")
        SLog.log(f"  controlled_by_threadgroup: {self.controlled_by_threadgroup.value}")
        SLog.log(f"  clear_each_iteration: {self.clear_each_iteration.value}")
        SLog.log(f"  authorizations: {len(self._auth_list.items)}")
        for auth in self._auth_list.items:
            url_prop = next((p for p in auth.properties if p.name == AUTHORIZATION_URL), None)
            username_prop = next((p for p in auth.properties if p.name == AUTHORIZATION_USERNAME), None)
            mechanism_prop = next((p for p in auth.properties if p.name == AUTHORIZATION_MECHANISM), None)
            if url_prop and username_prop:
                mechanism_str = mechanism_prop.value if mechanism_prop else "BASIC"
                SLog.log(f"    {url_prop.value} -> {username_prop.value} ({mechanism_str})")
        SLog.log(f"  children: {len(self.children)}")


class JDBCTransactionIsolation(Enum):
    DEFAULT = "DEFAULT"
    TRANSACTION_NONE = "TRANSACTION_NONE"
    TRANSACTION_READ_UNCOMMITTED = "TRANSACTION_READ_UNCOMMITTED"
    TRANSACTION_READ_COMMITTED = "TRANSACTION_READ_COMMITTED"
    TRANSACTION_REPEATABLE_READ = "TRANSACTION_REPEATABLE_READ"
    TRANSACTION_SERIALIZABLE = "TRANSACTION_SERIALIZABLE"


class JDBCCheckQuery(Enum):
    HSQLDB = "select 1 from INFORMATION_SCHEMA.SYSTEM_USERS"
    ORACLE = "select 1 from dual"
    DB2 = "select 1 from sysibm.sysdummy1"
    GENERIC = "select 1"
    FIREBIRD = "select 1 from rdb$database"


class JDBCDataSource(TreeElement):
    category: CategoryElement = CategoryElement.CONFIG_ELEMENT
    
    def __init__(
        self,
        testname: str = "JDBC Connection Configuration",
        enabled: bool = True
    ):
        self.autocommit: BoolProp = BoolProp(JDBCDATASOURCE_AUTOCOMMIT, True)
        self.check_query: StringProp = StringProp(JDBCDATASOURCE_CHECK_QUERY, "")
        self.connection_age: StringProp = StringProp(JDBCDATASOURCE_CONNECTION_AGE, "5000")
        self.connection_properties: StringProp = StringProp(JDBCDATASOURCE_CONNECTION_PROPERTIES, "")
        self.datasource: StringProp = StringProp(JDBCDATASOURCE_DATASOURCE, "")
        self.db_url: StringProp = StringProp(JDBCDATASOURCE_DB_URL, "")
        self.driver: StringProp = StringProp(JDBCDATASOURCE_DRIVER, "")
        self.init_query: StringProp = StringProp(JDBCDATASOURCE_INIT_QUERY, "")
        self.keep_alive: BoolProp = BoolProp(JDBCDATASOURCE_KEEP_ALIVE, True)
        self.password: StringProp = StringProp(JDBCDATASOURCE_PASSWORD, "")
        self.pool_max: StringProp = StringProp(JDBCDATASOURCE_POOL_MAX, "0")
        self.preinit: BoolProp = BoolProp(JDBCDATASOURCE_PREINIT, False)
        self.timeout: StringProp = StringProp(JDBCDATASOURCE_TIMEOUT, "10000")
        self.transaction_isolation: StringProp = StringProp(JDBCDATASOURCE_TRANSACTION_ISOLATION, "DEFAULT")
        self.trim_interval: StringProp = StringProp(JDBCDATASOURCE_TRIM_INTERVAL, "60000")
        self.username: StringProp = StringProp(JDBCDATASOURCE_USERNAME, "")
        self.pool_prepared_statements: StringProp = StringProp(JDBCDATASOURCE_POOL_PREPARED_STATEMENTS, "")
        
        super().__init__(
            testname=testname,
            enabled=enabled,
            properties=[
                self.autocommit,
                self.check_query,
                self.connection_age,
                self.connection_properties,
                self.datasource,
                self.db_url,
                self.driver,
                self.init_query,
                self.keep_alive,
                self.password,
                self.pool_max,
                self.preinit,
                self.timeout,
                self.transaction_isolation,
                self.trim_interval,
                self.username,
                self.pool_prepared_statements
            ]
        )
    
    @property
    def tag_name(self) -> str:
        return "JDBCDataSource"
    
    @property
    def guiclass(self) -> str:
        return "TestBeanGUI"
    
    @property
    def testclass(self) -> str:
        return "JDBCDataSource"
    
    @staticmethod
    def create_default(testname: str = "JDBC Connection Configuration") -> "JDBCDataSource":
        return JDBCDataSource(testname=testname)
    
    def set_autocommit(self, autocommit: bool) -> None:
        self.autocommit.value = autocommit
    
    def set_check_query(self, query: str) -> None:
        self.check_query.value = query
    
    def set_check_query_typed(self, query: JDBCCheckQuery) -> None:
        self.check_query.value = query.value
    
    def set_connection_age(self, age: str) -> None:
        self.connection_age.value = age
    
    def set_connection_properties(self, properties: str) -> None:
        self.connection_properties.value = properties
    
    def set_datasource(self, datasource: str) -> None:
        self.datasource.value = datasource
    
    def set_db_url(self, url: str) -> None:
        self.db_url.value = url
    
    def set_driver(self, driver: str) -> None:
        self.driver.value = driver
    
    def set_init_query(self, query: str) -> None:
        self.init_query.value = query
    
    def set_keep_alive(self, keep_alive: bool) -> None:
        self.keep_alive.value = keep_alive
    
    def set_password(self, password: str) -> None:
        self.password.value = password
    
    def set_pool_max(self, pool_max: str) -> None:
        self.pool_max.value = pool_max
    
    def set_preinit(self, preinit: bool) -> None:
        self.preinit.value = preinit
    
    def set_timeout(self, timeout: str) -> None:
        self.timeout.value = timeout
    
    def set_transaction_isolation(self, isolation: str) -> None:
        self.transaction_isolation.value = isolation
    
    def set_transaction_isolation_typed(self, isolation: JDBCTransactionIsolation) -> None:
        self.transaction_isolation.value = isolation.value
    
    def set_trim_interval(self, interval: str) -> None:
        self.trim_interval.value = interval
    
    def set_username(self, username: str) -> None:
        self.username.value = username
    
    def set_pool_prepared_statements(self, count: str) -> None:
        self.pool_prepared_statements.value = count
    
    def print_info(self) -> None:
        SLog.log(f"=== JDBCDataSource: {self.testname} ===")
        SLog.log(f"  enabled: {self.enabled}")
        SLog.log(f"  comment: {self.comment.value}")
        SLog.log(f"  datasource: {self.datasource.value}")
        SLog.log(f"  db_url: {self.db_url.value}")
        SLog.log(f"  driver: {self.driver.value}")
        SLog.log(f"  username: {self.username.value}")
        SLog.log(f"  password: {'*' * len(self.password.value) if self.password.value else '(empty)'}")
        SLog.log(f"  autocommit: {self.autocommit.value}")
        SLog.log(f"  keep_alive: {self.keep_alive.value}")
        SLog.log(f"  preinit: {self.preinit.value}")
        SLog.log(f"  pool_max: {self.pool_max.value}")
        SLog.log(f"  pool_prepared_statements: {self.pool_prepared_statements.value}")
        SLog.log(f"  timeout: {self.timeout.value}")
        SLog.log(f"  connection_age: {self.connection_age.value}")
        SLog.log(f"  trim_interval: {self.trim_interval.value}")
        SLog.log(f"  transaction_isolation: {self.transaction_isolation.value}")
        SLog.log(f"  check_query: {self.check_query.value}")
        SLog.log(f"  init_query: {self.init_query.value}")
        SLog.log(f"  connection_properties: {self.connection_properties.value}")
        SLog.log(f"  children: {len(self.children)}")


class JavaTestClass(Enum):
    JAVA_TEST = "org.apache.jmeter.protocol.java.test.JavaTest"
    SLEEP_TEST = "org.apache.jmeter.protocol.java.test.SleepTest"


class JavaConfig(TreeElement):
    category: CategoryElement = CategoryElement.CONFIG_ELEMENT
    
    def __init__(
        self,
        testname: str = "Java Request Defaults",
        enabled: bool = True
    ):
        self._arguments_collection: ArgumentsProp = ArgumentsProp()
        self._arguments: ElementProp = ElementProp(
            name=JAVACONFIG_ARGUMENTS,
            element_type="Arguments",
            guiclass="ArgumentsPanel",
            testclass="Arguments",
            properties=[self._arguments_collection]
        )
        self.classname: StringProp = StringProp(JAVACONFIG_CLASSNAME, JavaTestClass.JAVA_TEST.value)
        
        super().__init__(
            testname=testname,
            enabled=enabled,
            properties=[
                self._arguments,
                self.classname
            ]
        )
    
    @property
    def tag_name(self) -> str:
        return "JavaConfig"
    
    @property
    def guiclass(self) -> str:
        return "JavaConfigGui"
    
    @property
    def testclass(self) -> str:
        return "JavaConfig"
    
    @staticmethod
    def create_default(testname: str = "Java Request Defaults") -> "JavaConfig":
        return JavaConfig(testname=testname)
    
    def set_classname(self, classname: str) -> None:
        self.classname.value = classname
    
    def set_classname_typed(self, classname: JavaTestClass) -> None:
        self.classname.value = classname.value
    
    def add_argument(self, name: str, value: str) -> None:
        self._arguments_collection.add_argument(name, value)
    
    def remove_argument(self, name: str) -> None:
        self._arguments_collection.remove_argument(name)
    
    def get_argument(self, name: str) -> ElementProp | None:
        return self._arguments_collection.get_argument(name)
    
    def get_argument_value(self, name: str) -> str | None:
        return self._arguments_collection.get_argument_value(name)

    def has_argument(self, name: str, value: str | None = None) -> bool:
        return self._arguments_collection.has_argument(name, value)

    def get_arguments_data(self) -> list[ArgumentData]:
        return self._arguments_collection.to_data()

    def set_arguments_data(self, data: list[ArgumentData]) -> None:
        self._arguments_collection.from_data(data)
    
    def set_argument(self, name: str, value: str) -> bool:
        return self._arguments_collection.set_argument(name, value)
    
    def clear_arguments(self) -> None:
        self._arguments_collection.clear()
    
    def print_info(self) -> None:
        SLog.log(f"=== JavaConfig: {self.testname} ===")
        SLog.log(f"  enabled: {self.enabled}")
        SLog.log(f"  comment: {self.comment.value}")
        SLog.log(f"  classname: {self.classname.value}")
        SLog.log(f"  arguments: {len(self._arguments_collection.items)}")
        for arg in self._arguments_collection.items:
            name_prop = next((p for p in arg.properties if p.name == ARGUMENT_NAME), None)
            value_prop = next((p for p in arg.properties if p.name == ARGUMENT_VALUE), None)
            if name_prop and value_prop:
                SLog.log(f"    {name_prop.value} = {value_prop.value}")
        SLog.log(f"  children: {len(self.children)}")


class DNSCacheManager(TreeElement):
    category: CategoryElement = CategoryElement.CONFIG_ELEMENT
    
    def __init__(
        self,
        testname: str = "DNS Cache Manager",
        enabled: bool = True
    ):
        self._servers: DNSServersProp = DNSServersProp(DNSCACHEMANAGER_SERVERS)
        self._hosts: DNSHostsProp = DNSHostsProp(DNSCACHEMANAGER_HOSTS)
        self.clear_each_iteration: BoolProp = BoolProp(DNSCACHEMANAGER_CLEAR_EACH_ITERATION, False)
        self.is_custom_resolver: BoolProp = BoolProp(DNSCACHEMANAGER_IS_CUSTOM_RESOLVER, False)
        
        super().__init__(
            testname=testname,
            enabled=enabled,
            properties=[
                self._servers,
                self._hosts,
                self.clear_each_iteration,
                self.is_custom_resolver
            ]
        )
    
    @property
    def tag_name(self) -> str:
        return "DNSCacheManager"
    
    @property
    def guiclass(self) -> str:
        return "DNSCachePanel"
    
    @property
    def testclass(self) -> str:
        return "DNSCacheManager"
    
    @staticmethod
    def create_default(testname: str = "DNS Cache Manager") -> "DNSCacheManager":
        return DNSCacheManager(testname=testname)
    
    def add_server(self, server: str) -> None:
        self._servers.add_server(server)
    
    def remove_server(self, server: str) -> None:
        self._servers.remove_server(server)
    
    def get_servers(self) -> list[str]:
        return self._servers.get_servers()
    
    def clear_servers(self) -> None:
        self._servers.clear()
    
    def add_host(self, hostname: str, address: str) -> None:
        self._hosts.add_host(hostname, address)
    
    def remove_host(self, hostname: str) -> None:
        self._hosts.remove_host(hostname)
    
    def get_host(self, hostname: str) -> ElementProp | None:
        return self._hosts.get_host(hostname)
    
    def clear_hosts(self) -> None:
        self._hosts.clear()
    
    def set_clear_each_iteration(self, clear: bool) -> None:
        self.clear_each_iteration.value = clear
    
    def set_is_custom_resolver(self, custom: bool) -> None:
        self.is_custom_resolver.value = custom
    
    def get_host_address(self, hostname: str) -> str | None:
        return self._hosts.get_host_address(hostname)

    def has_host(self, hostname: str, address: str | None = None) -> bool:
        return self._hosts.has_host(hostname, address)

    def get_hosts_data(self) -> list[DNSHostData]:
        return self._hosts.to_data()

    def set_hosts_data(self, data: list[DNSHostData]) -> None:
        self._hosts.from_data(data)
    
    def print_info(self) -> None:
        SLog.log(f"=== DNSCacheManager: {self.testname} ===")
        SLog.log(f"  enabled: {self.enabled}")
        SLog.log(f"  comment: {self.comment.value}")
        SLog.log(f"  clear_each_iteration: {self.clear_each_iteration.value}")
        SLog.log(f"  is_custom_resolver: {self.is_custom_resolver.value}")
        SLog.log(f"  servers: {len(self._servers.items)}")
        for server in self._servers.get_servers():
            SLog.log(f"    {server}")
        SLog.log(f"  hosts: {len(self._hosts.items)}")
        for host in self._hosts.items:
            name_prop = next((p for p in host.properties if p.name == STATICHOST_NAME), None)
            addr_prop = next((p for p in host.properties if p.name == STATICHOST_ADDRESS), None)
            if name_prop and addr_prop:
                SLog.log(f"    {name_prop.value} -> {addr_prop.value}")
        SLog.log(f"  children: {len(self.children)}")


class HttpRequestDefaults(TreeElement):
    def __init__(
        self,
        testname: str = "HTTP Request Defaults",
        enabled: bool = True
    ):
        self.domain: StringProp = StringProp(HTTPSAMPLER_DOMAIN, "")
        self.port: StringProp = StringProp(HTTPSAMPLER_PORT, "")
        self.protocol: StringProp = StringProp(HTTPSAMPLER_PROTOCOL, "")
        self.path: StringProp = StringProp(HTTPSAMPLER_PATH, "")
        self.content_encoding: StringProp = StringProp(HTTPSAMPLER_CONTENT_ENCODING, "")
        self.connect_timeout: IntProp = IntProp(HTTPSAMPLER_CONNECT_TIMEOUT, 0)
        self.response_timeout: IntProp = IntProp(HTTPSAMPLER_RESPONSE_TIMEOUT, 0)
        
        self.image_parser: BoolProp = BoolProp(HTTPSAMPLER_IMAGE_PARSER, False)
        self.concurrent_dwn: BoolProp = BoolProp(HTTPSAMPLER_CONCURRENT_DWN, False)
        self.concurrent_pool: IntProp = IntProp(HTTPSAMPLER_CONCURRENT_POOL, 6)
        self.md5: BoolProp = BoolProp(HTTPSAMPLER_MD5, False)
        self.embedded_url_re: StringProp = StringProp(HTTPSAMPLER_EMBEDDED_URL_RE, "")
        self.embedded_url_exclude_re: StringProp = StringProp(HTTPSAMPLER_EMBEDDED_URL_EXCLUDE_RE, "")
        
        self.ip_source: StringProp = StringProp(HTTPSAMPLER_IP_SOURCE, "")
        self.ip_source_type: IntProp = IntProp(HTTPSAMPLER_IP_SOURCE_TYPE, 0)
        self.implementation: StringProp = StringProp(HTTPSAMPLER_IMPLEMENTATION, "")
        
        self.proxy_scheme: StringProp = StringProp(HTTPSAMPLER_PROXY_SCHEME, "")
        self.proxy_host: StringProp = StringProp(HTTPSAMPLER_PROXY_HOST, "")
        self.proxy_port: StringProp = StringProp(HTTPSAMPLER_PROXY_PORT, "")
        self.proxy_user: StringProp = StringProp(HTTPSAMPLER_PROXY_USER, "")
        self.proxy_pass: StringProp = StringProp(HTTPSAMPLER_PROXY_PASS, "")
        
        self._post_body_raw: BoolProp = BoolProp(HTTPSAMPLER_POST_BODY_RAW, False)
        self._arguments: HTTPArgumentsProp = HTTPArgumentsProp()
        self._arguments_element: ElementProp = ElementProp(
            name=HTTPSAMPLER_ARGUMENTS,
            element_type="Arguments",
            guiclass="HTTPArgumentsPanel",
            testclass="Arguments",
            testname="User Defined Variables",
            properties=[self._arguments]
        )
        
        super().__init__(
            testname=testname,
            enabled=enabled,
            properties=[
                self.image_parser,
                self.concurrent_dwn,
                self.concurrent_pool,
                self.md5,
                self.embedded_url_re,
                self.embedded_url_exclude_re,
                self.ip_source,
                self.proxy_scheme,
                self.proxy_host,
                self.proxy_port,
                self.proxy_user,
                self.proxy_pass,
                self.connect_timeout,
                self.response_timeout,
                self.domain,
                self.port,
                self.protocol,
                self.path,
                self.content_encoding,
                self._post_body_raw,
                self._arguments_element,
                self.ip_source_type,
                self.implementation
            ]
        )
    
    @property
    def tag_name(self) -> str:
        return "ConfigTestElement"
    
    @property
    def guiclass(self) -> str:
        return "HttpDefaultsGui"
    
    @property
    def testclass(self) -> str:
        return "ConfigTestElement"
    
    @staticmethod
    def create_default(testname: str = "HTTP Request Defaults") -> "HttpRequestDefaults":
        return HttpRequestDefaults(testname=testname)
    
    def set_domain(self, domain: str) -> None:
        self.domain.value = domain
    
    def set_port(self, port: str) -> None:
        self.port.value = port
    
    def set_protocol(self, protocol: str) -> None:
        self.protocol.value = protocol
    
    def set_path(self, path: str) -> None:
        self.path.value = path
    
    def set_content_encoding(self, encoding: str) -> None:
        self.content_encoding.value = encoding
    
    def set_connect_timeout(self, timeout: int) -> None:
        self.connect_timeout.value = timeout
    
    def set_response_timeout(self, timeout: int) -> None:
        self.response_timeout.value = timeout
    
    def set_image_parser(self, enable: bool) -> None:
        self.image_parser.value = enable
    
    def set_concurrent_dwn(self, enable: bool) -> None:
        self.concurrent_dwn.value = enable
    
    def set_concurrent_pool(self, pool: int) -> None:
        self.concurrent_pool.value = pool
    
    def set_md5(self, enable: bool) -> None:
        self.md5.value = enable
    
    def set_embedded_url_re(self, regex: str) -> None:
        self.embedded_url_re.value = regex
    
    def set_embedded_url_exclude_re(self, regex: str) -> None:
        self.embedded_url_exclude_re.value = regex
    
    def set_ip_source(self, ip: str) -> None:
        self.ip_source.value = ip
    
    def set_ip_source_type(self, source_type: int) -> None:
        self.ip_source_type.value = source_type
    
    def set_ip_source_type_typed(self, source_type: IpSourceType) -> None:
        self.ip_source_type.value = source_type.value
    
    def set_implementation(self, impl: str) -> None:
        self.implementation.value = impl
    
    def set_implementation_typed(self, impl: HttpImplementation) -> None:
        self.implementation.value = impl.value
    
    def set_proxy_scheme(self, scheme: str) -> None:
        self.proxy_scheme.value = scheme
    
    def set_proxy_host(self, host: str) -> None:
        self.proxy_host.value = host
    
    def set_proxy_port(self, port: str) -> None:
        self.proxy_port.value = port
    
    def set_proxy_user(self, user: str) -> None:
        self.proxy_user.value = user
    
    def set_proxy_pass(self, password: str) -> None:
        self.proxy_pass.value = password
    
    def set_body_data(self, body: str) -> None:
        self._post_body_raw.value = True
        self._arguments.clear()
        self._arguments_element.guiclass = None
        self._arguments_element.testclass = None
        self._arguments_element.testname = None
        
        body_arg = ElementProp(
            name="",
            element_type="HTTPArgument",
            properties=[
                BoolProp(HTTPARGUMENT_ALWAYS_ENCODE, False),
                StringProp(ARGUMENT_VALUE, body),
                StringProp(ARGUMENT_METADATA, "=")
            ]
        )
        self._arguments.items.append(body_arg)
    
    def get_body_data(self) -> str | None:
        if not self._post_body_raw.value:
            return None
        if self._arguments.items:
            for prop in self._arguments.items[0].properties:
                if isinstance(prop, StringProp) and prop.name == ARGUMENT_VALUE:
                    return prop.value
        return None
    
    def add_argument(
        self,
        name: str,
        value: str,
        always_encode: bool = False,
        use_equals: bool = True
    ) -> None:
        if self._post_body_raw.value:
            self._post_body_raw.value = False
            self._arguments.clear()
            self._arguments_element.guiclass = "HTTPArgumentsPanel"
            self._arguments_element.testclass = "Arguments"
            self._arguments_element.testname = "User Defined Variables"
        
        self._arguments.add_argument(name, value, always_encode, use_equals)
    
    def remove_argument(self, name: str) -> None:
        self._arguments.remove_argument(name)
    
    def get_argument(self, name: str) -> ElementProp | None:
        return self._arguments.get_argument(name)
    
    def get_argument_value(self, name: str) -> str | None:
        return self._arguments.get_argument_value(name)

    def has_argument(self, name: str, value: str | None = None) -> bool:
        return self._arguments.has_argument(name, value)
    
    def get_arguments_data(self) -> list[HTTPArgumentData]:
        return self._arguments.to_data()

    def set_arguments_data(self, data: list[HTTPArgumentData]) -> None:
        self._arguments.from_data(data)
    
    def clear_arguments(self) -> None:
        self._arguments.clear()
    
    def print_info(self) -> None:
        SLog.log(f"=== HttpRequestDefaults: {self.testname} ===")
        SLog.log(f"  enabled: {self.enabled}")
        SLog.log(f"  comment: {self.comment.value}")
        SLog.log(f"  protocol: {self.protocol.value}")
        SLog.log(f"  domain: {self.domain.value}")
        SLog.log(f"  port: {self.port.value}")
        SLog.log(f"  path: {self.path.value}")
        SLog.log(f"  content_encoding: {self.content_encoding.value}")
        SLog.log(f"  connect_timeout: {self.connect_timeout.value}")
        SLog.log(f"  response_timeout: {self.response_timeout.value}")
        SLog.log(f"  implementation: {self.implementation.value}")
        SLog.log(f"  image_parser: {self.image_parser.value}")
        SLog.log(f"  concurrent_dwn: {self.concurrent_dwn.value}")
        SLog.log(f"  concurrent_pool: {self.concurrent_pool.value}")
        SLog.log(f"  md5: {self.md5.value}")
        SLog.log(f"  embedded_url_re: {self.embedded_url_re.value}")
        SLog.log(f"  embedded_url_exclude_re: {self.embedded_url_exclude_re.value}")
        SLog.log(f"  ip_source: {self.ip_source.value}")
        SLog.log(f"  ip_source_type: {self.ip_source_type.value}")
        SLog.log(f"  proxy_scheme: {self.proxy_scheme.value}")
        SLog.log(f"  proxy_host: {self.proxy_host.value}")
        SLog.log(f"  proxy_port: {self.proxy_port.value}")
        SLog.log(f"  proxy_user: {self.proxy_user.value}")
        SLog.log(f"  proxy_pass: {'*' * len(self.proxy_pass.value) if self.proxy_pass.value else '(empty)'}")
        SLog.log(f"  post_body_raw: {self._post_body_raw.value}")
        if self._post_body_raw.value:
            body = self.get_body_data()
            SLog.log(f"  body: {body[:50]}..." if body and len(body) > 50 else f"  body: {body}")
        else:
            SLog.log(f"  arguments: {len(self._arguments.items)}")
            for arg in self._arguments.items:
                name_prop = next((p for p in arg.properties if p.name == ARGUMENT_NAME), None)
                value_prop = next((p for p in arg.properties if p.name == ARGUMENT_VALUE), None)
                if name_prop and value_prop:
                    SLog.log(f"    {name_prop.value} = {value_prop.value}")
        SLog.log(f"  children: {len(self.children)}")


################## SAMPLERS ######################
# Flow Control Action
class TestActionTarget(Enum):
    CURRENT_THREAD = 0
    ALL_THREADS = 2


class TestActionType(Enum):
    STOP = 0
    PAUSE = 1
    STOP_NOW = 2
    START_NEXT_THREAD_LOOP = 3
    GO_TO_NEXT_LOOP_ITERATION = 4
    BREAK_CURRENT_LOOP = 5


class TestAction(TreeElement):
    category: CategoryElement = CategoryElement.SAMPLER
    
    def __init__(
        self,
        testname: str = "Think Time",
        enabled: bool = True
    ):
        self.action: IntProp = IntProp(TESTACTION_ACTION, TestActionType.PAUSE.value)
        self.target: IntProp = IntProp(TESTACTION_TARGET, TestActionTarget.CURRENT_THREAD.value)
        self.duration: StringProp = StringProp(TESTACTION_DURATION, "0")
        
        super().__init__(
            testname=testname,
            enabled=enabled,
            properties=[
                self.action,
                self.target,
                self.duration
            ]
        )
    
    @property
    def tag_name(self) -> str:
        return "TestAction"
    
    @property
    def guiclass(self) -> str:
        return "TestActionGui"
    
    @property
    def testclass(self) -> str:
        return "TestAction"
    
    @staticmethod
    def create_default(testname: str = "Flow Control Action") -> "TestAction":
        return TestAction(testname=testname)
    
    def set_action(self, action: TestActionType) -> None:
        self.action.value = action.value
    
    def set_action_raw(self, action: int) -> None:
        self.action.value = action
    
    def set_target(self, target: TestActionTarget) -> None:
        self.target.value = target.value
    
    def set_target_raw(self, target: int) -> None:
        self.target.value = target
    
    def set_duration(self, duration_ms: int) -> None:
        self.duration.value = str(duration_ms)
    
    def set_duration_raw(self, duration: str) -> None:
        self.duration.value = duration
    
    def print_info(self) -> None:
        SLog.log(f"=== TestAction: {self.testname} ===")
        SLog.log(f"  enabled: {self.enabled}")
        SLog.log(f"  comment: {self.comment.value}")
        
        action_name = "unknown"
        for a in TestActionType:
            if a.value == self.action.value:
                action_name = a.name
                break
        SLog.log(f"  action: {self.action.value} ({action_name})")
        
        target_name = "unknown"
        for t in TestActionTarget:
            if t.value == self.target.value:
                target_name = t.name
                break
        SLog.log(f"  target: {self.target.value} ({target_name})")
        
        SLog.log(f"  duration: {self.duration.value}")
        SLog.log(f"  children: {len(self.children)}")


# Http Request
class HTTPSamplerProxy(TreeElement):
    category: CategoryElement = CategoryElement.SAMPLER
    
    def __init__(
        self,
        testname: str = "HTTP Request",
        enabled: bool = True
    ):
        self.domain: StringProp = StringProp(HTTPSAMPLER_DOMAIN, "")
        self.port: StringProp = StringProp(HTTPSAMPLER_PORT, "")
        self.protocol: StringProp = StringProp(HTTPSAMPLER_PROTOCOL, "")
        self.path: StringProp = StringProp(HTTPSAMPLER_PATH, "")
        self.method: StringProp = StringProp(HTTPSAMPLER_METHOD, HttpMethod.GET.value)
        self.content_encoding: StringProp = StringProp(HTTPSAMPLER_CONTENT_ENCODING, "")
        
        self.follow_redirects: BoolProp = BoolProp(HTTPSAMPLER_FOLLOW_REDIRECTS, True)
        self.auto_redirects: BoolProp = BoolProp(HTTPSAMPLER_AUTO_REDIRECTS, False)
        self.use_keepalive: BoolProp = BoolProp(HTTPSAMPLER_USE_KEEPALIVE, True)
        self.do_multipart_post: BoolProp = BoolProp(HTTPSAMPLER_DO_MULTIPART_POST, False)
        self.browser_compatible_multipart: BoolProp = BoolProp(HTTPSAMPLER_BROWSER_COMPATIBLE_MULTIPART, False)
        
        self.connect_timeout: IntProp = IntProp(HTTPSAMPLER_CONNECT_TIMEOUT, 0)
        self.response_timeout: IntProp = IntProp(HTTPSAMPLER_RESPONSE_TIMEOUT, 0)
        
        self.image_parser: BoolProp = BoolProp(HTTPSAMPLER_IMAGE_PARSER, False)
        self.concurrent_dwn: BoolProp = BoolProp(HTTPSAMPLER_CONCURRENT_DWN, False)
        self.concurrent_pool: IntProp = IntProp(HTTPSAMPLER_CONCURRENT_POOL, 6)
        self.embedded_url_re: StringProp = StringProp(HTTPSAMPLER_EMBEDDED_URL_RE, "")
        self.embedded_url_exclude_re: StringProp = StringProp(HTTPSAMPLER_EMBEDDED_URL_EXCLUDE_RE, "")
        
        self.ip_source: StringProp = StringProp(HTTPSAMPLER_IP_SOURCE, "")
        self.ip_source_type: IntProp = IntProp(HTTPSAMPLER_IP_SOURCE_TYPE, 0)
        
        self.proxy_scheme: StringProp = StringProp(HTTPSAMPLER_PROXY_SCHEME, "")
        self.proxy_host: StringProp = StringProp(HTTPSAMPLER_PROXY_HOST, "")
        self.proxy_port: IntProp = IntProp(HTTPSAMPLER_PROXY_PORT, 0)
        self.proxy_user: StringProp = StringProp(HTTPSAMPLER_PROXY_USER, "")
        self.proxy_pass: StringProp = StringProp(HTTPSAMPLER_PROXY_PASS, "")
        
        self.implementation: StringProp = StringProp(HTTPSAMPLER_IMPLEMENTATION, "")
        self.md5: BoolProp = BoolProp(HTTPSAMPLER_MD5, False)
        
        self._post_body_raw: BoolProp = BoolProp(HTTPSAMPLER_POST_BODY_RAW, False)
        self._arguments: HTTPArgumentsProp = HTTPArgumentsProp()
        self._arguments_element: ElementProp = ElementProp(
            name=HTTPSAMPLER_ARGUMENTS,
            element_type="Arguments",
            guiclass="HTTPArgumentsPanel",
            testclass="Arguments",
            testname="User Defined Variables",
            properties=[self._arguments]
        )
        
        self._files: HTTPFileArgsProp = HTTPFileArgsProp()
        self._files_element: ElementProp = ElementProp(
            name=HTTPSAMPLER_FILES,
            element_type="HTTPFileArgs",
            properties=[self._files]
        )
        
        super().__init__(
            testname=testname,
            enabled=enabled,
            properties=[
                self.follow_redirects,
                self.method,
                self.use_keepalive,
                self._post_body_raw,
                self._arguments_element
            ]
        )
    
    @property
    def tag_name(self) -> str:
        return "HTTPSamplerProxy"
    
    @property
    def guiclass(self) -> str:
        return "HttpTestSampleGui"
    
    @property
    def testclass(self) -> str:
        return "HTTPSamplerProxy"
    
    @staticmethod
    def create_default(testname: str = "HTTP Request") -> "HTTPSamplerProxy":
        return HTTPSamplerProxy(testname=testname)
    
    def set_method(self, method: HttpMethod) -> None:
        self.method.value = method.value
    
    def set_method_raw(self, method: str) -> None:
        self.method.value = method
    
    def set_implementation(self, impl: HttpImplementation) -> None:
        self.implementation.value = impl.value
        self._ensure_property(self.implementation)
    
    def set_implementation_raw(self, impl: str) -> None:
        self.implementation.value = impl
        self._ensure_property(self.implementation)
    
    def set_redirect_type(self, redirect_type: RedirectType) -> None:
        if redirect_type == RedirectType.NONE:
            self.follow_redirects.value = False
            self.auto_redirects.value = False
        elif redirect_type == RedirectType.FOLLOW_REDIRECTS:
            self.follow_redirects.value = True
            self.auto_redirects.value = False
        elif redirect_type == RedirectType.AUTO_REDIRECTS:
            self.follow_redirects.value = False
            self.auto_redirects.value = True
        
        if self.auto_redirects.value:
            self._ensure_property(self.auto_redirects)
            self._remove_property(self.follow_redirects)
        else:
            self._ensure_property(self.follow_redirects)
            self._remove_property(self.auto_redirects)
    
    def set_ip_source_type(self, source_type: IpSourceType) -> None:
        self.ip_source_type.value = source_type.value
        self._ensure_property(self.ip_source_type)
    
    def set_ip_source_type_raw(self, source_type: int) -> None:
        self.ip_source_type.value = source_type
        self._ensure_property(self.ip_source_type)
    
    def set_ip_source(self, address: str) -> None:
        self.ip_source.value = address
        self._ensure_property(self.ip_source)
    
    def set_proxy(
        self,
        host: str,
        port: int,
        scheme: str = "",
        user: str = "",
        password: str = ""
    ) -> None:
        self.proxy_host.value = host
        self.proxy_port.value = port
        self.proxy_scheme.value = scheme
        self.proxy_user.value = user
        self.proxy_pass.value = password
        
        self._ensure_property(self.proxy_host)
        self._ensure_property(self.proxy_port)
        if scheme:
            self._ensure_property(self.proxy_scheme)
        if user:
            self._ensure_property(self.proxy_user)
        if password:
            self._ensure_property(self.proxy_pass)
    
    def set_proxy_scheme(self, scheme: str) -> None:
        self.proxy_scheme.value = scheme
        self._ensure_property(self.proxy_scheme)
    
    def set_proxy_host(self, host: str) -> None:
        self.proxy_host.value = host
        self._ensure_property(self.proxy_host)
    
    def set_proxy_port(self, port: int) -> None:
        self.proxy_port.value = port
        self._ensure_property(self.proxy_port)
    
    def set_proxy_user(self, user: str) -> None:
        self.proxy_user.value = user
        self._ensure_property(self.proxy_user)
    
    def set_proxy_pass(self, password: str) -> None:
        self.proxy_pass.value = password
        self._ensure_property(self.proxy_pass)
    
    def set_connect_timeout(self, timeout_ms: int) -> None:
        self.connect_timeout.value = timeout_ms
        self._ensure_property(self.connect_timeout)
    
    def set_response_timeout(self, timeout_ms: int) -> None:
        self.response_timeout.value = timeout_ms
        self._ensure_property(self.response_timeout)
    
    def set_retrieve_embedded_resources(self, enable: bool) -> None:
        self.image_parser.value = enable
        self._ensure_property(self.image_parser)
    
    def set_concurrent_download(self, enable: bool, pool_size: int = 6) -> None:
        self.concurrent_dwn.value = enable
        self.concurrent_pool.value = pool_size
        self._ensure_property(self.concurrent_dwn)
        if enable:
            self._ensure_property(self.concurrent_pool)
    
    def set_embedded_url_match(self, regex: str) -> None:
        self.embedded_url_re.value = regex
        self._ensure_property(self.embedded_url_re)
    
    def set_embedded_url_exclude(self, regex: str) -> None:
        self.embedded_url_exclude_re.value = regex
        self._ensure_property(self.embedded_url_exclude_re)

    def set_domain(self, domain: str) -> None:
        self.domain.value = domain
        self._ensure_property(self.domain)
    
    def set_port(self, port: str) -> None:
        self.port.value = port
        self._ensure_property(self.port)
    
    def set_protocol(self, protocol: str) -> None:
        self.protocol.value = protocol
        self._ensure_property(self.protocol)
    
    def set_path(self, path: str) -> None:
        self.path.value = path
        self._ensure_property(self.path)
    
    def set_content_encoding(self, encoding: str) -> None:
        self.content_encoding.value = encoding
        self._ensure_property(self.content_encoding)
    
    def set_use_keepalive(self, enable: bool) -> None:
        self.use_keepalive.value = enable

    def set_multipart(self, enable: bool, browser_compatible: bool = False) -> None:
        self.do_multipart_post.value = enable
        self.browser_compatible_multipart.value = browser_compatible
        self._ensure_property(self.do_multipart_post)
        if browser_compatible:
            self._ensure_property(self.browser_compatible_multipart)

    def set_md5(self, enable: bool) -> None:
        self.md5.value = enable
        self._ensure_property(self.md5)

    def set_body_data(self, body: str) -> None:
        self._post_body_raw.value = True
        self._arguments.clear()
        self._arguments_element.guiclass = None
        self._arguments_element.testclass = None
        self._arguments_element.testname = None
        
        body_argument = ElementProp(
            name="",
            element_type="HTTPArgument",
            properties=[
                BoolProp(HTTPARGUMENT_ALWAYS_ENCODE, False),
                StringProp(ARGUMENT_VALUE, body),
                StringProp(ARGUMENT_METADATA, "=")
            ]
        )
        self._arguments.items.append(body_argument)
    
    def add_argument(
        self,
        name: str,
        value: str,
        always_encode: bool = False,
        use_equals: bool = True
    ) -> None:
        if self._post_body_raw.value:
            self._post_body_raw.value = False
            self._arguments.clear()
            self._arguments_element.guiclass = "HTTPArgumentsPanel"
            self._arguments_element.testclass = "Arguments"
            self._arguments_element.testname = "User Defined Variables"
        
        self._arguments.add_argument(name, value, always_encode, use_equals)
    
    def remove_argument(self, name: str) -> None:
        self._arguments.remove_argument(name)
    
    def get_argument(self, name: str) -> ElementProp | None:
        return self._arguments.get_argument(name)
    
    def get_arguments(self) -> HTTPArgumentsProp:
        return self._arguments
    
    def get_argument_value(self, name: str) -> str | None:
        return self._arguments.get_argument_value(name)

    def has_argument(self, name: str, value: str | None = None) -> bool:
        return self._arguments.has_argument(name, value)

    def has_file(self, path: str) -> bool:
        return self._files.has_file(path)

    def get_arguments_data(self) -> list[HTTPArgumentData]:
        return self._arguments.to_data()

    def set_arguments_data(self, data: list[HTTPArgumentData]) -> None:
        self._arguments.from_data(data)

    def get_files_data(self) -> list[HTTPFileData]:
        return self._files.to_data()

    def set_files_data(self, data: list[HTTPFileData]) -> None:
        self._files.from_data(data)
    
    def clear_arguments(self) -> None:
        self._arguments.clear()

    def add_file(
        self,
        path: str,
        param_name: str = "",
        mime_type: str = "application/octet-stream"
    ) -> None:
        self._files.add_file(path, param_name, mime_type)
        self._ensure_property(self._files_element)
    
    def remove_file(self, path: str) -> None:
        self._files.remove_file(path)
        if not self._files.items:
            self._remove_property(self._files_element)
    
    def get_file(self, path: str) -> ElementProp | None:
        return self._files.get_file(path)
    
    def clear_files(self) -> None:
        self._files.clear()
        self._remove_property(self._files_element)

    def _ensure_property(self, prop: PropElement) -> None:
        if prop not in self.properties:
            self.properties.append(prop)
    
    def _remove_property(self, prop: PropElement) -> None:
        if prop in self.properties:
            self.properties.remove(prop)

    def to_data(self) -> HTTPSamplerData:
        """Извлекает все данные в простой dataclass"""
        data = HTTPSamplerData(
            testname=self.testname,
            enabled=self.enabled,
            comment=self.comment.value,
            domain=self.domain.value,
            port=self.port.value,
            protocol=self.protocol.value,
            path=self.path.value,
            method=self.method.value,
            content_encoding=self.content_encoding.value,
            follow_redirects=self.follow_redirects.value,
            auto_redirects=self.auto_redirects.value,
            use_keepalive=self.use_keepalive.value,
            do_multipart_post=self.do_multipart_post.value,
            browser_compatible_multipart=self.browser_compatible_multipart.value,
            connect_timeout=self.connect_timeout.value,
            response_timeout=self.response_timeout.value,
            image_parser=self.image_parser.value,
            concurrent_dwn=self.concurrent_dwn.value,
            concurrent_pool=self.concurrent_pool.value,
            md5=self.md5.value,
            embedded_url_re=self.embedded_url_re.value,
            embedded_url_exclude_re=self.embedded_url_exclude_re.value,
            ip_source=self.ip_source.value,
            ip_source_type=self.ip_source_type.value,
            implementation=self.implementation.value,
            proxy_scheme=self.proxy_scheme.value,
            proxy_host=self.proxy_host.value,
            proxy_port=self.proxy_port.value,
            proxy_user=self.proxy_user.value,
            proxy_pass=self.proxy_pass.value,
        )
        
        if self._post_body_raw.value:
            data.body_data = self.get_body_data()
        else:
            for arg in self._arguments.items:
                name_prop = next((p for p in arg.properties if p.name == ARGUMENT_NAME), None)
                value_prop = next((p for p in arg.properties if p.name == ARGUMENT_VALUE), None)
                always_encode_prop = next((p for p in arg.properties if p.name == HTTPARGUMENT_ALWAYS_ENCODE), None)
                use_equals_prop = next((p for p in arg.properties if p.name == HTTPARGUMENT_USE_EQUALS), None)
                
                if name_prop and value_prop:
                    data.arguments.append(HTTPArgumentData(
                        name=name_prop.value,
                        value=value_prop.value,
                        always_encode=always_encode_prop.value if always_encode_prop else False,
                        use_equals=use_equals_prop.value if use_equals_prop else True
                    ))
        
        for file_arg in self._files.items:
            path_prop = next((p for p in file_arg.properties if p.name == HTTPFILEARG_PATH), None)
            param_prop = next((p for p in file_arg.properties if p.name == HTTPFILEARG_PARAMNAME), None)
            mime_prop = next((p for p in file_arg.properties if p.name == HTTPFILEARG_MIMETYPE), None)
            
            if path_prop:
                data.files.append(HTTPFileData(
                    path=path_prop.value,
                    param_name=param_prop.value if param_prop else "",
                    mime_type=mime_prop.value if mime_prop else "application/octet-stream"
                ))
        
        return data


    def from_data(self, data: HTTPSamplerData) -> None:
        """Применяет данные из dataclass"""
        self.testname = data.testname
        self.enabled = data.enabled
        self.comment.value = data.comment
        
        self.domain.value = data.domain
        self.port.value = data.port
        self.protocol.value = data.protocol
        self.path.value = data.path
        self.method.value = data.method
        self.content_encoding.value = data.content_encoding
        
        self.follow_redirects.value = data.follow_redirects
        self.auto_redirects.value = data.auto_redirects
        self.use_keepalive.value = data.use_keepalive
        self.do_multipart_post.value = data.do_multipart_post
        self.browser_compatible_multipart.value = data.browser_compatible_multipart
        
        self.connect_timeout.value = data.connect_timeout
        self.response_timeout.value = data.response_timeout
        
        self.image_parser.value = data.image_parser
        self.concurrent_dwn.value = data.concurrent_dwn
        self.concurrent_pool.value = data.concurrent_pool
        self.md5.value = data.md5
        self.embedded_url_re.value = data.embedded_url_re
        self.embedded_url_exclude_re.value = data.embedded_url_exclude_re
        
        self.ip_source.value = data.ip_source
        self.ip_source_type.value = data.ip_source_type
        self.implementation.value = data.implementation
        
        self.proxy_scheme.value = data.proxy_scheme
        self.proxy_host.value = data.proxy_host
        self.proxy_port.value = data.proxy_port
        self.proxy_user.value = data.proxy_user
        self.proxy_pass.value = data.proxy_pass
        
        self.clear_arguments()
        self.clear_files()
        
        if data.body_data is not None:
            self.set_body_data(data.body_data)
        else:
            for arg in data.arguments:
                self.add_argument(arg.name, arg.value, arg.always_encode, arg.use_equals)
        
        for file in data.files:
            self.add_file(file.path, file.param_name, file.mime_type)


    @staticmethod
    def create_from_data(data: HTTPSamplerData) -> "HTTPSamplerProxy":
        """Создаёт новый HTTPSamplerProxy из dataclass"""
        sampler = HTTPSamplerProxy(testname=data.testname, enabled=data.enabled)
        sampler.from_data(data)
        return sampler

    def print_info(self) -> None:
        SLog.log(f"=== HTTPSamplerProxy: {self.testname} ===")
        SLog.log(f"  enabled: {self.enabled}")
        SLog.log(f"  comment: {self.comment.value}")
        SLog.log(f"  method: {self.method.value}")
        SLog.log(f"  protocol: {self.protocol.value}")
        SLog.log(f"  domain: {self.domain.value}")
        SLog.log(f"  port: {self.port.value}")
        SLog.log(f"  path: {self.path.value}")
        SLog.log(f"  content_encoding: {self.content_encoding.value}")
        SLog.log(f"  follow_redirects: {self.follow_redirects.value}")
        SLog.log(f"  auto_redirects: {self.auto_redirects.value}")
        SLog.log(f"  use_keepalive: {self.use_keepalive.value}")
        SLog.log(f"  connect_timeout: {self.connect_timeout.value}")
        SLog.log(f"  response_timeout: {self.response_timeout.value}")
        SLog.log(f"  post_body_raw: {self._post_body_raw.value}")
        SLog.log(f"  arguments: {len(self._arguments.items)}")
        for arg in self._arguments.items:
            name_prop = next((p for p in arg.properties if p.name == ARGUMENT_NAME), None)
            value_prop = next((p for p in arg.properties if p.name == ARGUMENT_VALUE), None)
            if name_prop and value_prop:
                SLog.log(f"    {name_prop.value} = {value_prop.value}")
        SLog.log(f"  files: {len(self._files.items)}")
        for file_arg in self._files.items:
            path_prop = next((p for p in file_arg.properties if p.name == HTTPFILEARG_PATH), None)
            if path_prop:
                SLog.log(f"    {path_prop.value}")
        SLog.log(f"  children: {len(self.children)}")


class DebugSampler(TreeElement):
    category: CategoryElement = CategoryElement.SAMPLER
    
    def __init__(
        self,
        testname: str = "Debug Sampler",
        enabled: bool = True
    ):
        self.display_jmeter_properties: BoolProp = BoolProp(DEBUGSAMPLER_DISPLAY_JMETER_PROPERTIES, False)
        self.display_jmeter_variables: BoolProp = BoolProp(DEBUGSAMPLER_DISPLAY_JMETER_VARIABLES, True)
        self.display_system_properties: BoolProp = BoolProp(DEBUGSAMPLER_DISPLAY_SYSTEM_PROPERTIES, False)
        
        super().__init__(
            testname=testname,
            enabled=enabled,
            properties=[
                self.display_jmeter_properties,
                self.display_jmeter_variables,
                self.display_system_properties
            ]
        )
    
    @property
    def tag_name(self) -> str:
        return "DebugSampler"
    
    @property
    def guiclass(self) -> str:
        return "TestBeanGUI"
    
    @property
    def testclass(self) -> str:
        return "DebugSampler"
    
    @staticmethod
    def create_default(testname: str = "Debug Sampler") -> "DebugSampler":
        return DebugSampler(testname=testname)
    
    def set_display_jmeter_properties(self, enable: bool) -> None:
        self.display_jmeter_properties.value = enable
    
    def set_display_jmeter_variables(self, enable: bool) -> None:
        self.display_jmeter_variables.value = enable
    
    def set_display_system_properties(self, enable: bool) -> None:
        self.display_system_properties.value = enable
    
    def print_info(self) -> None:
        SLog.log(f"=== DebugSampler: {self.testname} ===")
        SLog.log(f"  enabled: {self.enabled}")
        SLog.log(f"  comment: {self.comment.value}")
        SLog.log(f"  display_jmeter_properties: {self.display_jmeter_properties.value}")
        SLog.log(f"  display_jmeter_variables: {self.display_jmeter_variables.value}")
        SLog.log(f"  display_system_properties: {self.display_system_properties.value}")
        SLog.log(f"  children: {len(self.children)}")


class JSR223Element(TreeElement):
    category: CategoryElement = CategoryElement.SAMPLER
    
    def __init__(
        self,
        testname: str,
        enabled: bool = True
    ):
        self.script_language: StringProp = StringProp(JSR223_SCRIPT_LANGUAGE, "groovy")
        self.filename: StringProp = StringProp(JSR223_FILENAME, "")
        self.parameters: StringProp = StringProp(JSR223_PARAMETERS, "")
        self.script: StringProp = StringProp(JSR223_SCRIPT, "")
        self.cache_key: StringProp = StringProp(JSR223_CACHE_KEY, "true")
        
        super().__init__(
            testname=testname,
            enabled=enabled,
            properties=[
                self.cache_key,
                self.filename,
                self.parameters,
                self.script,
                self.script_language
            ]
        )
    
    @property
    def guiclass(self) -> str:
        return "TestBeanGUI"
    
    def set_script_language(self, language: str) -> None:
        self.script_language.value = language
    
    def set_filename(self, path: str) -> None:
        self.filename.value = path
    
    def set_parameters(self, params: str) -> None:
        self.parameters.value = params
    
    def set_script(self, script: str) -> None:
        self.script.value = script
    
    def set_cache_key(self, cache: bool) -> None:
        self.cache_key.value = "true" if cache else "false"
    
    def print_info(self) -> None:
        SLog.log(f"=== {self.tag_name}: {self.testname} ===")
        SLog.log(f"  enabled: {self.enabled}")
        SLog.log(f"  comment: {self.comment.value}")
        SLog.log(f"  script_language: {self.script_language.value}")
        SLog.log(f"  filename: {self.filename.value}")
        SLog.log(f"  parameters: {self.parameters.value}")
        SLog.log(f"  cache_key: {self.cache_key.value}")
        script_preview = self.script.value[:50] + "..." if len(self.script.value) > 50 else self.script.value
        SLog.log(f"  script: {script_preview}")
        SLog.log(f"  children: {len(self.children)}")


class JSR223Sampler(JSR223Element):
    category: CategoryElement = CategoryElement.SAMPLER
    
    def __init__(
        self,
        testname: str = "JSR223 Sampler",
        enabled: bool = True
    ):
        super().__init__(testname=testname, enabled=enabled)
    
    @property
    def tag_name(self) -> str:
        return "JSR223Sampler"
    
    @property
    def testclass(self) -> str:
        return "JSR223Sampler"
    
    @staticmethod
    def create_default(testname: str = "JSR223 Sampler") -> "JSR223Sampler":
        return JSR223Sampler(testname=testname)


################## PREPROCESS ######################
class JSR223PreProcessor(JSR223Element):
    category: CategoryElement = CategoryElement.PRE_PROCESSORS
    
    def __init__(
        self,
        testname: str = "JSR223 PreProcessor",
        enabled: bool = True
    ):
        super().__init__(testname=testname, enabled=enabled)
    
    @property
    def tag_name(self) -> str:
        return "JSR223PreProcessor"
    
    @property
    def testclass(self) -> str:
        return "JSR223PreProcessor"
    
    @staticmethod
    def create_default(testname: str = "JSR223 PreProcessor") -> "JSR223PreProcessor":
        return JSR223PreProcessor(testname=testname)



################## POSTPROCESS ######################
class JSR223PostProcessor(JSR223Element):
    category: CategoryElement = CategoryElement.POST_PROCESSORS
    
    def __init__(
        self,
        testname: str = "JSR223 PostProcessor",
        enabled: bool = True
    ):
        super().__init__(testname=testname, enabled=enabled)
    
    @property
    def tag_name(self) -> str:
        return "JSR223PostProcessor"
    
    @property
    def testclass(self) -> str:
        return "JSR223PostProcessor"
    
    @staticmethod
    def create_default(testname: str = "JSR223 PostProcessor") -> "JSR223PostProcessor":
        return JSR223PostProcessor(testname=testname)


class RegexField(Enum):
    BODY = "false"
    BODY_UNESCAPED = "unescaped"
    BODY_AS_DOCUMENT = "as_document"
    RESPONSE_HEADERS = "true"
    REQUEST_HEADERS = "request_headers"
    URL = "URL"
    RESPONSE_CODE = "code"
    RESPONSE_MESSAGE = "message"


class SampleScope(Enum):
    MAIN_AND_SUB = "all"
    MAIN_ONLY = ""
    SUB_ONLY = "children"
    VARIABLE = "variable"


class RegexExtractor(TreeElement):
    category: CategoryElement = CategoryElement.POST_PROCESSORS
    
    def __init__(
        self,
        testname: str = "Regular Expression Extractor",
        enabled: bool = True
    ):
        self.use_headers: StringProp = StringProp(REGEXEXTRACTOR_USE_HEADERS, RegexField.BODY.value)
        self.refname: StringProp = StringProp(REGEXEXTRACTOR_REFNAME, "")
        self.regex: StringProp = StringProp(REGEXEXTRACTOR_REGEX, "")
        self.template: StringProp = StringProp(REGEXEXTRACTOR_TEMPLATE, "$1$")
        self.default: StringProp = StringProp(REGEXEXTRACTOR_DEFAULT, "")
        self.default_empty_value: BoolProp = BoolProp(REGEXEXTRACTOR_DEFAULT_EMPTY_VALUE, False)
        self.match_number: StringProp = StringProp(REGEXEXTRACTOR_MATCH_NUMBER, "1")
        #self.scope: StringProp = StringProp(SAMPLE_SCOPE, "")
        self.scope_variable: StringProp = StringProp(SCOPE_VARIABLE, "")
        
        super().__init__(
            testname=testname,
            enabled=enabled,
            properties=[
                self.use_headers,
                self.refname,
                self.regex,
                self.template,
                self.default,
                self.default_empty_value,
                self.match_number,
                #self.scope,
                self.scope_variable
            ]
        )
    
    @property
    def tag_name(self) -> str:
        return "RegexExtractor"
    
    @property
    def guiclass(self) -> str:
        return "RegexExtractorGui"
    
    @property
    def testclass(self) -> str:
        return "RegexExtractor"
    
    @staticmethod
    def create_default(testname: str = "Regular Expression Extractor") -> "RegexExtractor":
        return RegexExtractor(testname=testname)
    
    def set_field(self, field: RegexField) -> None:
        self.use_headers.value = field.value
    
    def set_field_raw(self, field: str) -> None:
        self.use_headers.value = field
    
    def set_refname(self, name: str) -> None:
        self.refname.value = name
    
    def set_regex(self, regex: str) -> None:
        self.regex.value = regex
    
    def set_template(self, template: str) -> None:
        self.template.value = template
    
    def set_default(self, default: str) -> None:
        self.default.value = default
    
    def set_default_empty_value(self, enable: bool) -> None:
        self.default_empty_value.value = enable
    
    def set_match_number(self, number: int) -> None:
        self.match_number.value = str(number)
    
    def set_match_number_raw(self, number: str) -> None:
        self.match_number.value = number
    
    def set_scope(self, scope: SampleScope) -> None:
        self.set_scope_raw(scope.value)
    
    def set_scope_raw(self, scope: str) -> None:
        if scope == '':
            if self.scope:
                self.properties.remove(self.scope)
                self.scope = None
        else:
            if self.scope:
                self.scope.value = scope
            else:
                self.scope = StringProp(SAMPLE_SCOPE, scope)
                self.properties.append(self.scope)
    
    def set_scope_variable(self, variable: str) -> None:
        self.scope_variable.value = variable
    
    def print_info(self) -> None:
        SLog.log(f"=== RegexExtractor: {self.testname} ===")
        SLog.log(f"  enabled: {self.enabled}")
        SLog.log(f"  comment: {self.comment.value}")
        
        field_name = "unknown"
        for f in RegexField:
            if f.value == self.use_headers.value:
                field_name = f.name
                break
        SLog.log(f"  field: {self.use_headers.value} ({field_name})")
        SLog.log(f"  refname: {self.refname.value}")
        SLog.log(f"  regex: {self.regex.value}")
        SLog.log(f"  template: {self.template.value}")
        SLog.log(f"  default: {self.default.value}")
        SLog.log(f"  default_empty_value: {self.default_empty_value.value}")
        SLog.log(f"  match_number: {self.match_number.value}")
        
        scope_name = "unknown"
        for s in SampleScope:
            if s.value == self.scope.value:
                scope_name = s.name
                break
        SLog.log(f"  scope: {self.scope.value} ({scope_name})")
        SLog.log(f"  scope_variable: {self.scope_variable.value}")
        SLog.log(f"  children: {len(self.children)}")


class JSONPostProcessor(TreeElement):
    category: CategoryElement = CategoryElement.POST_PROCESSORS
    
    def __init__(
        self,
        testname: str = "JSON Extractor",
        enabled: bool = True
    ):
        self.reference_names: StringProp = StringProp(JSONPOSTPROCESSOR_REFERENCE_NAMES, "")
        self.json_path_exprs: StringProp = StringProp(JSONPOSTPROCESSOR_JSON_PATH_EXPRS, "")
        self.match_numbers: StringProp = StringProp(JSONPOSTPROCESSOR_MATCH_NUMBERS, "")
        self.default_values: StringProp = StringProp(JSONPOSTPROCESSOR_DEFAULT_VALUES, "")
        self.compute_concat: BoolProp = BoolProp(JSONPOSTPROCESSOR_COMPUTE_CONCAT, False)
        #self.scope: StringProp = StringProp(SAMPLE_SCOPE, "")
        self.scope_variable: StringProp = StringProp(SCOPE_VARIABLE, "")
        
        super().__init__(
            testname=testname,
            enabled=enabled,
            properties=[
                self.reference_names,
                self.json_path_exprs,
                self.match_numbers,
                #self.scope,
                self.default_values,
                self.compute_concat,
                self.scope_variable
            ]
        )
    
    @property
    def tag_name(self) -> str:
        return "JSONPostProcessor"
    
    @property
    def guiclass(self) -> str:
        return "JSONPostProcessorGui"
    
    @property
    def testclass(self) -> str:
        return "JSONPostProcessor"
    
    @staticmethod
    def create_default(testname: str = "JSON Extractor") -> "JSONPostProcessor":
        return JSONPostProcessor(testname=testname)
    
    def set_reference_names(self, names: str) -> None:
        self.reference_names.value = names
    
    def set_json_path_exprs(self, exprs: str) -> None:
        self.json_path_exprs.value = exprs
    
    def set_match_numbers(self, numbers: str) -> None:
        self.match_numbers.value = numbers
    
    def set_default_values(self, defaults: str) -> None:
        self.default_values.value = defaults
    
    def set_compute_concat(self, enable: bool) -> None:
        self.compute_concat.value = enable
    
    def set_scope(self, scope: SampleScope) -> None:
        self.set_scope_raw(scope.value)
    
    def set_scope_raw(self, scope: str) -> None:
        if scope == '':
            if self.scope:
                self.properties.remove(self.scope)
                self.scope = None
        else:
            if self.scope:
                self.scope.value = scope
            else:
                self.scope = StringProp(SAMPLE_SCOPE, scope)
                self.properties.append(self.scope)
    
    def set_scope_variable(self, variable: str) -> None:
        self.scope_variable.value = variable
    
    def print_info(self) -> None:
        SLog.log(f"=== JSONPostProcessor: {self.testname} ===")
        SLog.log(f"  enabled: {self.enabled}")
        SLog.log(f"  comment: {self.comment.value}")
        SLog.log(f"  reference_names: {self.reference_names.value}")
        SLog.log(f"  json_path_exprs: {self.json_path_exprs.value}")
        SLog.log(f"  match_numbers: {self.match_numbers.value}")
        SLog.log(f"  default_values: {self.default_values.value}")
        SLog.log(f"  compute_concat: {self.compute_concat.value}")
        
        scope_name = "unknown"
        for s in SampleScope:
            if s.value == self.scope.value:
                scope_name = s.name
                break
        SLog.log(f"  scope: {self.scope.value} ({scope_name})")
        SLog.log(f"  scope_variable: {self.scope_variable.value}")
        SLog.log(f"  children: {len(self.children)}")


class CssSelectorImpl(Enum):
    JSOUP = "JSOUP"
    JODD = "JODD"


# CSS EXTRACTOR 
class HtmlExtractor(TreeElement):
    category: CategoryElement = CategoryElement.POST_PROCESSORS
    
    def __init__(
        self,
        testname: str = "CSS Selector Extractor",
        enabled: bool = True
    ):
        self.refname: StringProp = StringProp(HTMLEXTRACTOR_REFNAME, "")
        self.expr: StringProp = StringProp(HTMLEXTRACTOR_EXPR, "")
        self.attribute: StringProp = StringProp(HTMLEXTRACTOR_ATTRIBUTE, "")
        self.default: StringProp = StringProp(HTMLEXTRACTOR_DEFAULT, "")
        self.default_empty_value: BoolProp = BoolProp(HTMLEXTRACTOR_DEFAULT_EMPTY_VALUE, False)
        self.match_number: StringProp = StringProp(HTMLEXTRACTOR_MATCH_NUMBER, "")
        self.extractor_impl: StringProp = StringProp(HTMLEXTRACTOR_EXTRACTOR_IMPL, CssSelectorImpl.JSOUP.value)
        #self.scope: StringProp = StringProp(SAMPLE_SCOPE, "")
        self.scope_variable: StringProp = StringProp(SCOPE_VARIABLE, "")
        
        super().__init__(
            testname=testname,
            enabled=enabled,
            properties=[
                self.refname,
                self.expr,
                self.attribute,
                self.default,
                self.default_empty_value,
                self.match_number,
                self.extractor_impl,
                #self.scope,
                self.scope_variable
            ]
        )
    
    @property
    def tag_name(self) -> str:
        return "HtmlExtractor"
    
    @property
    def guiclass(self) -> str:
        return "HtmlExtractorGui"
    
    @property
    def testclass(self) -> str:
        return "HtmlExtractor"
    
    @staticmethod
    def create_default(testname: str = "CSS Selector Extractor") -> "HtmlExtractor":
        return HtmlExtractor(testname=testname)
    
    def set_refname(self, name: str) -> None:
        self.refname.value = name
    
    def set_expr(self, expr: str) -> None:
        self.expr.value = expr
    
    def set_attribute(self, attribute: str) -> None:
        self.attribute.value = attribute
    
    def set_default(self, default: str) -> None:
        self.default.value = default
    
    def set_default_empty_value(self, enable: bool) -> None:
        self.default_empty_value.value = enable
    
    def set_match_number(self, number: int) -> None:
        self.match_number.value = str(number)
    
    def set_match_number_raw(self, number: str) -> None:
        self.match_number.value = number
    
    def set_extractor_impl(self, impl: CssSelectorImpl) -> None:
        self.extractor_impl.value = impl.value
    
    def set_extractor_impl_raw(self, impl: str) -> None:
        self.extractor_impl.value = impl
    
    def set_scope(self, scope: SampleScope) -> None:
        self.set_scope_raw(scope.value)
    
    def set_scope_raw(self, scope: str) -> None:
        if scope == '':
            if self.scope:
                self.properties.remove(self.scope)
                self.scope = None
        else:
            if self.scope:
                self.scope.value = scope
            else:
                self.scope = StringProp(SAMPLE_SCOPE, scope)
                self.properties.append(self.scope)
    
    def set_scope_variable(self, variable: str) -> None:
        self.scope_variable.value = variable
    
    def print_info(self) -> None:
        SLog.log(f"=== HtmlExtractor: {self.testname} ===")
        SLog.log(f"  enabled: {self.enabled}")
        SLog.log(f"  comment: {self.comment.value}")
        SLog.log(f"  refname: {self.refname.value}")
        SLog.log(f"  expr: {self.expr.value}")
        SLog.log(f"  attribute: {self.attribute.value}")
        SLog.log(f"  default: {self.default.value}")
        SLog.log(f"  default_empty_value: {self.default_empty_value.value}")
        SLog.log(f"  match_number: {self.match_number.value}")
        
        impl_name = "unknown"
        for i in CssSelectorImpl:
            if i.value == self.extractor_impl.value:
                impl_name = i.name
                break
        SLog.log(f"  extractor_impl: {self.extractor_impl.value} ({impl_name})")
        
        scope_name = "unknown"
        for s in SampleScope:
            if s.value == self.scope.value:
                scope_name = s.name
                break
        SLog.log(f"  scope: {self.scope.value} ({scope_name})")
        SLog.log(f"  scope_variable: {self.scope_variable.value}")
        SLog.log(f"  children: {len(self.children)}")


class BoundaryExtractor(TreeElement):
    category: CategoryElement = CategoryElement.POST_PROCESSORS
    
    def __init__(
        self,
        testname: str = "Boundary Extractor",
        enabled: bool = True
    ):
        self.use_headers: StringProp = StringProp(BOUNDARYEXTRACTOR_USE_HEADERS, RegexField.BODY.value)
        self.refname: StringProp = StringProp(BOUNDARYEXTRACTOR_REFNAME, "")
        self.lboundary: StringProp = StringProp(BOUNDARYEXTRACTOR_LBOUNDARY, "")
        self.rboundary: StringProp = StringProp(BOUNDARYEXTRACTOR_RBOUNDARY, "")
        self.default: StringProp = StringProp(BOUNDARYEXTRACTOR_DEFAULT, "")
        self.default_empty_value: BoolProp = BoolProp(BOUNDARYEXTRACTOR_DEFAULT_EMPTY_VALUE, False)
        self.match_number: StringProp = StringProp(BOUNDARYEXTRACTOR_MATCH_NUMBER, "1")
        #self.scope: StringProp = StringProp(SAMPLE_SCOPE, "")
        self.scope_variable: StringProp = StringProp(SCOPE_VARIABLE, "")
        
        super().__init__(
            testname=testname,
            enabled=enabled,
            properties=[
                self.use_headers,
                self.refname,
                self.lboundary,
                self.rboundary,
                self.default,
                self.default_empty_value,
                self.match_number,
                #self.scope,
                self.scope_variable
            ]
        )
    
    @property
    def tag_name(self) -> str:
        return "BoundaryExtractor"
    
    @property
    def guiclass(self) -> str:
        return "BoundaryExtractorGui"
    
    @property
    def testclass(self) -> str:
        return "BoundaryExtractor"
    
    @staticmethod
    def create_default(testname: str = "Boundary Extractor") -> "BoundaryExtractor":
        return BoundaryExtractor(testname=testname)
    
    def set_field(self, field: RegexField) -> None:
        self.use_headers.value = field.value
    
    def set_field_raw(self, field: str) -> None:
        self.use_headers.value = field
    
    def set_refname(self, name: str) -> None:
        self.refname.value = name
    
    def set_lboundary(self, boundary: str) -> None:
        self.lboundary.value = boundary
    
    def set_rboundary(self, boundary: str) -> None:
        self.rboundary.value = boundary
    
    def set_default(self, default: str) -> None:
        self.default.value = default
    
    def set_default_empty_value(self, enable: bool) -> None:
        self.default_empty_value.value = enable
    
    def set_match_number(self, number: int) -> None:
        self.match_number.value = str(number)
    
    def set_match_number_raw(self, number: str) -> None:
        self.match_number.value = number
    
    def set_scope(self, scope: SampleScope) -> None:
        self.set_scope_raw(scope.value)
    
    def set_scope_raw(self, scope: str) -> None:
        if scope == '':
            if self.scope:
                self.properties.remove(self.scope)
                self.scope = None
        else:
            if self.scope:
                self.scope.value = scope
            else:
                self.scope = StringProp(SAMPLE_SCOPE, scope)
                self.properties.append(self.scope)
    
    def set_scope_variable(self, variable: str) -> None:
        self.scope_variable.value = variable
    
    def print_info(self) -> None:
        SLog.log(f"=== BoundaryExtractor: {self.testname} ===")
        SLog.log(f"  enabled: {self.enabled}")
        SLog.log(f"  comment: {self.comment.value}")
        
        field_name = "unknown"
        for f in RegexField:
            if f.value == self.use_headers.value:
                field_name = f.name
                break
        SLog.log(f"  field: {self.use_headers.value} ({field_name})")
        SLog.log(f"  refname: {self.refname.value}")
        SLog.log(f"  lboundary: {self.lboundary.value}")
        SLog.log(f"  rboundary: {self.rboundary.value}")
        SLog.log(f"  default: {self.default.value}")
        SLog.log(f"  default_empty_value: {self.default_empty_value.value}")
        SLog.log(f"  match_number: {self.match_number.value}")
        
        scope_name = "unknown"
        for s in SampleScope:
            if s.value == self.scope.value:
                scope_name = s.name
                break
        SLog.log(f"  scope: {self.scope.value} ({scope_name})")
        SLog.log(f"  scope_variable: {self.scope_variable.value}")
        SLog.log(f"  children: {len(self.children)}")


class JMESPathExtractor(TreeElement):
    category: CategoryElement = CategoryElement.POST_PROCESSORS
    
    def __init__(
        self,
        testname: str = "JSON JMESPath Extractor",
        enabled: bool = True
    ):
        self.reference_name: StringProp = StringProp(JMESEXTRACTOR_REFERENCE_NAME, "")
        self.jmes_path_expr: StringProp = StringProp(JMESEXTRACTOR_JMES_PATH_EXPR, "")
        self.match_number: StringProp = StringProp(JMESEXTRACTOR_MATCH_NUMBER, "")
        self.default_value: StringProp = StringProp(JMESEXTRACTOR_DEFAULT_VALUE, "")
        self.scope: StringProp = StringProp(SAMPLE_SCOPE, "")
        self.scope_variable: StringProp = StringProp(SCOPE_VARIABLE, "")
        
        super().__init__(
            testname=testname,
            enabled=enabled,
            properties=[
                self.reference_name,
                self.jmes_path_expr,
                self.match_number,
                self.scope,
                self.default_value,
                self.scope_variable
            ]
        )
    
    @property
    def tag_name(self) -> str:
        return "JMESPathExtractor"
    
    @property
    def guiclass(self) -> str:
        return "JMESPathExtractorGui"
    
    @property
    def testclass(self) -> str:
        return "JMESPathExtractor"
    
    @staticmethod
    def create_default(testname: str = "JSON JMESPath Extractor") -> "JMESPathExtractor":
        return JMESPathExtractor(testname=testname)
    
    def set_reference_name(self, name: str) -> None:
        self.reference_name.value = name
    
    def set_jmes_path_expr(self, expr: str) -> None:
        self.jmes_path_expr.value = expr
    
    def set_match_number(self, number: int) -> None:
        self.match_number.value = str(number)
    
    def set_match_number_raw(self, number: str) -> None:
        self.match_number.value = number
    
    def set_default_value(self, default: str) -> None:
        self.default_value.value = default
    
    def set_scope(self, scope: SampleScope) -> None:
        self.set_scope_raw(scope.value)
    
    def set_scope_raw(self, scope: str) -> None:
        if scope == '':
            if self.scope:
                self.properties.remove(self.scope)
                self.scope = None
        else:
            if self.scope:
                self.scope.value = scope
            else:
                self.scope = StringProp(SAMPLE_SCOPE, scope)
                self.properties.append(self.scope)
    
    def set_scope_variable(self, variable: str) -> None:
        self.scope_variable.value = variable
    
    def print_info(self) -> None:
        SLog.log(f"=== JMESPathExtractor: {self.testname} ===")
        SLog.log(f"  enabled: {self.enabled}")
        SLog.log(f"  comment: {self.comment.value}")
        SLog.log(f"  reference_name: {self.reference_name.value}")
        SLog.log(f"  jmes_path_expr: {self.jmes_path_expr.value}")
        SLog.log(f"  match_number: {self.match_number.value}")
        SLog.log(f"  default_value: {self.default_value.value}")
        
        scope_name = "unknown"
        for s in SampleScope:
            if s.value == self.scope.value:
                scope_name = s.name
                break
        SLog.log(f"  scope: {self.scope.value} ({scope_name})")
        SLog.log(f"  scope_variable: {self.scope_variable.value}")
        SLog.log(f"  children: {len(self.children)}")


class DebugPostProcessor(TreeElement):
    category: CategoryElement = CategoryElement.POST_PROCESSORS
    
    def __init__(
        self,
        testname: str = "Debug PostProcessor",
        enabled: bool = True
    ):
        self.display_jmeter_properties: BoolProp = BoolProp(DEBUGPOSTPROCESSOR_DISPLAY_JMETER_PROPERTIES, False)
        self.display_jmeter_variables: BoolProp = BoolProp(DEBUGPOSTPROCESSOR_DISPLAY_JMETER_VARIABLES, True)
        self.display_sampler_properties: BoolProp = BoolProp(DEBUGPOSTPROCESSOR_DISPLAY_SAMPLER_PROPERTIES, True)
        self.display_system_properties: BoolProp = BoolProp(DEBUGPOSTPROCESSOR_DISPLAY_SYSTEM_PROPERTIES, False)
        
        super().__init__(
            testname=testname,
            enabled=enabled,
            properties=[
                self.display_jmeter_properties,
                self.display_jmeter_variables,
                self.display_sampler_properties,
                self.display_system_properties
            ]
        )
    
    @property
    def tag_name(self) -> str:
        return "DebugPostProcessor"
    
    @property
    def guiclass(self) -> str:
        return "TestBeanGUI"
    
    @property
    def testclass(self) -> str:
        return "DebugPostProcessor"
    
    @staticmethod
    def create_default(testname: str = "Debug PostProcessor") -> "DebugPostProcessor":
        return DebugPostProcessor(testname=testname)
    
    def set_display_jmeter_properties(self, enable: bool) -> None:
        self.display_jmeter_properties.value = enable
    
    def set_display_jmeter_variables(self, enable: bool) -> None:
        self.display_jmeter_variables.value = enable
    
    def set_display_sampler_properties(self, enable: bool) -> None:
        self.display_sampler_properties.value = enable
    
    def set_display_system_properties(self, enable: bool) -> None:
        self.display_system_properties.value = enable
    
    def print_info(self) -> None:
        SLog.log(f"=== DebugPostProcessor: {self.testname} ===")
        SLog.log(f"  enabled: {self.enabled}")
        SLog.log(f"  comment: {self.comment.value}")
        SLog.log(f"  display_jmeter_properties: {self.display_jmeter_properties.value}")
        SLog.log(f"  display_jmeter_variables: {self.display_jmeter_variables.value}")
        SLog.log(f"  display_sampler_properties: {self.display_sampler_properties.value}")
        SLog.log(f"  display_system_properties: {self.display_system_properties.value}")
        SLog.log(f"  children: {len(self.children)}")


class ResultActionOnError(Enum):
    CONTINUE = 0
    STOP_THREAD = 1
    STOP_TEST = 2
    STOP_TEST_NOW = 3
    START_NEXT_THREAD_LOOP = 4
    GO_TO_NEXT_ITERATION = 5
    BREAK_CURRENT_LOOP = 6


class ResultAction(TreeElement):
    category: CategoryElement = CategoryElement.POST_PROCESSORS
    
    def __init__(
        self,
        testname: str = "Result Status Action Handler",
        enabled: bool = True
    ):
        self.on_error_action: IntProp = IntProp(RESULTACTION_ON_ERROR_ACTION, ResultActionOnError.CONTINUE.value)
        
        super().__init__(
            testname=testname,
            enabled=enabled,
            properties=[
                self.on_error_action
            ]
        )
    
    @property
    def tag_name(self) -> str:
        return "ResultAction"
    
    @property
    def guiclass(self) -> str:
        return "ResultActionGui"
    
    @property
    def testclass(self) -> str:
        return "ResultAction"
    
    @staticmethod
    def create_default(testname: str = "Result Status Action Handler") -> "ResultAction":
        return ResultAction(testname=testname)
    
    def set_on_error_action(self, action: ResultActionOnError) -> None:
        self.on_error_action.value = action.value
    
    def set_on_error_action_raw(self, action: int) -> None:
        self.on_error_action.value = action
    
    def print_info(self) -> None:
        SLog.log(f"=== ResultAction: {self.testname} ===")
        SLog.log(f"  enabled: {self.enabled}")
        SLog.log(f"  comment: {self.comment.value}")
        
        action_name = "unknown"
        for a in ResultActionOnError:
            if a.value == self.on_error_action.value:
                action_name = a.name
                break
        SLog.log(f"  on_error_action: {self.on_error_action.value} ({action_name})")
        SLog.log(f"  children: {len(self.children)}")


class XPathExtractor(TreeElement):
    category: CategoryElement = CategoryElement.POST_PROCESSORS
    
    def __init__(
        self,
        testname: str = "XPath Extractor",
        enabled: bool = True
    ):
        self.default: StringProp = StringProp(XPATHEXTRACTOR_DEFAULT, "")
        self.refname: StringProp = StringProp(XPATHEXTRACTOR_REFNAME, "")
        self.match_number: StringProp = StringProp(XPATHEXTRACTOR_MATCH_NUMBER, "-1")
        self.xpath_query: StringProp = StringProp(XPATHEXTRACTOR_XPATH_QUERY, "")
        self.fragment: BoolProp = BoolProp(XPATHEXTRACTOR_FRAGMENT, True)
        self.validate: BoolProp = BoolProp(XPATHEXTRACTOR_VALIDATE, False)
        self.tolerant: BoolProp = BoolProp(XPATHEXTRACTOR_TOLERANT, False)
        self.namespace: BoolProp = BoolProp(XPATHEXTRACTOR_NAMESPACE, False)
        self.report_errors: BoolProp = BoolProp(XPATHEXTRACTOR_REPORT_ERRORS, False)
        self.show_warnings: BoolProp = BoolProp(XPATHEXTRACTOR_SHOW_WARNINGS, False)
        self.whitespace: BoolProp = BoolProp(XPATHEXTRACTOR_WHITESPACE, False)
        self.download_dtds: BoolProp = BoolProp(XPATHEXTRACTOR_DOWNLOAD_DTDS, False)
        self.scope: StringProp = StringProp(SAMPLE_SCOPE, "")
        self.scope_variable: StringProp = StringProp(SCOPE_VARIABLE, "")
        
        super().__init__(
            testname=testname,
            enabled=enabled,
            properties=[
                self.default,
                self.refname,
                self.match_number,
                self.xpath_query,
                self.fragment,
                self.validate,
                self.tolerant,
                self.namespace,
                self.report_errors,
                self.show_warnings,
                self.whitespace,
                self.download_dtds,
                self.scope,
                self.scope_variable
            ]
        )
    
    @property
    def tag_name(self) -> str:
        return "XPathExtractor"
    
    @property
    def guiclass(self) -> str:
        return "XPathExtractorGui"
    
    @property
    def testclass(self) -> str:
        return "XPathExtractor"
    
    @staticmethod
    def create_default(testname: str = "XPath Extractor") -> "XPathExtractor":
        return XPathExtractor(testname=testname)
    
    def set_default(self, default: str) -> None:
        self.default.value = default
    
    def set_refname(self, name: str) -> None:
        self.refname.value = name
    
    def set_match_number(self, number: int) -> None:
        self.match_number.value = str(number)
    
    def set_match_number_raw(self, number: str) -> None:
        self.match_number.value = number
    
    def set_xpath_query(self, query: str) -> None:
        self.xpath_query.value = query
    
    def set_fragment(self, enable: bool) -> None:
        self.fragment.value = enable
    
    def set_validate(self, enable: bool) -> None:
        self.validate.value = enable
    
    def set_tolerant(self, enable: bool) -> None:
        self.tolerant.value = enable
    
    def set_namespace(self, enable: bool) -> None:
        self.namespace.value = enable
    
    def set_report_errors(self, enable: bool) -> None:
        self.report_errors.value = enable
    
    def set_show_warnings(self, enable: bool) -> None:
        self.show_warnings.value = enable
    
    def set_whitespace(self, enable: bool) -> None:
        self.whitespace.value = enable
    
    def set_download_dtds(self, enable: bool) -> None:
        self.download_dtds.value = enable
    
    def set_scope(self, scope: SampleScope) -> None:
        self.set_scope_raw(scope.value)
    
    def set_scope_raw(self, scope: str) -> None:
        if scope == '':
            if self.scope:
                self.properties.remove(self.scope)
                self.scope = None
        else:
            if self.scope:
                self.scope.value = scope
            else:
                self.scope = StringProp(SAMPLE_SCOPE, scope)
                self.properties.append(self.scope)
    
    def set_scope_variable(self, variable: str) -> None:
        self.scope_variable.value = variable
    
    def print_info(self) -> None:
        SLog.log(f"=== XPathExtractor: {self.testname} ===")
        SLog.log(f"  enabled: {self.enabled}")
        SLog.log(f"  comment: {self.comment.value}")
        SLog.log(f"  default: {self.default.value}")
        SLog.log(f"  refname: {self.refname.value}")
        SLog.log(f"  match_number: {self.match_number.value}")
        SLog.log(f"  xpath_query: {self.xpath_query.value}")
        SLog.log(f"  fragment: {self.fragment.value}")
        SLog.log(f"  validate: {self.validate.value}")
        SLog.log(f"  tolerant: {self.tolerant.value}")
        SLog.log(f"  namespace: {self.namespace.value}")
        SLog.log(f"  report_errors: {self.report_errors.value}")
        SLog.log(f"  show_warnings: {self.show_warnings.value}")
        SLog.log(f"  whitespace: {self.whitespace.value}")
        SLog.log(f"  download_dtds: {self.download_dtds.value}")
        
        scope_name = "unknown"
        for s in SampleScope:
            if s.value == self.scope.value:
                scope_name = s.name
                break
        SLog.log(f"  scope: {self.scope.value} ({scope_name})")
        SLog.log(f"  scope_variable: {self.scope_variable.value}")
        SLog.log(f"  children: {len(self.children)}")


class XPath2Extractor(TreeElement):
    category: CategoryElement = CategoryElement.POST_PROCESSORS
    
    def __init__(
        self,
        testname: str = "XPath2 Extractor",
        enabled: bool = True
    ):
        self.default: StringProp = StringProp(XPATH2EXTRACTOR_DEFAULT, "")
        self.refname: StringProp = StringProp(XPATH2EXTRACTOR_REFNAME, "")
        self.match_number: StringProp = StringProp(XPATH2EXTRACTOR_MATCH_NUMBER, "0")
        self.xpath_query: StringProp = StringProp(XPATH2EXTRACTOR_XPATH_QUERY, "")
        self.fragment: BoolProp = BoolProp(XPATH2EXTRACTOR_FRAGMENT, True)
        self.namespaces: StringProp = StringProp(XPATH2EXTRACTOR_NAMESPACES, "")
        self.scope: StringProp = StringProp(SAMPLE_SCOPE, "")
        self.scope_variable: StringProp = StringProp(SCOPE_VARIABLE, "")
        
        super().__init__(
            testname=testname,
            enabled=enabled,
            properties=[
                self.default,
                self.refname,
                self.match_number,
                self.xpath_query,
                self.fragment,
                self.namespaces,
                self.scope,
                self.scope_variable
            ]
        )
    
    @property
    def tag_name(self) -> str:
        return "XPath2Extractor"
    
    @property
    def guiclass(self) -> str:
        return "XPath2ExtractorGui"
    
    @property
    def testclass(self) -> str:
        return "XPath2Extractor"
    
    @staticmethod
    def create_default(testname: str = "XPath2 Extractor") -> "XPath2Extractor":
        return XPath2Extractor(testname=testname)
    
    def set_default(self, default: str) -> None:
        self.default.value = default
    
    def set_refname(self, name: str) -> None:
        self.refname.value = name
    
    def set_match_number(self, number: int) -> None:
        self.match_number.value = str(number)
    
    def set_match_number_raw(self, number: str) -> None:
        self.match_number.value = number
    
    def set_xpath_query(self, query: str) -> None:
        self.xpath_query.value = query
    
    def set_fragment(self, enable: bool) -> None:
        self.fragment.value = enable
    
    def set_namespaces(self, namespaces: str) -> None:
        self.namespaces.value = namespaces
    
    def set_scope(self, scope: SampleScope) -> None:
        self.set_scope_raw(scope.value)
    
    def set_scope_raw(self, scope: str) -> None:
        if scope == '':
            if self.scope:
                self.properties.remove(self.scope)
                self.scope = None
        else:
            if self.scope:
                self.scope.value = scope
            else:
                self.scope = StringProp(SAMPLE_SCOPE, scope)
                self.properties.append(self.scope)
    
    def set_scope_variable(self, variable: str) -> None:
        self.scope_variable.value = variable
    
    def print_info(self) -> None:
        SLog.log(f"=== XPath2Extractor: {self.testname} ===")
        SLog.log(f"  enabled: {self.enabled}")
        SLog.log(f"  comment: {self.comment.value}")
        SLog.log(f"  default: {self.default.value}")
        SLog.log(f"  refname: {self.refname.value}")
        SLog.log(f"  match_number: {self.match_number.value}")
        SLog.log(f"  xpath_query: {self.xpath_query.value}")
        SLog.log(f"  fragment: {self.fragment.value}")
        SLog.log(f"  namespaces: {self.namespaces.value}")
        
        scope_name = "unknown"
        for s in SampleScope:
            if s.value == self.scope.value:
                scope_name = s.name
                break
        SLog.log(f"  scope: {self.scope.value} ({scope_name})")
        SLog.log(f"  scope_variable: {self.scope_variable.value}")
        SLog.log(f"  children: {len(self.children)}")



################## TIMERS ######################

class UniformRandomTimer(TreeElement):
    category: CategoryElement = CategoryElement.TIMER
    
    def __init__(
        self,
        testname: str = "Uniform Random Timer",
        enabled: bool = True
    ):
        self.delay: StringProp = StringProp(UNIFORMRANDOMTIMER_DELAY, "0")
        self.range: StringProp = StringProp(UNIFORMRANDOMTIMER_RANGE, "100")
        
        super().__init__(
            testname=testname,
            enabled=enabled,
            properties=[
                self.delay,
                self.range
            ]
        )
    
    @property
    def tag_name(self) -> str:
        return "UniformRandomTimer"
    
    @property
    def guiclass(self) -> str:
        return "UniformRandomTimerGui"
    
    @property
    def testclass(self) -> str:
        return "UniformRandomTimer"
    
    @staticmethod
    def create_default(testname: str = "Uniform Random Timer") -> "UniformRandomTimer":
        return UniformRandomTimer(testname=testname)
    
    def set_delay(self, delay_ms: int) -> None:
        self.delay.value = str(delay_ms)
    
    def set_delay_raw(self, delay: str) -> None:
        self.delay.value = delay
    
    def set_range(self, range_ms: int) -> None:
        self.range.value = str(range_ms)
    
    def set_range_raw(self, range_val: str) -> None:
        self.range.value = range_val
    
    def print_info(self) -> None:
        SLog.log(f"=== UniformRandomTimer: {self.testname} ===")
        SLog.log(f"  enabled: {self.enabled}")
        SLog.log(f"  comment: {self.comment.value}")
        SLog.log(f"  delay: {self.delay.value}")
        SLog.log(f"  range: {self.range.value}")
        SLog.log(f"  children: {len(self.children)}")


class ConstantTimer(TreeElement):
    category: CategoryElement = CategoryElement.TIMER
    
    def __init__(
        self,
        testname: str = "Constant Timer",
        enabled: bool = True
    ):
        self.delay: StringProp = StringProp(CONSTANTTIMER_DELAY, "300")
        
        super().__init__(
            testname=testname,
            enabled=enabled,
            properties=[
                self.delay
            ]
        )
    
    @property
    def tag_name(self) -> str:
        return "ConstantTimer"
    
    @property
    def guiclass(self) -> str:
        return "ConstantTimerGui"
    
    @property
    def testclass(self) -> str:
        return "ConstantTimer"
    
    @staticmethod
    def create_default(testname: str = "Constant Timer") -> "ConstantTimer":
        return ConstantTimer(testname=testname)
    
    def set_delay(self, delay_ms: int) -> None:
        self.delay.value = str(delay_ms)
    
    def set_delay_raw(self, delay: str) -> None:
        self.delay.value = delay
    
    def print_info(self) -> None:
        SLog.log(f"=== ConstantTimer: {self.testname} ===")
        SLog.log(f"  enabled: {self.enabled}")
        SLog.log(f"  comment: {self.comment.value}")
        SLog.log(f"  delay: {self.delay.value}")
        SLog.log(f"  children: {len(self.children)}")


class PreciseThroughputTimer(TreeElement):
    category: CategoryElement = CategoryElement.TIMER
    
    def __init__(
        self,
        testname: str = "Precise Throughput Timer",
        enabled: bool = True
    ):
        self.throughput: DoubleProp = DoubleProp(PRECISETHROUGHPUTTIMER_THROUGHPUT, 100.0)
        self.throughput_period: IntProp = IntProp(PRECISETHROUGHPUTTIMER_THROUGHPUT_PERIOD, 3600)
        self.duration: LongProp = LongProp(PRECISETHROUGHPUTTIMER_DURATION, 3600)
        self.batch_size: IntProp = IntProp(PRECISETHROUGHPUTTIMER_BATCH_SIZE, 1)
        self.batch_thread_delay: IntProp = IntProp(PRECISETHROUGHPUTTIMER_BATCH_THREAD_DELAY, 0)
        self.allowed_throughput_surplus: DoubleProp = DoubleProp(PRECISETHROUGHPUTTIMER_ALLOWED_THROUGHPUT_SURPLUS, 1.0)
        self.exact_limit: IntProp = IntProp(PRECISETHROUGHPUTTIMER_EXACT_LIMIT, 10000)
        self.random_seed: LongProp = LongProp(PRECISETHROUGHPUTTIMER_RANDOM_SEED, 0)
        
        super().__init__(
            testname=testname,
            enabled=enabled,
            properties=[
                self.allowed_throughput_surplus,
                self.batch_size,
                self.batch_thread_delay,
                self.duration,
                self.exact_limit,
                self.random_seed,
                self.throughput,
                self.throughput_period
            ]
        )
    
    @property
    def tag_name(self) -> str:
        return "PreciseThroughputTimer"
    
    @property
    def guiclass(self) -> str:
        return "TestBeanGUI"
    
    @property
    def testclass(self) -> str:
        return "PreciseThroughputTimer"
    
    @staticmethod
    def create_default(testname: str = "Precise Throughput Timer") -> "PreciseThroughputTimer":
        return PreciseThroughputTimer(testname=testname)
    
    def set_throughput(self, value: float) -> None:
        self.throughput.value = value
    
    def set_throughput_period(self, seconds: int) -> None:
        self.throughput_period.value = seconds
    
    def set_duration(self, seconds: int) -> None:
        self.duration.value = seconds
    
    def set_batch_size(self, size: int) -> None:
        self.batch_size.value = size
    
    def set_batch_thread_delay(self, delay_ms: int) -> None:
        self.batch_thread_delay.value = delay_ms
    
    def set_allowed_throughput_surplus(self, value: float) -> None:
        self.allowed_throughput_surplus.value = value
    
    def set_exact_limit(self, limit: int) -> None:
        self.exact_limit.value = limit
    
    def set_random_seed(self, seed: int) -> None:
        self.random_seed.value = seed
    
    def print_info(self) -> None:
        SLog.log(f"=== PreciseThroughputTimer: {self.testname} ===")
        SLog.log(f"  enabled: {self.enabled}")
        SLog.log(f"  comment: {self.comment.value}")
        SLog.log(f"  throughput: {self.throughput.value}")
        SLog.log(f"  throughput_period: {self.throughput_period.value}")
        SLog.log(f"  duration: {self.duration.value}")
        SLog.log(f"  batch_size: {self.batch_size.value}")
        SLog.log(f"  batch_thread_delay: {self.batch_thread_delay.value}")
        SLog.log(f"  allowed_throughput_surplus: {self.allowed_throughput_surplus.value}")
        SLog.log(f"  exact_limit: {self.exact_limit.value}")
        SLog.log(f"  random_seed: {self.random_seed.value}")
        SLog.log(f"  children: {len(self.children)}")


class ThroughputCalcMode(Enum):
    THIS_THREAD_ONLY = 0
    ALL_ACTIVE_THREADS = 1
    ALL_ACTIVE_THREADS_IN_CURRENT_GROUP = 2
    ALL_ACTIVE_THREADS_SHARED = 3
    ALL_ACTIVE_THREADS_IN_CURRENT_GROUP_SHARED = 4


class ConstantThroughputTimer(TreeElement):
    category: CategoryElement = CategoryElement.TIMER
    
    def __init__(
        self,
        testname: str = "Constant Throughput Timer",
        enabled: bool = True
    ):
        self.throughput: DoubleProp = DoubleProp(CONSTANTTHROUGHPUTTIMER_THROUGHPUT, 0.0)
        self.calc_mode: IntProp = IntProp(CONSTANTTHROUGHPUTTIMER_CALC_MODE, ThroughputCalcMode.THIS_THREAD_ONLY.value)
        
        super().__init__(
            testname=testname,
            enabled=enabled,
            properties=[
                self.calc_mode,
                self.throughput
            ]
        )
    
    @property
    def tag_name(self) -> str:
        return "ConstantThroughputTimer"
    
    @property
    def guiclass(self) -> str:
        return "TestBeanGUI"
    
    @property
    def testclass(self) -> str:
        return "ConstantThroughputTimer"
    
    @staticmethod
    def create_default(testname: str = "Constant Throughput Timer") -> "ConstantThroughputTimer":
        return ConstantThroughputTimer(testname=testname)
    
    def set_throughput(self, value: float) -> None:
        self.throughput.value = value
    
    def set_calc_mode(self, mode: ThroughputCalcMode) -> None:
        self.calc_mode.value = mode.value
    
    def set_calc_mode_raw(self, mode: int) -> None:
        self.calc_mode.value = mode
    
    def print_info(self) -> None:
        SLog.log(f"=== ConstantThroughputTimer: {self.testname} ===")
        SLog.log(f"  enabled: {self.enabled}")
        SLog.log(f"  comment: {self.comment.value}")
        SLog.log(f"  throughput: {self.throughput.value}")
        
        mode_name = "unknown"
        for m in ThroughputCalcMode:
            if m.value == self.calc_mode.value:
                mode_name = m.name
                break
        SLog.log(f"  calc_mode: {self.calc_mode.value} ({mode_name})")
        SLog.log(f"  children: {len(self.children)}")


################## LISTENERS ######################

class ViewResultsTree(TreeElement):
    category: CategoryElement = CategoryElement.LISTENER
    
    def __init__(
        self,
        testname: str = "View Results Tree",
        enabled: bool = True
    ):
        self.error_logging: BoolProp = BoolProp(RESULTCOLLECTOR_ERROR_LOGGING, False)
        self.save_config: SampleSaveConfiguration = SampleSaveConfiguration()
        self.filename: StringProp = StringProp(RESULTCOLLECTOR_FILENAME, "")
        self.success_only_logging: BoolProp = BoolProp(RESULTCOLLECTOR_SUCCESS_ONLY_LOGGING, False)
        
        super().__init__(
            testname=testname,
            enabled=enabled,
            properties=[
                self.error_logging,
                self.save_config,
                self.filename,
                self.success_only_logging
            ]
        )
    
    @property
    def tag_name(self) -> str:
        return "ResultCollector"
    
    @property
    def guiclass(self) -> str:
        return "ViewResultsFullVisualizer"
    
    @property
    def testclass(self) -> str:
        return "ResultCollector"
    
    @staticmethod
    def create_default(testname: str = "View Results Tree") -> "ViewResultsTree":
        return ViewResultsTree(testname=testname)
    
    def set_error_logging(self, enable: bool) -> None:
        self.error_logging.value = enable
    
    def set_success_only_logging(self, enable: bool) -> None:
        self.success_only_logging.value = enable
    
    def set_filename(self, filename: str) -> None:
        self.filename.value = filename
    
    def print_info(self) -> None:
        SLog.log(f"=== ViewResultsTree: {self.testname} ===")
        SLog.log(f"  enabled: {self.enabled}")
        SLog.log(f"  comment: {self.comment.value}")
        SLog.log(f"  error_logging: {self.error_logging.value}")
        SLog.log(f"  success_only_logging: {self.success_only_logging.value}")
        SLog.log(f"  filename: {self.filename.value}")
        SLog.log(f"  children: {len(self.children)}")


class SummaryReport(TreeElement):
    category: CategoryElement = CategoryElement.LISTENER
    
    def __init__(
        self,
        testname: str = "Summary Report",
        enabled: bool = True
    ):
        self.error_logging: BoolProp = BoolProp(RESULTCOLLECTOR_ERROR_LOGGING, False)
        self.save_config: SampleSaveConfiguration = SampleSaveConfiguration()
        self.filename: StringProp = StringProp(RESULTCOLLECTOR_FILENAME, "")
        self.use_group_name: BoolProp = BoolProp(RESULTCOLLECTOR_USE_GROUP_NAME, False)
        
        super().__init__(
            testname=testname,
            enabled=enabled,
            properties=[
                self.error_logging,
                self.save_config,
                self.filename,
                self.use_group_name
            ]
        )
    
    @property
    def tag_name(self) -> str:
        return "ResultCollector"
    
    @property
    def guiclass(self) -> str:
        return "SummaryReport"
    
    @property
    def testclass(self) -> str:
        return "ResultCollector"
    
    @staticmethod
    def create_default(testname: str = "Summary Report") -> "SummaryReport":
        return SummaryReport(testname=testname)
    
    def set_error_logging(self, enable: bool) -> None:
        self.error_logging.value = enable
    
    def set_filename(self, filename: str) -> None:
        self.filename.value = filename
    
    def set_use_group_name(self, enable: bool) -> None:
        self.use_group_name.value = enable
    
    def print_info(self) -> None:
        SLog.log(f"=== SummaryReport: {self.testname} ===")
        SLog.log(f"  enabled: {self.enabled}")
        SLog.log(f"  comment: {self.comment.value}")
        SLog.log(f"  error_logging: {self.error_logging.value}")
        SLog.log(f"  filename: {self.filename.value}")
        SLog.log(f"  use_group_name: {self.use_group_name.value}")
        SLog.log(f"  children: {len(self.children)}")


class AggregateReport(TreeElement):
    category: CategoryElement = CategoryElement.LISTENER
    
    def __init__(
        self,
        testname: str = "Aggregate Report",
        enabled: bool = True
    ):
        self.error_logging: BoolProp = BoolProp(RESULTCOLLECTOR_ERROR_LOGGING, False)
        self.save_config: SampleSaveConfiguration = SampleSaveConfiguration()
        self.filename: StringProp = StringProp(RESULTCOLLECTOR_FILENAME, "")
        self.use_group_name: BoolProp = BoolProp(RESULTCOLLECTOR_USE_GROUP_NAME, False)
        
        super().__init__(
            testname=testname,
            enabled=enabled,
            properties=[
                self.error_logging,
                self.save_config,
                self.filename,
                self.use_group_name
            ]
        )
    
    @property
    def tag_name(self) -> str:
        return "ResultCollector"
    
    @property
    def guiclass(self) -> str:
        return "StatVisualizer"
    
    @property
    def testclass(self) -> str:
        return "ResultCollector"
    
    @staticmethod
    def create_default(testname: str = "Aggregate Report") -> "AggregateReport":
        return AggregateReport(testname=testname)
    
    def set_error_logging(self, enable: bool) -> None:
        self.error_logging.value = enable
    
    def set_filename(self, filename: str) -> None:
        self.filename.value = filename
    
    def set_use_group_name(self, enable: bool) -> None:
        self.use_group_name.value = enable
    
    def print_info(self) -> None:
        SLog.log(f"=== AggregateReport: {self.testname} ===")
        SLog.log(f"  enabled: {self.enabled}")
        SLog.log(f"  comment: {self.comment.value}")
        SLog.log(f"  error_logging: {self.error_logging.value}")
        SLog.log(f"  filename: {self.filename.value}")
        SLog.log(f"  use_group_name: {self.use_group_name.value}")
        SLog.log(f"  children: {len(self.children)}")


class SimpleDataWriter(TreeElement):
    category: CategoryElement = CategoryElement.LISTENER
    
    def __init__(
        self,
        testname: str = "Simple Data Writer",
        enabled: bool = True
    ):
        self.error_logging: BoolProp = BoolProp(RESULTCOLLECTOR_ERROR_LOGGING, False)
        self.save_config: SampleSaveConfiguration = SampleSaveConfiguration()
        self.filename: StringProp = StringProp(RESULTCOLLECTOR_FILENAME, "")
        
        super().__init__(
            testname=testname,
            enabled=enabled,
            properties=[
                self.error_logging,
                self.save_config,
                self.filename
            ]
        )
    
    @property
    def tag_name(self) -> str:
        return "ResultCollector"
    
    @property
    def guiclass(self) -> str:
        return "SimpleDataWriter"
    
    @property
    def testclass(self) -> str:
        return "ResultCollector"
    
    @staticmethod
    def create_default(testname: str = "Simple Data Writer") -> "SimpleDataWriter":
        return SimpleDataWriter(testname=testname)
    
    def set_error_logging(self, enable: bool) -> None:
        self.error_logging.value = enable
    
    def set_filename(self, filename: str) -> None:
        self.filename.value = filename
    
    def print_info(self) -> None:
        SLog.log(f"=== SimpleDataWriter: {self.testname} ===")
        SLog.log(f"  enabled: {self.enabled}")
        SLog.log(f"  comment: {self.comment.value}")
        SLog.log(f"  error_logging: {self.error_logging.value}")
        SLog.log(f"  filename: {self.filename.value}")
        SLog.log(f"  children: {len(self.children)}")


class BackendListenerClient(Enum):
    GRAPHITE = "org.apache.jmeter.visualizers.backend.graphite.GraphiteBackendListenerClient"
    INFLUXDB_RAW = "org.apache.jmeter.visualizers.backend.influxdb.InfluxDBRawBackendListenerClient"
    INFLUXDB = "org.apache.jmeter.visualizers.backend.influxdb.InfluxdbBackendListenerClient"


class BackendListener(TreeElement):
    category: CategoryElement = CategoryElement.LISTENER
    
    def __init__(
        self,
        testname: str = "Backend Listener",
        enabled: bool = True
    ):
        self._arguments_collection: ArgumentsProp = ArgumentsProp()
        self._arguments: ElementProp = ElementProp(
            name=BACKENDLISTENER_ARGUMENTS,
            element_type="Arguments",
            guiclass="ArgumentsPanel",
            testclass="Arguments",
            properties=[self._arguments_collection]
        )
        self.classname: StringProp = StringProp(BACKENDLISTENER_CLASSNAME, BackendListenerClient.GRAPHITE.value)
        self.queue_size: StringProp = StringProp(BACKENDLISTENER_QUEUE_SIZE, "5000")
        
        super().__init__(
            testname=testname,
            enabled=enabled,
            properties=[
                self._arguments,
                self.classname,
                self.queue_size
            ]
        )
        
        self._init_default_graphite_arguments()
    
    @property
    def tag_name(self) -> str:
        return "BackendListener"
    
    @property
    def guiclass(self) -> str:
        return "BackendListenerGui"
    
    @property
    def testclass(self) -> str:
        return "BackendListener"
    
    @staticmethod
    def create_default(testname: str = "Backend Listener") -> "BackendListener":
        return BackendListener(testname=testname)
    
    def _init_default_graphite_arguments(self) -> None:
        self._arguments_collection.add_argument("graphiteMetricsSender", "org.apache.jmeter.visualizers.backend.graphite.TextGraphiteMetricsSender")
        self._arguments_collection.add_argument("graphiteHost", "")
        self._arguments_collection.add_argument("graphitePort", "2003")
        self._arguments_collection.add_argument("rootMetricsPrefix", "jmeter.")
        self._arguments_collection.add_argument("summaryOnly", "false")
        self._arguments_collection.add_argument("samplersList", "")
        self._arguments_collection.add_argument("percentiles", "99;95;90")
    
    def set_classname(self, client: BackendListenerClient) -> None:
        self.classname.value = client.value
    
    def set_classname_raw(self, classname: str) -> None:
        self.classname.value = classname
    
    def set_queue_size(self, size: int) -> None:
        self.queue_size.value = str(size)
    
    def set_queue_size_raw(self, size: str) -> None:
        self.queue_size.value = size
    
    def get_argument_value(self, name: str) -> str | None:
        return self._arguments_collection.get_argument_value(name)

    def has_argument(self, name: str, value: str | None = None) -> bool:
        return self._arguments_collection.has_argument(name, value)

    def get_arguments_data(self) -> list[ArgumentData]:
        return self._arguments_collection.to_data()

    def set_arguments_data(self, data: list[ArgumentData]) -> None:
        self._arguments_collection.from_data(data)
    
    def add_argument(self, name: str, value: str) -> None:
        self._arguments_collection.add_argument(name, value)
    
    def set_argument(self, name: str, value: str) -> bool:
        return self._arguments_collection.set_argument(name, value)
    
    def remove_argument(self, name: str) -> None:
        self._arguments_collection.remove_argument(name)
    
    def clear_arguments(self) -> None:
        self._arguments_collection.clear()
    
    def print_info(self) -> None:
        SLog.log(f"=== BackendListener: {self.testname} ===")
        SLog.log(f"  enabled: {self.enabled}")
        SLog.log(f"  comment: {self.comment.value}")
        
        client_name = "unknown"
        for c in BackendListenerClient:
            if c.value == self.classname.value:
                client_name = c.name
                break
        SLog.log(f"  classname: {client_name}")
        SLog.log(f"  queue_size: {self.queue_size.value}")
        SLog.log(f"  arguments: {len(self._arguments_collection.items)}")
        for arg in self._arguments_collection.items:
            name_prop = next((p for p in arg.properties if p.name == "Argument.name"), None)
            value_prop = next((p for p in arg.properties if p.name == "Argument.value"), None)
            if name_prop and value_prop:
                SLog.log(f"    {name_prop.value} = {value_prop.value}")
        SLog.log(f"  children: {len(self.children)}")



