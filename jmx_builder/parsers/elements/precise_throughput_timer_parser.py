from jmx_builder.parsers.elements.base import TreeElementParser
from jmx_builder.models.tree import PreciseThroughputTimer
from jmx_builder.parsers.const import (
    ATTR_TESTNAME,
    ATTR_ENABLED,
    TESTPLAN_COMMENTS,
    PRECISETHROUGHPUTTIMER_THROUGHPUT,
    PRECISETHROUGHPUTTIMER_THROUGHPUT_PERIOD,
    PRECISETHROUGHPUTTIMER_DURATION,
    PRECISETHROUGHPUTTIMER_BATCH_SIZE,
    PRECISETHROUGHPUTTIMER_BATCH_THREAD_DELAY,
    PRECISETHROUGHPUTTIMER_ALLOWED_THROUGHPUT_SURPLUS,
    PRECISETHROUGHPUTTIMER_EXACT_LIMIT,
    PRECISETHROUGHPUTTIMER_RANDOM_SEED,
)
import re


class PreciseThroughputTimerParser(TreeElementParser):
    @staticmethod
    def parse(xml_content: str) -> PreciseThroughputTimer:
        testname = TreeElementParser.extract_attribute(xml_content, ATTR_TESTNAME) or "Precise Throughput Timer"
        enabled_attr = TreeElementParser.extract_attribute(xml_content, ATTR_ENABLED)
        enabled = enabled_attr != "false"
        
        timer = PreciseThroughputTimer(testname=testname, enabled=enabled)
        
        comment = TreeElementParser.extract_simple_prop_value(xml_content, TESTPLAN_COMMENTS)
        if comment:
            timer.change_comment(comment)
        
        throughput = PreciseThroughputTimerParser._extract_double_prop(xml_content, PRECISETHROUGHPUTTIMER_THROUGHPUT)
        if throughput is not None:
            timer.set_throughput(throughput)
        
        throughput_period = TreeElementParser.extract_simple_prop_value(xml_content, PRECISETHROUGHPUTTIMER_THROUGHPUT_PERIOD)
        if throughput_period:
            timer.set_throughput_period(int(throughput_period))
        
        duration = TreeElementParser.extract_simple_prop_value(xml_content, PRECISETHROUGHPUTTIMER_DURATION)
        if duration:
            timer.set_duration(int(duration))
        
        batch_size = TreeElementParser.extract_simple_prop_value(xml_content, PRECISETHROUGHPUTTIMER_BATCH_SIZE)
        if batch_size:
            timer.set_batch_size(int(batch_size))
        
        batch_thread_delay = TreeElementParser.extract_simple_prop_value(xml_content, PRECISETHROUGHPUTTIMER_BATCH_THREAD_DELAY)
        if batch_thread_delay:
            timer.set_batch_thread_delay(int(batch_thread_delay))
        
        allowed_surplus = PreciseThroughputTimerParser._extract_double_prop(xml_content, PRECISETHROUGHPUTTIMER_ALLOWED_THROUGHPUT_SURPLUS)
        if allowed_surplus is not None:
            timer.set_allowed_throughput_surplus(allowed_surplus)
        
        exact_limit = TreeElementParser.extract_simple_prop_value(xml_content, PRECISETHROUGHPUTTIMER_EXACT_LIMIT)
        if exact_limit:
            timer.set_exact_limit(int(exact_limit))
        
        random_seed = TreeElementParser.extract_simple_prop_value(xml_content, PRECISETHROUGHPUTTIMER_RANDOM_SEED)
        if random_seed:
            timer.set_random_seed(int(random_seed))
        
        return timer
    
    @staticmethod
    def _extract_double_prop(xml_content: str, prop_name: str) -> float | None:
        pattern = rf'<doubleProp>\s*<name>{prop_name}</name>\s*<value>([^<]*)</value>'
        match = re.search(pattern, xml_content)
        if match:
            return float(match.group(1))
        return None