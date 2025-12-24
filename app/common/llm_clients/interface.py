from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator, Generator

from openai.types.chat import ChatCompletion, ChatCompletionChunk


class ILLMClient(ABC):
    @property
    @abstractmethod
    def model(self) -> str:
        """모델 이름 반환."""
        pass

    @abstractmethod
    async def agenerate(
        self,
        system_prompt: str,
        chat_messages: list[dict[str, any]] | None = None,
        /,
        **kwargs,
    ) -> ChatCompletion:
        """비동기 텍스트/이미지 생성."""
        pass

    @abstractmethod
    async def agenerate_stream(
        self,
        system_prompt: str,
        chat_messages: list[dict[str, any]] | None = None,
        /,
        **kwargs,
    ) -> AsyncGenerator[ChatCompletionChunk, None]:
        """비동기 스트림 생성."""
        pass

    @abstractmethod
    def generate(
        self,
        system_prompt: str,
        chat_messages: list[dict[str, any]] | None = None,
        /,
        **kwargs,
    ) -> ChatCompletion:
        """동기 텍스트/이미지 생성."""
        pass

    @abstractmethod
    def generate_stream(
        self,
        system_prompt: str,
        chat_messages: list[dict[str, any]] | None = None,
        /,
        **kwargs,
    ) -> Generator[ChatCompletionChunk, None, None]:
        """동기 스트림 생성."""
        pass
