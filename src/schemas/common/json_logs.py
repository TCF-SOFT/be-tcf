from typing import List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator


class BaseJsonLogSchema(BaseModel):
    """
    Main log in JSON format
    """

    timestamp: str = Field(..., description="ISO 8601 timestamp")
    level: str
    msg: str
    func: str
    source_log: str
    duration: int
    exceptions: Union[List[str], str] = None
    trace_id: str = None
    span_id: str = None
    parent_id: str = None
    # thread: Union[int, str]
    # app_name: str
    # app_version: str
    # app_env: str

    model_config = ConfigDict(extra="ignore")


class RequestJsonLogSchema(BaseModel):
    """
    Schema for request/response answer
    """

    # request_uri: str
    # request_referer: str
    request_method: str
    request_path: str
    request_host: str
    request_size: int
    # request_content_type: str
    # request_headers: dict
    # request_direction: str
    request_body: Optional[str]
    response_status_code: int
    response_size: int
    duration: int
    response_headers: dict
    response_body: Optional[str]

    @field_validator(
        "request_body",
        "response_body",
        mode="before",
    )
    def valid_body(cls, field):
        if isinstance(field, bytes):
            try:
                field = field.decode("utf-8")
            except UnicodeDecodeError:
                field = b"file_bytes"
            return field

        if isinstance(field, str):
            return field
