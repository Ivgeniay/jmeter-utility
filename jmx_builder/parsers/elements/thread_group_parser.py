from jmx_builder.parsers.elements.base import TreeElementParser
from jmx_builder.models.tree import ThreadGroup
from jmx_builder.parsers.const import *


class ThreadGroupParser(TreeElementParser):
    @staticmethod
    def parse(xml_content: str) -> ThreadGroup:
        testname = TreeElementParser.extract_attribute(xml_content, ATTR_TESTNAME) or ""
        enabled_attr = TreeElementParser.extract_attribute(xml_content, ATTR_ENABLED)
        enabled = enabled_attr != "false"
        
        thread_group = ThreadGroup(testname=testname, enabled=enabled)
        
        comment = TreeElementParser.extract_simple_prop_value(xml_content, TESTPLAN_COMMENTS)
        if comment:
            thread_group.change_comment(comment)
        
        num_threads = TreeElementParser.extract_simple_prop_value(xml_content, THREADGROUP_NUM_THREADS)
        if num_threads:
            thread_group.num_threads.value = int(num_threads)
        
        ramp_time = TreeElementParser.extract_simple_prop_value(xml_content, THREADGROUP_RAMP_TIME)
        if ramp_time:
            thread_group.ramp_time.value = int(ramp_time)
        
        duration = TreeElementParser.extract_simple_prop_value(xml_content, THREADGROUP_DURATION)
        if duration:
            thread_group.duration.value = int(duration)
        
        delay = TreeElementParser.extract_simple_prop_value(xml_content, THREADGROUP_DELAY)
        if delay:
            thread_group.delay.value = int(delay)
        
        delayed_start = TreeElementParser.extract_simple_prop_value(xml_content, THREADGROUP_DELAYED_START)
        if delayed_start:
            thread_group.delayed_start.value = delayed_start.lower() == "true"
        
        scheduler = TreeElementParser.extract_simple_prop_value(xml_content, THREADGROUP_SCHEDULER)
        if scheduler:
            thread_group.scheduler.value = scheduler.lower() == "true"
        
        same_user = TreeElementParser.extract_simple_prop_value(xml_content, THREADGROUP_SAME_USER_ON_NEXT_ITERATION)
        if same_user:
            thread_group.same_user_on_next_iteration.value = same_user.lower() == "true"
        
        on_sample_error = TreeElementParser.extract_simple_prop_value(xml_content, THREADGROUP_ON_SAMPLE_ERROR)
        if on_sample_error:
            thread_group.set_on_sample_error_raw(on_sample_error)
        
        loop_controller_content = TreeElementParser.extract_element_prop_content(xml_content, THREADGROUP_MAIN_CONTROLLER)
        if loop_controller_content:
            ThreadGroupParser._parse_loop_controller(thread_group, loop_controller_content)
        
        return thread_group
    
    @staticmethod
    def _parse_loop_controller(thread_group: ThreadGroup, content: str) -> None:
        loops = TreeElementParser.extract_simple_prop_value(content, LOOPCONTROLLER_LOOPS)
        if loops:
            if loops == "-1":
                thread_group.set_loop_count_infinite(True)
            elif loops.lstrip("-").isdigit():
                thread_group.set_loop_count(int(loops))
            else:
                thread_group.set_loop_count_raw(loops)
        
        continue_forever = TreeElementParser.extract_simple_prop_value(content, LOOPCONTROLLER_CONTINUE_FOREVER)
        if continue_forever:
            thread_group.set_continue_forever(continue_forever.lower() == "true")