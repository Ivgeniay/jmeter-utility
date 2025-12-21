from abc import abstractmethod
from console import SLog
from jmx_builder.parsers.const import *
from jmx_builder.models.base import IHierarchable, JMXElement
from jmx_builder.models.props import *
from enum import Enum


################## GENERAL ######################

class TreeElement(JMXElement, IHierarchable):
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
    def create_default(testname: str = "Think Time") -> "TestAction":
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
        self.scope: StringProp = StringProp(SAMPLE_SCOPE, "")
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
                self.scope,
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
        self.scope.value = scope.value
    
    def set_scope_raw(self, scope: str) -> None:
        self.scope.value = scope
    
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




################## TIMERS ######################

class UniformRandomTimer(TreeElement):
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












