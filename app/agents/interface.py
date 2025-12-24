from abc import ABC, abstractmethod

from app.agents.context.schema import Message
from app.common.messaging.message_queue import MessageQueue


class IAgent(ABC):
    """외부 도메인(Chat)에서 에이전트를 사용하기 위한 인터페이스."""

    @abstractmethod
    async def run_with_sse(self, request: str, message_queue: MessageQueue) -> str:
        """Chat 도메인에서 필요한 실행 메서드."""
        pass

    @abstractmethod
    async def cleanup(self) -> None:
        """리소스 정리."""
        pass

    @property
    @abstractmethod
    def messages(self) -> list[Message]:
        """메시지 기록 접근."""
        pass
