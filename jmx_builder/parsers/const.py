# Attributes
ATTR_TESTNAME = "testname"
ATTR_ENABLED = "enabled"
ATTR_GUICLASS = "guiclass"
ATTR_TESTCLASS = "testclass"
ATTR_ELEMENT_TYPE = "elementType"


# TestPlan
# UI: Comments
TESTPLAN_COMMENTS = "TestPlan.comments"
# UI: Functional Test Mode
TESTPLAN_FUNCTIONAL_MODE = "TestPlan.functional_mode"
# UI: Run Thread Groups consecutively
TESTPLAN_SERIALIZE_THREADGROUPS = "TestPlan.serialize_threadgroups"
# UI: Run tearDown Thread Groups after shutdown
TESTPLAN_TEARDOWN_ON_SHUTDOWN = "TestPlan.tearDown_on_shutdown"
# UI: User Defined Variables
TESTPLAN_USER_DEFINED_VARIABLES = "TestPlan.user_defined_variables"
# UI: Add directory or jar to classpath
TESTPLAN_USER_DEFINE_CLASSPATH = "TestPlan.user_define_classpath"

# ThreadGroup
# UI: Delay Thread creation until needed
THREADGROUP_DELAYED_START = "ThreadGroup.delayedStart"
# UI: Number of Threads (users)
THREADGROUP_NUM_THREADS = "ThreadGroup.num_threads"
# UI: Ramp-up period (seconds)
THREADGROUP_RAMP_TIME = "ThreadGroup.ramp_time"
# UI: Duration (seconds)
THREADGROUP_DURATION = "ThreadGroup.duration"
# UI: Startup delay (seconds)
THREADGROUP_DELAY = "ThreadGroup.delay"
# UI: Same user on each iteration
THREADGROUP_SAME_USER_ON_NEXT_ITERATION = "ThreadGroup.same_user_on_next_iteration"
# UI: Specify Thread lifetime
THREADGROUP_SCHEDULER = "ThreadGroup.scheduler"
# UI: Action to be taken after a Sampler error
THREADGROUP_ON_SAMPLE_ERROR = "ThreadGroup.on_sample_error"
# UI: Loop Controller (embedded element)
THREADGROUP_MAIN_CONTROLLER = "ThreadGroup.main_controller"

# LoopController (внутри ThreadGroup)
# UI: Loop Count
LOOPCONTROLLER_LOOPS = "LoopController.loops"
# UI: Continue Forever
LOOPCONTROLLER_CONTINUE_FOREVER = "LoopController.continue_forever"

# TransactionController
# UI: Generate parent sample
TRANSACTIONCONTROLLER_PARENT = "TransactionController.parent"
# UI: Include duration of timer and pre-post processors
TRANSACTIONCONTROLLER_INCLUDE_TIMERS = "TransactionController.includeTimers"

# Arguments (User Defined Variables)
# UI: Variable name
ARGUMENT_NAME = "Argument.name"
# UI: Variable value
ARGUMENT_VALUE = "Argument.value"
# UI: Description
ARGUMENT_DESC = "Argument.desc"
# UI: Metadata (equals sign)
ARGUMENT_METADATA = "Argument.metadata"
# UI: Arguments collection
ARGUMENTS_ARGUMENTS = "Arguments.arguments"

