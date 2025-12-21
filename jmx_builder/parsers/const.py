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


# IfController
# UI: Condition (expression)
IFCONTROLLER_CONDITION = "IfController.condition"
# UI: Evaluate for all children
IFCONTROLLER_EVALUATE_ALL = "IfController.evaluateAll"
# UI: Interpret Condition as Variable Expression
IFCONTROLLER_USE_EXPRESSION = "IfController.useExpression"

# WhileController
# UI: Condition (function or variable)
WHILECONTROLLER_CONDITION = "WhileController.condition"

# CriticalSectionController
# UI: Lock name
CRITICALSECTIONCONTROLLER_LOCK_NAME = "CriticalSectionController.lockName"


# ForeachController
# UI: Input variable prefix
FOREACHCONTROLLER_INPUT_VAL = "ForeachController.inputVal"
# UI: Output variable name
FOREACHCONTROLLER_RETURN_VAL = "ForeachController.returnVal"
# UI: Add "_" before number
FOREACHCONTROLLER_USE_SEPARATOR = "ForeachController.useSeparator"
# UI: Start index for loop (exclusive)
FOREACHCONTROLLER_START_INDEX = "ForeachController.startIndex"
# UI: End index for loop (inclusive)
FOREACHCONTROLLER_END_INDEX = "ForeachController.endIndex"


# IncludeController
# UI: Filename
INCLUDECONTROLLER_INCLUDE_PATH = "IncludeController.includepath"

# InterleaveControl
# UI: Interleave style (0 - ignore sub-controllers, 1 - interleave across threads)
INTERLEAVECONTROL_STYLE = "InterleaveControl.style"
# UI: Interleave across threads
INTERLEAVECONTROL_ACCROSS_THREADS = "InterleaveControl.accrossThreads"

# RunTime
# UI: Runtime (seconds)
RUNTIME_SECONDS = "RunTime.seconds"

# ThroughputController
# UI: Based on (0 - Total Executions, 1 - Percent Executions)
THROUGHPUTCONTROLLER_STYLE = "ThroughputController.style"
# UI: Per User
THROUGHPUTCONTROLLER_PER_THREAD = "ThroughputController.perThread"
# UI: Throughput (for Total Executions mode)
THROUGHPUTCONTROLLER_MAX_THROUGHPUT = "ThroughputController.maxThroughput"
# UI: Throughput (for Percent Executions mode)
THROUGHPUTCONTROLLER_PERCENT_THROUGHPUT = "ThroughputController.percentThroughput"


# SwitchController
# UI: Switch Value
SWITCHCONTROLLER_VALUE = "SwitchController.value"

# ModuleController
# UI: Module path
MODULECONTROLLER_NODE_PATH = "ModuleController.node_path"

# DebugSampler
# UI: JMeter properties
DEBUGSAMPLER_DISPLAY_JMETER_PROPERTIES = "displayJMeterProperties"
# UI: JMeter variables
DEBUGSAMPLER_DISPLAY_JMETER_VARIABLES = "displayJMeterVariables"
# UI: System properties
DEBUGSAMPLER_DISPLAY_SYSTEM_PROPERTIES = "displaySystemProperties"


# RegexExtractor
# UI: Field to check
REGEXEXTRACTOR_USE_HEADERS = "RegexExtractor.useHeaders"
# UI: Name of created variable
REGEXEXTRACTOR_REFNAME = "RegexExtractor.refname"
# UI: Regular Expression
REGEXEXTRACTOR_REGEX = "RegexExtractor.regex"
# UI: Template
REGEXEXTRACTOR_TEMPLATE = "RegexExtractor.template"
# UI: Default Value
REGEXEXTRACTOR_DEFAULT = "RegexExtractor.default"
# UI: Use empty default value
REGEXEXTRACTOR_DEFAULT_EMPTY_VALUE = "RegexExtractor.default_empty_value"
# UI: Match No.
REGEXEXTRACTOR_MATCH_NUMBER = "RegexExtractor.match_number"
# UI: Apply to (scope)
SAMPLE_SCOPE = "Sample.scope"
# UI: JMeter Variable Name (when scope=variable)
SCOPE_VARIABLE = "Scope.variable"


# JSONPostProcessor
# UI: Names of created variables
JSONPOSTPROCESSOR_REFERENCE_NAMES = "JSONPostProcessor.referenceNames"
# UI: JSON Path expressions
JSONPOSTPROCESSOR_JSON_PATH_EXPRS = "JSONPostProcessor.jsonPathExprs"
# UI: Match No.
JSONPOSTPROCESSOR_MATCH_NUMBERS = "JSONPostProcessor.match_numbers"
# UI: Default Values
JSONPOSTPROCESSOR_DEFAULT_VALUES = "JSONPostProcessor.defaultValues"
# UI: Compute concatenation var
JSONPOSTPROCESSOR_COMPUTE_CONCAT = "JSONPostProcessor.compute_concat"


# HtmlExtractor
# UI: Name of created variable
HTMLEXTRACTOR_REFNAME = "HtmlExtractor.refname"
# UI: CSS Selector expression
HTMLEXTRACTOR_EXPR = "HtmlExtractor.expr"
# UI: Attribute
HTMLEXTRACTOR_ATTRIBUTE = "HtmlExtractor.attribute"
# UI: Default Value
HTMLEXTRACTOR_DEFAULT = "HtmlExtractor.default"
# UI: Use empty default value
HTMLEXTRACTOR_DEFAULT_EMPTY_VALUE = "HtmlExtractor.default_empty_value"
# UI: Match No.
HTMLEXTRACTOR_MATCH_NUMBER = "HtmlExtractor.match_number"
# UI: CSS Selector implementation
HTMLEXTRACTOR_EXTRACTOR_IMPL = "HtmlExtractor.extractor_impl"



# BoundaryExtractor
# UI: Field to check
BOUNDARYEXTRACTOR_USE_HEADERS = "BoundaryExtractor.useHeaders"
# UI: Name of created variable
BOUNDARYEXTRACTOR_REFNAME = "BoundaryExtractor.refname"
# UI: Left boundary
BOUNDARYEXTRACTOR_LBOUNDARY = "BoundaryExtractor.lboundary"
# UI: Right boundary
BOUNDARYEXTRACTOR_RBOUNDARY = "BoundaryExtractor.rboundary"
# UI: Default Value
BOUNDARYEXTRACTOR_DEFAULT = "BoundaryExtractor.default"
# UI: Use empty default value
BOUNDARYEXTRACTOR_DEFAULT_EMPTY_VALUE = "BoundaryExtractor.default_empty_value"
# UI: Match No.
BOUNDARYEXTRACTOR_MATCH_NUMBER = "BoundaryExtractor.match_number"


# JMESPathExtractor
# UI: Name of created variable
JMESEXTRACTOR_REFERENCE_NAME = "JMESExtractor.referenceName"
# UI: JMESPath expression
JMESEXTRACTOR_JMES_PATH_EXPR = "JMESExtractor.jmesPathExpr"
# UI: Match No.
JMESEXTRACTOR_MATCH_NUMBER = "JMESExtractor.matchNumber"
# UI: Default Value
JMESEXTRACTOR_DEFAULT_VALUE = "JMESExtractor.defaultValue"


# DebugPostProcessor
# UI: JMeter properties
DEBUGPOSTPROCESSOR_DISPLAY_JMETER_PROPERTIES = "displayJMeterProperties"
# UI: JMeter variables
DEBUGPOSTPROCESSOR_DISPLAY_JMETER_VARIABLES = "displayJMeterVariables"
# UI: Sampler properties
DEBUGPOSTPROCESSOR_DISPLAY_SAMPLER_PROPERTIES = "displaySamplerProperties"
# UI: System properties
DEBUGPOSTPROCESSOR_DISPLAY_SYSTEM_PROPERTIES = "displaySystemProperties"

# ResultAction
# UI: Action to be taken after a Sampler error
RESULTACTION_ON_ERROR_ACTION = "OnError.action"


# XPathExtractor
# UI: Default Value
XPATHEXTRACTOR_DEFAULT = "XPathExtractor.default"
# UI: Name of created variable
XPATHEXTRACTOR_REFNAME = "XPathExtractor.refname"
# UI: Match No.
XPATHEXTRACTOR_MATCH_NUMBER = "XPathExtractor.matchNumber"
# UI: XPath query
XPATHEXTRACTOR_XPATH_QUERY = "XPathExtractor.xpathQuery"
# UI: Use Tidy (tolerant parser)
XPATHEXTRACTOR_TOLERANT = "XPathExtractor.tolerant"
# UI: Validate XML
XPATHEXTRACTOR_VALIDATE = "XPathExtractor.validate"
# UI: Use Namespaces
XPATHEXTRACTOR_NAMESPACE = "XPathExtractor.namespace"
# UI: Report errors
XPATHEXTRACTOR_REPORT_ERRORS = "XPathExtractor.report_errors"
# UI: Show warnings
XPATHEXTRACTOR_SHOW_WARNINGS = "XPathExtractor.show_warnings"
# UI: Whitespace
XPATHEXTRACTOR_WHITESPACE = "XPathExtractor.whitespace"
# UI: Download external DTDs
XPATHEXTRACTOR_DOWNLOAD_DTDS = "XPathExtractor.download_dtds"
# UI: Return entire XPath fragment
XPATHEXTRACTOR_FRAGMENT = "XPathExtractor.fragment"



# XPath2Extractor
# UI: Default Value
XPATH2EXTRACTOR_DEFAULT = "XPathExtractor2.default"
# UI: Name of created variable
XPATH2EXTRACTOR_REFNAME = "XPathExtractor2.refname"
# UI: Match No.
XPATH2EXTRACTOR_MATCH_NUMBER = "XPathExtractor2.matchNumber"
# UI: XPath query
XPATH2EXTRACTOR_XPATH_QUERY = "XPathExtractor2.xpathQuery"
# UI: Namespaces aliases list
XPATH2EXTRACTOR_NAMESPACES = "XPathExtractor2.namespaces"
# UI: Return entire XPath fragment
XPATH2EXTRACTOR_FRAGMENT = "XPathExtractor2.fragment"



# ResultCollector
# UI: Log Errors Only
RESULTCOLLECTOR_ERROR_LOGGING = "ResultCollector.error_logging"
# UI: Log Successes Only
RESULTCOLLECTOR_SUCCESS_ONLY_LOGGING = "ResultCollector.success_only_logging"
# UI: Filename
RESULTCOLLECTOR_FILENAME = "filename"
# UI: Include group name in label
RESULTCOLLECTOR_USE_GROUP_NAME = "useGroupName"


# BackendListener
# UI: Backend Listener implementation
BACKENDLISTENER_CLASSNAME = "classname"
# UI: Async Queue size
BACKENDLISTENER_QUEUE_SIZE = "QUEUE_SIZE"
# UI: Arguments
BACKENDLISTENER_ARGUMENTS = "arguments"

# CSVDataSet
CSVDATASET_FILENAME = "filename"
CSVDATASET_FILE_ENCODING = "fileEncoding"
CSVDATASET_VARIABLE_NAMES = "variableNames"
CSVDATASET_IGNORE_FIRST_LINE = "ignoreFirstLine"
CSVDATASET_DELIMITER = "delimiter"
CSVDATASET_QUOTED_DATA = "quotedData"
CSVDATASET_RECYCLE = "recycle"
CSVDATASET_STOP_THREAD = "stopThread"
CSVDATASET_SHARE_MODE = "shareMode"



# BoltConnectionElement
BOLTCONNECTION_URI = "boltUri"
BOLTCONNECTION_MAX_POOL_SIZE = "maxConnectionPoolSize"
BOLTCONNECTION_PASSWORD = "password"
BOLTCONNECTION_USERNAME = "username"


# CounterConfig
COUNTERCONFIG_START = "CounterConfig.start"
COUNTERCONFIG_END = "CounterConfig.end"
COUNTERCONFIG_INCR = "CounterConfig.incr"
COUNTERCONFIG_NAME = "CounterConfig.name"
COUNTERCONFIG_FORMAT = "CounterConfig.format"
COUNTERCONFIG_PER_USER = "CounterConfig.per_user"
COUNTERCONFIG_RESET_ON_TG_ITERATION = "CounterConfig.reset_on_tg_iteration"


# RandomVariableConfig
RANDOMVARIABLE_MAXIMUM_VALUE = "maximumValue"
RANDOMVARIABLE_MINIMUM_VALUE = "minimumValue"
RANDOMVARIABLE_OUTPUT_FORMAT = "outputFormat"
RANDOMVARIABLE_PER_THREAD = "perThread"
RANDOMVARIABLE_RANDOM_SEED = "randomSeed"
RANDOMVARIABLE_VARIABLE_NAME = "variableName"

# LdapExtConfigGui (LDAP Extended Request Defaults)
LDAPEXT_SERVERNAME = "servername"
LDAPEXT_PORT = "port"
LDAPEXT_ROOTDN = "rootdn"
LDAPEXT_SCOPE = "scope"
LDAPEXT_COUNTLIMIT = "countlimit"
LDAPEXT_TIMELIMIT = "timelimit"
LDAPEXT_ATTRIBUTES = "attributes"
LDAPEXT_RETURN_OBJECT = "return_object"
LDAPEXT_DEREF_ALIASES = "deref_aliases"
LDAPEXT_CONNECTION_TIMEOUT = "connection_timeout"
LDAPEXT_PARSEFLAG = "parseflag"
LDAPEXT_SECURE = "secure"
LDAPEXT_TRUSTALL = "trustall"
LDAPEXT_USER_DN = "user_dn"
LDAPEXT_USER_PW = "user_pw"
LDAPEXT_COMPAREDN = "comparedn"
LDAPEXT_COMPAREFILT = "comparefilt"
LDAPEXT_MODDDN = "modddn"
LDAPEXT_NEWDN = "newdn"
LDAPEXT_TEST = "test"


# FtpConfigGui (FTP Request Defaults)
FTPSAMPLER_SERVER = "FTPSampler.server"
FTPSAMPLER_PORT = "FTPSampler.port"
FTPSAMPLER_FILENAME = "FTPSampler.filename"
FTPSAMPLER_LOCALFILENAME = "FTPSampler.localfilename"
FTPSAMPLER_INPUTDATA = "FTPSampler.inputdata"
FTPSAMPLER_BINARYMODE = "FTPSampler.binarymode"
FTPSAMPLER_SAVERESPONSE = "FTPSampler.saveresponse"
FTPSAMPLER_UPLOAD = "FTPSampler.upload"



# LdapConfigGui (LDAP Request Defaults)
LDAP_SERVERNAME = "servername"
LDAP_PORT = "port"
LDAP_ROOTDN = "rootdn"
LDAP_USER_DEFINED = "user_defined"
LDAP_TEST = "test"
LDAP_BASE_ENTRY_DN = "base_entry_dn"
LDAP_ARGUMENTS = "arguments"


# LoginConfigGui (Login Config Element)
LOGINCONFIG_USERNAME = "ConfigTestElement.username"
LOGINCONFIG_PASSWORD = "ConfigTestElement.password"


# TCPConfigGui (TCP Sampler Config)
TCPSAMPLER_SERVER = "TCPSampler.server"
TCPSAMPLER_PORT = "TCPSampler.port"
TCPSAMPLER_REUSE_CONNECTION = "TCPSampler.reUseConnection"
TCPSAMPLER_NODELAY = "TCPSampler.nodelay"
TCPSAMPLER_TIMEOUT = "TCPSampler.timeout"
TCPSAMPLER_REQUEST = "TCPSampler.request"
TCPSAMPLER_CLOSE_CONNECTION = "TCPSampler.closeConnection"
TCPSAMPLER_CLASSNAME = "TCPSampler.classname"
TCPSAMPLER_CTIMEOUT = "TCPSampler.ctimeout"
TCPSAMPLER_SO_LINGER = "TCPSampler.soLinger"
TCPSAMPLER_EOL_BYTE = "TCPSampler.EolByte"


# KeystoreConfig
KEYSTORECONFIG_CLIENT_CERT_ALIAS_VAR_NAME = "clientCertAliasVarName"
KEYSTORECONFIG_END_INDEX = "endIndex"
KEYSTORECONFIG_PRELOAD = "preload"
KEYSTORECONFIG_START_INDEX = "startIndex"


# AuthManager (HTTP Authorization Manager)
AUTHMANAGER_AUTH_LIST = "AuthManager.auth_list"
AUTHMANAGER_CONTROLLED_BY_THREADGROUP = "AuthManager.controlledByThreadGroup"
AUTHMANAGER_CLEAR_EACH_ITERATION = "AuthManager.clearEachIteration"

# Authorization (внутри AuthManager.auth_list)
AUTHORIZATION_URL = "Authorization.url"
AUTHORIZATION_USERNAME = "Authorization.username"
AUTHORIZATION_PASSWORD = "Authorization.password"
AUTHORIZATION_DOMAIN = "Authorization.domain"
AUTHORIZATION_REALM = "Authorization.realm"
AUTHORIZATION_MECHANISM = "Authorization.mechanism"


# JDBCDataSource (JDBC Connection Configuration)
JDBCDATASOURCE_AUTOCOMMIT = "autocommit"
JDBCDATASOURCE_CHECK_QUERY = "checkQuery"
JDBCDATASOURCE_CONNECTION_AGE = "connectionAge"
JDBCDATASOURCE_CONNECTION_PROPERTIES = "connectionProperties"
JDBCDATASOURCE_DATASOURCE = "dataSource"
JDBCDATASOURCE_DB_URL = "dbUrl"
JDBCDATASOURCE_DRIVER = "driver"
JDBCDATASOURCE_INIT_QUERY = "initQuery"
JDBCDATASOURCE_KEEP_ALIVE = "keepAlive"
JDBCDATASOURCE_PASSWORD = "password"
JDBCDATASOURCE_POOL_MAX = "poolMax"
JDBCDATASOURCE_PREINIT = "preinit"
JDBCDATASOURCE_TIMEOUT = "timeout"
JDBCDATASOURCE_TRANSACTION_ISOLATION = "transactionIsolation"
JDBCDATASOURCE_TRIM_INTERVAL = "trimInterval"
JDBCDATASOURCE_USERNAME = "username"
JDBCDATASOURCE_POOL_PREPARED_STATEMENTS = "poolPreparedStatements"

# JavaConfig (Java Request Defaults)
JAVACONFIG_ARGUMENTS = "arguments"
JAVACONFIG_CLASSNAME = "classname"


# DNSCacheManager
DNSCACHEMANAGER_SERVERS = "DNSCacheManager.servers"
DNSCACHEMANAGER_HOSTS = "DNSCacheManager.hosts"
DNSCACHEMANAGER_CLEAR_EACH_ITERATION = "DNSCacheManager.clearEachIteration"
DNSCACHEMANAGER_IS_CUSTOM_RESOLVER = "DNSCacheManager.isCustomResolver"

# StaticHost (внутри DNSCacheManager.hosts)
STATICHOST_NAME = "StaticHost.Name"
STATICHOST_ADDRESS = "StaticHost.Address"