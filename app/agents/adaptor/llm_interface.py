from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator

from openai.types.chat import ChatCompletionChunk, ChatCompletionMessage

from app.agents.context.schema import TOOL_CHOICE_TYPE, Message, ToolChoice


class ILLMAdapter(ABC):
    """에이전트가 LLM과 상호작용하는 데 필요한 메서드를 정의하는 인터페이스입니다."""

    @abstractmethod
    async def ask(
        self,
        messages: list[dict | Message],
        system_msgs: list[dict | Message] | None = None,
        **kwargs,
    ) -> ChatCompletionMessage | None:
        """LLM에 메시지 사용을 요청하고 응답을 반환합니다."""
        pass

    @abstractmethod
    async def ask_streaming(
        self,
        messages: list[dict | Message],
        system_msgs: list[dict | Message] | None = None,
        **kwargs,
    ) -> AsyncGenerator[ChatCompletionChunk, None]:
        """LLM에 메시지 사용을 요청하고 응답을 스트리밍으로 반환합니다."""
        pass

    @abstractmethod
    async def ask_tool(
        self,
        messages: list[dict | Message],
        system_msgs: list[dict | Message] | None = None,
        tools: list[dict] | None = None,
        tool_choice: TOOL_CHOICE_TYPE = ToolChoice.AUTO,
        **kwargs,
    ) -> ChatCompletionMessage | None:
        """LLM에 도구 사용을 요청하고 응답을 반환합니다. (Non-streaming)."""
        pass

    @abstractmethod
    async def ask_tool_streaming(
        self,
        messages: list[dict | Message],
        system_msgs: list[dict | Message] | None = None,
        tools: list[dict] | None = None,
        tool_choice: TOOL_CHOICE_TYPE = ToolChoice.AUTO,
        **kwargs,
    ) -> AsyncGenerator[ChatCompletionChunk, None]:
        """LLM에 도구 사용을 요청하고 응답을 스트리밍으로 반환합니다."""
        pass
