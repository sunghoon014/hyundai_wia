from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


class Role(str, Enum):
    """메시지 역할 옵션."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


ROLE_TYPE = Literal[Role.SYSTEM, Role.USER, Role.ASSISTANT, Role.TOOL]
ROLE_VALUES = tuple(role.value for role in Role)


class ToolChoice(str, Enum):
    """도구 선택 옵션(OpenAI API 문서 참고)."""

    NONE = "none"
    AUTO = "auto"
    REQUIRED = "required"


TOOL_CHOICE_TYPE = Literal[ToolChoice.NONE, ToolChoice.AUTO, ToolChoice.REQUIRED]
TOOL_CHOICE_VALUES = tuple(choice.value for choice in ToolChoice)


class AgentState(str, Enum):
    """에이전트 실행 상태."""

    IDLE = "idle"  # 대기
    RUNNING = "assistant_running"  # 에이전트 실행 중
    FINISHED = "assistant_finished"  # 에이전트 실행 완료
    ERROR = "error"  # 에이전트 실행 오류


class Function(BaseModel):
    name: str
    arguments: str


class ToolCall(BaseModel):
    """메시지 내 도구/함수 호출을 나타냅니다."""

    id: str
    type: str = "function"
    function: Function


class Message(BaseModel):
    """대화 내 채팅 메시지를 나타냅니다."""

    role: ROLE_TYPE = Field(...)
    content: str | None = Field(default=None)
    tool_calls: list[ToolCall] | None = Field(default=None)
    name: str | None = Field(default=None)
    tool_call_id: str | None = Field(default=None)
    base64_image: str | None = Field(default=None)
    metadata: dict[str, Any] | None = Field(default=None)

    def __add__(self, other) -> list["Message"]:
        """Message와 리스트 또는 Message와 Message 연산을 지원합니다."""
        if isinstance(other, list):
            return [self] + other
        elif isinstance(other, Message):
            return [self, other]
        else:
            raise TypeError(
                f"지원되지 않는 연산 유형(들) +: '{type(self).__name__}' 및 '{type(other).__name__}'"
            )

    def __radd__(self, other) -> list["Message"]:
        """리스트와 Message 연산을 지원합니다."""
        if isinstance(other, list):
            return other + [self]
        else:
            raise TypeError(
                f"지원되지 않는 연산 유형(들) +: '{type(other).__name__}' 및 '{type(self).__name__}'"
            )

    def to_dict(self) -> dict:
        """메시지를 딕셔너리 형식으로 변환합니다.

        Returns:
            dict: 메시지 딕셔너리
        """
        message = {"role": self.role}
        if self.content is not None:
            message["content"] = self.content
        if self.tool_calls is not None:
            message["tool_calls"] = [tool_call.dict() for tool_call in self.tool_calls]
        if self.name is not None:
            message["name"] = self.name
        if self.tool_call_id is not None:
            message["tool_call_id"] = self.tool_call_id
        if self.base64_image is not None:
            message["base64_image"] = self.base64_image
        if self.metadata is not None:
            message["metadata"] = self.metadata
        return message

    @classmethod
    def user_message(
        cls,
        content: str,
        base64_image: str | None = None,
        metadata: dict | None = None,
    ) -> "Message":
        """사용자 메시지를 생성합니다.

        Args:
            content: 메시지 내용
            base64_image: 선택적 base64 인코딩 이미지
            metadata: 선택적 메타데이터

        Returns:
            Message: 사용자 메시지
        """
        return cls(
            role=Role.USER,
            content=content,
            base64_image=base64_image,
            metadata=metadata,
        )

    @classmethod
    def system_message(cls, content: str, metadata: dict | None = None) -> "Message":
        """시스템 메시지를 생성합니다.

        Args:
            content: 메시지 내용
            metadata: 선택적 메타데이터

        Returns:
            Message: 시스템 메시지
        """
        return cls(role=Role.SYSTEM, content=content, metadata=metadata)

    @classmethod
    def assistant_message(
        cls,
        content: str | None = None,
        base64_image: str | None = None,
        metadata: dict | None = None,
    ) -> "Message":
        """어시스턴트 메시지를 생성합니다.

        Args:
            content: 메시지 내용
            base64_image: 선택적 base64 인코딩 이미지
            metadata: 선택적 메타데이터

        Returns:
            Message: 어시스턴트 메시지
        """
        return cls(
            role=Role.ASSISTANT,
            content=content,
            base64_image=base64_image,
            metadata=metadata,
        )

    @classmethod
    def tool_message(
        cls,
        content: str,
        name,
        tool_call_id: str,
        base64_image: str | None = None,
        metadata: dict | None = None,
    ) -> "Message":
        """도구 메시지를 생성합니다.

        Args:
            content: 메시지 내용
            name: 도구 이름
            tool_call_id: 도구 호출 ID
            base64_image: 선택적 base64 인코딩 이미지
            metadata: 선택적 메타데이터

        Returns:
            Message: 도구 메시지
        """
        return cls(
            role=Role.TOOL,
            content=content,
            name=name,
            tool_call_id=tool_call_id,
            base64_image=base64_image,
            metadata=metadata,
        )

    @classmethod
    def from_tool_calls(
        cls,
        tool_calls: list[Any],
        content: str | list[str] = "",
        base64_image: str | None = None,
        **kwargs,
    ):
        """원시 도구 호출로부터 ToolCallsMessage를 생성합니다.

        Args:
            tool_calls: LLM의 원시 도구 호출
            content: 선택적 메시지 내용
            base64_image: 선택적 base64 인코딩 이미지
            **kwargs: Message 생성자에 전달할 추가 키워드 인자

        Returns:
            Message: 도구 메시지
        """
        formatted_calls = [
            {"id": call.id, "function": call.function.model_dump(), "type": "function"}
            for call in tool_calls
        ]
        return cls(
            role=Role.ASSISTANT,
            content=content,
            tool_calls=formatted_calls,
            base64_image=base64_image,
            **kwargs,
        )


class Memory(BaseModel):
    """단기 메모리 스키마.

    Args:
        messages: 메시지 목록
        max_messages: 최대 메시지 수
    """

    messages: list[Message] = Field(default_factory=list)
    max_messages: int = Field(default=30)

    def add_message(self, message: Message) -> None:
        """메모리에 메시지를 추가합니다."""
        self.messages.append(message)
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages :]

    def add_messages(self, messages: list[Message]) -> None:
        """메모리에 여러 메시지를 추가합니다."""
        self.messages.extend(messages)
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages :]

    def clear(self) -> None:
        """모든 메시지를 지웁니다."""
        self.messages.clear()

    def get_recent_messages(self, n: int) -> list[Message]:
        """최근 n개의 메시지를 가져옵니다."""
        return self.messages[-n:]

    def to_dict_list(self) -> list[dict]:
        """메시지 목록을 딕셔너리 목록으로 변환합니다."""
        return [msg.to_dict() for msg in self.messages]
