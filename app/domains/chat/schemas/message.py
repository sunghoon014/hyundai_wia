import uuid
from datetime import datetime
from typing import Any

import pytz
from pydantic import BaseModel, Field

from app.agents.context.schema import Function as AgentFunction
from app.agents.context.schema import Message as AgentMessage
from app.agents.context.schema import ToolCall as AgentToolCall
from app.domains.chat.schemas.enums import Role


class Message(AgentMessage):
    """채팅 도메인에서 사용하는 기본 메시지 모델입니다.

    에이전트의 Message를 상속받아 DB 저장 및 이벤트 처리에 필요한 필드를 확장합니다.
    """

    id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(pytz.UTC), description="메시지 생성 시간"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Reference 등 추가 정보"
    )

    # AgentMessage의 role 타입을 chat 도메인의 Role Enum으로 오버라이드합니다.
    role: Role

    class Config:
        arbitrary_types_allowed = True


class UserMessage(Message):
    """사용자가 보낸 메시지를 나타내는 모델입니다."""

    role: Role = Role.USER
    content: str  # 사용자의 메시지는 항상 content가 있어야 합니다.


class FunctionCall(AgentFunction):
    """도구 호출 정보를 나타내는 모델입니다."""

    pass


class ToolCall(AgentToolCall):
    """채팅 도메인에서 사용하는 도구 호출 모델입니다.

    FunctionCall 타입을 chat 도메인의 것으로 사용합니다.
    """

    function: FunctionCall


class AssistantMessage(Message):
    """AI 어시스턴트가 보낸 메시지를 나타내는 모델입니다."""

    role: Role
    content: str | None = None
    tool_calls: list[ToolCall] | None = None


class ToolCallsEvent(BaseModel):
    """Tool-call 정보를 담기 위한 이벤트 모델입니다."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(pytz.UTC))
    tool_calls: list[FunctionCall]


class ErrorEvent(Message):
    """오류 발생을 알리는 메시지를 나타내는 모델입니다."""

    role: Role = Role.ERROR
    metadata: dict[str, Any]


class SSEMessage(Message):
    """서버-전송 이벤트(SSE) 메시지를 나타내는 모델입니다."""

    role: Role = Role.SSE


class InfoMessage(Message):
    """정보성 메시지를 나타내는 모델입니다."""

    role: Role = Role.INFO


class DebugMessage(Message):
    """디버깅 목적의 메시지를 나타내는 모델입니다."""

    role: Role = Role.DEBUG


class StopMessage(Message):
    """대화 종료를 알리는 메시지를 나타내는 모델입니다."""

    role: Role = Role.STOP
    content: str = ""
