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


# CookieManager
# UI: Clear cookies each iteration
COOKIEMANAGER_CLEAR_EACH_ITERATION = "CookieManager.clearEachIteration"
# UI: Use Thread Group configuration
COOKIEMANAGER_CONTROLLED_BY_THREADGROUP = "CookieManager.controlledByThreadGroup"
# UI: Cookies collection
COOKIEMANAGER_COOKIES = "CookieManager.cookies"
# UI: Cookie Policy (не в твоём примере, но бывает)
COOKIEMANAGER_POLICY = "CookieManager.policy"

# Cookie (внутри CookieManager.cookies)
# UI: Cookie Name (в атрибуте name и testname элемента)
COOKIE_VALUE = "Cookie.value"
# UI: Cookie Domain
COOKIE_DOMAIN = "Cookie.domain"
# UI: Cookie Path
COOKIE_PATH = "Cookie.path"
# UI: Secure
COOKIE_SECURE = "Cookie.secure"
# UI: Expires
COOKIE_EXPIRES = "Cookie.expires"
# UI: Path Specified
COOKIE_PATH_SPECIFIED = "Cookie.path_specified"
# UI: Domain Specified
COOKIE_DOMAIN_SPECIFIED = "Cookie.domain_specified"



# CacheManager
# UI: Clear cache each iteration
CACHEMANAGER_CLEAR_EACH_ITERATION = "clearEachIteration"
# UI: Use Cache-Control/Expires header when processing GET requests
CACHEMANAGER_USE_EXPIRES = "useExpires"
# UI: Use Thread Group configuration
CACHEMANAGER_CONTROLLED_BY_THREAD = "CacheManager.controlledByThread"
# UI: Max Number of elements in cache
CACHEMANAGER_MAX_SIZE = "maxSize"


# HeaderManager
# UI: Headers collection
HEADERMANAGER_HEADERS = "HeaderManager.headers"

# Header (внутри HeaderManager.headers)
# UI: Header Name
HEADER_NAME = "Header.name"
# UI: Header Value
HEADER_VALUE = "Header.value"


# TestAction
# UI: Action to take
TESTACTION_ACTION = "ActionProcessor.action"
# UI: Target
TESTACTION_TARGET = "ActionProcessor.target"
# UI: Duration (ms)
TESTACTION_DURATION = "ActionProcessor.duration"

# UniformRandomTimer
# UI: Constant Delay Offset (ms)
UNIFORMRANDOMTIMER_DELAY = "ConstantTimer.delay"
# UI: Random Delay Maximum (ms)
UNIFORMRANDOMTIMER_RANGE = "RandomTimer.range"

# ConstantTimer
# UI: Thread Delay (ms)
CONSTANTTIMER_DELAY = "ConstantTimer.delay"

# PreciseThroughputTimer
# UI: Target throughput (samples per time period)
PRECISETHROUGHPUTTIMER_THROUGHPUT = "throughput"
# UI: Throughput period (seconds)
PRECISETHROUGHPUTTIMER_THROUGHPUT_PERIOD = "throughputPeriod"
# UI: Test duration (seconds)
PRECISETHROUGHPUTTIMER_DURATION = "duration"
# UI: Number of threads in the batch
PRECISETHROUGHPUTTIMER_BATCH_SIZE = "batchSize"
# UI: Delay between threads in the batch (ms)
PRECISETHROUGHPUTTIMER_BATCH_THREAD_DELAY = "batchThreadDelay"
# UI: Allowed throughput surplus
PRECISETHROUGHPUTTIMER_ALLOWED_THROUGHPUT_SURPLUS = "allowedThroughputSurplus"
# UI: Exact limit for iterations
PRECISETHROUGHPUTTIMER_EXACT_LIMIT = "exactLimit"
# UI: Random seed
PRECISETHROUGHPUTTIMER_RANDOM_SEED = "randomSeed"


# ConstantThroughputTimer
# UI: Target throughput (samples per minute)
CONSTANTTHROUGHPUTTIMER_THROUGHPUT = "throughput"
# UI: Calculate Throughput based on
CONSTANTTHROUGHPUTTIMER_CALC_MODE = "calcMode"


# JSR223 (общие для Sampler, PreProcessor, PostProcessor)
# UI: Script language
JSR223_SCRIPT_LANGUAGE = "scriptLanguage"
# UI: Script file path
JSR223_FILENAME = "filename"
# UI: Parameters
JSR223_PARAMETERS = "parameters"
# UI: Script text
JSR223_SCRIPT = "script"
# UI: Cache compiled script
JSR223_CACHE_KEY = "cacheKey"