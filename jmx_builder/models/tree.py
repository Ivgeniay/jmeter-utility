from abc import abstractmethod
from console import SLog
from jmx_builder.parsers.const import *
from jmx_builder.models.base import IHierarchable, JMXElement
from jmx_builder.models.props import BoolProp, ElementProp, IntProp, LongProp, PropElement, StringProp, UserDefinedVariablesProp
from enum import Enum



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
