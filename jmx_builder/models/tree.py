from abc import abstractmethod
from jmx_builder.models.base import JMXElement
from jmx_builder.models.props import BoolProp, ElementProp, IntProp, LongProp, PropElement, StringProp, UserDefinedVariablesProp
from enum import Enum

class TreeElement(JMXElement):
    def __init__(
        self,
        testname: str,
        enabled: bool = True,
        properties: list[PropElement] | None = None
    ):
        self.testname = testname
        self.enabled = enabled
        self.children: list[TreeElement] = []
        self.comment: StringProp = StringProp("TestPlan.comments", "")
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


class TestPlan(TreeElement):
    def __init__(
        self,
        testname: str = "Test Plan",
        enabled: bool = True
    ):
        self.functional_mode: BoolProp = BoolProp("TestPlan.functional_mode", False)
        self.serialize_threadgroups: BoolProp = BoolProp("TestPlan.serialize_threadgroups", False)
        self.teardown_on_shutdown: BoolProp = BoolProp("TestPlan.tearDown_on_shutdown", True)
        self.user_define_classpath: StringProp = StringProp("TestPlan.user_define_classpath", "")
        
        self._variables: UserDefinedVariablesProp = UserDefinedVariablesProp()
        self._user_defined_variables: ElementProp = ElementProp(
            name="TestPlan.user_defined_variables",
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
    
    def add_variable(self, name: str, value: str) -> None:
        self._variables.add_variable(name, value)
    
    def remove_variable(self, name: str) -> None:
        self._variables.remove_variable(name)
    
    def get_variable(self, name: str) -> ElementProp | None:
        return self._variables.get_variable(name)
    
    def change_variable(self, name: str, new_name: str | None = None, new_value: str | None = None) -> bool:
        return self._variables.change_variable(name, new_name, new_value)


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
        self.delayed_start: BoolProp = BoolProp("ThreadGroup.delayedStart", False)
        self.num_threads: IntProp = IntProp("ThreadGroup.num_threads", 1)
        self.ramp_time: IntProp = IntProp("ThreadGroup.ramp_time", 1)
        self.duration: LongProp = LongProp("ThreadGroup.duration", 0)
        self.delay: LongProp = LongProp("ThreadGroup.delay", 0)
        self.same_user_on_next_iteration: BoolProp = BoolProp("ThreadGroup.same_user_on_next_iteration", True)
        self.scheduler: BoolProp = BoolProp("ThreadGroup.scheduler", False)
        self._on_sample_error: StringProp = StringProp("ThreadGroup.on_sample_error", OnSampleError.CONTINUE.value)
        
        self._loop_count_infinite: bool = False
        self._loop_count_prop: IntProp | StringProp = StringProp("LoopController.loops", "1")
        self._continue_forever: BoolProp = BoolProp("LoopController.continue_forever", False)
        
        self._loop_controller: ElementProp = ElementProp(
            name="ThreadGroup.main_controller",
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


class TransactionController(TreeElement):
    def __init__(
        self,
        testname: str = "Transaction Controller",
        enabled: bool = True
    ):
        self.generate_parent_sample: BoolProp = BoolProp("TransactionController.parent", False)
        self.include_timers: BoolProp = BoolProp("TransactionController.includeTimers", False)
        
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
    
    def set_generate_parent_sample(self, enable: bool) -> None:
        self.generate_parent_sample.value = enable
    
    def set_include_timers(self, enable: bool) -> None:
        self.include_timers.value = enable