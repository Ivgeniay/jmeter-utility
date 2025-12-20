# Attributes
ATTR_TESTNAME = "testname"
ATTR_ENABLED = "enabled"
ATTR_GUICLASS = "guiclass"
ATTR_TESTCLASS = "testclass"
ATTR_ELEMENT_TYPE = "elementType"
ARGUMENT = "Argument"
ARGUMENT_NAME = "Argument.name"
ARGUMENT_VALUE = "Argument.value"
ARGUMENT_DESC = "Argument.desc"
ARGUMENT_METADATA = "Argument.metadata"
ARGUMENTS_ARGUMENTS = "Arguments.arguments"

# PROPS
STRING_PROP = "stringProp"
BOOL_PROP = "boolProp"
INT_PROP = "intProp"
LONG_PROP = "longProp"
COLLECTION_PROP ="collectionProp"
ELEMENT_PROP = "elementProp"

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


# HTTPSamplerProxy
# UI: Server Name or IP
HTTPSAMPLER_DOMAIN = "HTTPSampler.domain"
# UI: Port Number
HTTPSAMPLER_PORT = "HTTPSampler.port"
# UI: Protocol [http/https]
HTTPSAMPLER_PROTOCOL = "HTTPSampler.protocol"
# UI: Path
HTTPSAMPLER_PATH = "HTTPSampler.path"
# UI: Method
HTTPSAMPLER_METHOD = "HTTPSampler.method"
# UI: Content encoding
HTTPSAMPLER_CONTENT_ENCODING = "HTTPSampler.contentEncoding"
# UI: Follow Redirects
HTTPSAMPLER_FOLLOW_REDIRECTS = "HTTPSampler.follow_redirects"
# UI: Redirect Automatically
HTTPSAMPLER_AUTO_REDIRECTS = "HTTPSampler.auto_redirects"
# UI: Use KeepAlive
HTTPSAMPLER_USE_KEEPALIVE = "HTTPSampler.use_keepalive"
# UI: Use multipart/form-data
HTTPSAMPLER_DO_MULTIPART_POST = "HTTPSampler.DO_MULTIPART_POST"
# UI: Browser-compatible headers
HTTPSAMPLER_BROWSER_COMPATIBLE_MULTIPART = "HTTPSampler.BROWSER_COMPATIBLE_MULTIPART"
# UI: Body Data mode switch
HTTPSAMPLER_POST_BODY_RAW = "HTTPSampler.postBodyRaw"
# UI: Parameters / Body Data
HTTPSAMPLER_ARGUMENTS = "HTTPsampler.Arguments"
# UI: Files Upload
HTTPSAMPLER_FILES = "HTTPsampler.Files"
# UI: Connect Timeout (ms)
HTTPSAMPLER_CONNECT_TIMEOUT = "HTTPSampler.connect_timeout"
# UI: Response Timeout (ms)
HTTPSAMPLER_RESPONSE_TIMEOUT = "HTTPSampler.response_timeout"
# UI: Retrieve All Embedded Resources
HTTPSAMPLER_IMAGE_PARSER = "HTTPSampler.image_parser"
# UI: Parallel downloads
HTTPSAMPLER_CONCURRENT_DWN = "HTTPSampler.concurrentDwn"
# UI: Parallel downloads pool size
HTTPSAMPLER_CONCURRENT_POOL = "HTTPSampler.concurrentPool"
# UI: URLs must match
HTTPSAMPLER_EMBEDDED_URL_RE = "HTTPSampler.embedded_url_re"
# UI: URLs must not match
HTTPSAMPLER_EMBEDDED_URL_EXCLUDE_RE = "HTTPSampler.embedded_url_exclude_re"
# UI: Source Address
HTTPSAMPLER_IP_SOURCE = "HTTPSampler.ipSource"
# UI: Source Address Type
HTTPSAMPLER_IP_SOURCE_TYPE = "HTTPSampler.ipSourceType"
# UI: Proxy Scheme
HTTPSAMPLER_PROXY_SCHEME = "HTTPSampler.proxyScheme"
# UI: Proxy Host
HTTPSAMPLER_PROXY_HOST = "HTTPSampler.proxyHost"
# UI: Proxy Port
HTTPSAMPLER_PROXY_PORT = "HTTPSampler.proxyPort"
# UI: Proxy Username
HTTPSAMPLER_PROXY_USER = "HTTPSampler.proxyUser"
# UI: Proxy Password
HTTPSAMPLER_PROXY_PASS = "HTTPSampler.proxyPass"
# UI: Implementation
HTTPSAMPLER_IMPLEMENTATION = "HTTPSampler.implementation"
# UI: Save response as MD5 hash
HTTPSAMPLER_MD5 = "HTTPSampler.md5"
HTTP_ARGUMENT = "HTTPArgument"

# HTTPArgument (внутри HTTPSampler.Arguments)
# UI: Include Equals
HTTPARGUMENT_USE_EQUALS = "HTTPArgument.use_equals"
# UI: Encode?
HTTPARGUMENT_ALWAYS_ENCODE = "HTTPArgument.always_encode"

# HTTPFileArg (внутри HTTPsampler.Files)
# UI: File Path
HTTPFILEARG_PATH = "File.path"
# UI: Parameter Name
HTTPFILEARG_PARAMNAME = "File.paramname"
# UI: MIME Type
HTTPFILEARG_MIMETYPE = "File.mimetype"
# HTTPFileArgs
HTTPFILEARGS_FILES = "HTTPFileArgs.files"
