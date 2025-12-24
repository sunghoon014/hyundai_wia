from enum import Enum


class Role(str, Enum):
    """채팅 도메인에서 사용하는 메시지 역할 옵션."""

    USER = "user"
    ASSISTANT_RUNNING = "assistant_running"
    ASSISTANT_STREAMING = "assistant_streaming"
    ASSISTANT_FINISHED = "assistant_finished"
    SYSTEM = "system"
    DEBUG = "debug"
    INFO = "info"
    STOP = "stop"
    ERROR = "error"
    SSE = "sse"
    TOOL = "tool"
    DOC_LINK = "doc_link"
    WEB_LINK = "web_link"
