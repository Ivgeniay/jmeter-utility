from pydantic import BaseModel, Field
from typing import Optional


class AssertionResult(BaseModel):
    name: str = ""
    failure: bool = False
    error: bool = False
    failure_message: str = Field(default="", alias="failureMessage")

    model_config = {"populate_by_name": True}


class HttpSample(BaseModel):
    """
    Represents a single HTTP sample (request/response) from JMeter JTL output.
    Can contain nested sub-samples (e.g., for redirects).
    """
    # Timing attributes
    timestamp: int = Field(alias="ts")
    elapsed: int = Field(alias="t")
    latency: int = Field(default=0, alias="lt")
    connect_time: int = Field(default=0, alias="ct")
    idle_time: int = Field(default=0, alias="it")
    
    # Sample identification
    label: str = Field(alias="lb")
    thread_name: str = Field(default="", alias="tn")
    
    # Response attributes
    response_code: str = Field(default="", alias="rc")
    response_message: str = Field(default="", alias="rm")
    success: bool = Field(alias="s")
    
    # Data attributes
    data_type: str = Field(default="", alias="dt")
    data_encoding: str = Field(default="", alias="de")
    bytes_received: int = Field(default=0, alias="by")
    sent_bytes: int = Field(default=0, alias="sby")
    
    # Thread info
    group_threads: int = Field(default=0, alias="ng")
    all_threads: int = Field(default=0, alias="na")
    
    # System info
    hostname: str = Field(default="", alias="hn")
    
    # Counters
    error_count: int = Field(default=0, alias="ec")
    sample_count: int = Field(default=1, alias="sc")
    
    # Request details (nested elements in XML)
    url: Optional[str] = Field(default=None, alias="java.net.URL")
    method: str = ""
    query_string: str = Field(default="", alias="queryString")
    cookies: str = ""
    
    # Headers and data
    request_header: str = Field(default="", alias="requestHeader")
    response_header: str = Field(default="", alias="responseHeader")
    response_data: str = Field(default="", alias="responseData")
    sampler_data: str = Field(default="", alias="samplerData")
    response_file: str = Field(default="", alias="responseFile")
    
    # Redirect
    redirect_location: str = Field(default="", alias="redirectLocation")
    
    # Assertions
    assertion_results: list[AssertionResult] = Field(default_factory=list, alias="assertionResult")
    
    # Sub-samples (e.g., redirects)
    http_sample: list["HttpSample"] = Field(default_factory=list, alias="httpSample")

    model_config = {"populate_by_name": True}


class TestResults(BaseModel):
    """
    Root element of JTL XML file.
    Contains all HTTP samples from test execution.
    """
    version: str = Field(default="1.2")
    http_sample: list[HttpSample] = Field(default_factory=list, alias="httpSample")

    model_config = {"populate_by_name": True}