from abc import ABC, abstractmethod

from app.domains.chat.schemas.message import Message
from app.domains.chat.schemas.session import ChatSession


class ISessionRepository(ABC):
    """세션 관련 데이터 처리를 위한 인터페이스입니다.

    세션 생성 및 조회를 위한 메서드들을 정의합니다.
    """

    @abstractmethod
    async def create_session(self, session: ChatSession) -> None:
        """새로운 세션을 생성합니다.

        Args:
            session (Session): 생성할 세션 도메인 모델 객체입니다.
        """
        pass

    @abstractmethod
    async def find_session_by_id(self, session_id: str) -> ChatSession | None:
        """세션 ID를 기준으로 특정 세션을 조회합니다.

        세션에 속한 메시지들을 포함하여 조회합니다.

        Args:
            session_id (str): 조회할 세션의 ID입니다.

        Returns:
            Session | None: 조회된 세션 도메인 모델 객체 또는 찾지 못한 경우 None입니다.
        """
        pass


class IMessageRepository(ABC):
    """메시지 관련 데이터 처리를 위한 인터페이스입니다.

    메시지 저장 기능을 위한 메서드들을 정의합니다.
    """

    @abstractmethod
    async def save_message(self, message: Message, session_id: str) -> None:
        """단일 메시지를 특정 세션에 저장합니다.

        Args:
            message (Message): 저장할 메시지 도메인 모델 객체입니다.
            session_id (str): 메시지가 속한 세션의 ID입니다.
        """
        pass

    @abstractmethod
    async def save_messages(self, messages: list[Message], session_id: str) -> None:
        """여러 메시지를 특정 세션에 한 번에 저장합니다.

        Args:
            messages (list[Message]): 저장할 메시지 도메인 모델 객체들의 리스트입니다.
            session_id (str): 메시지들이 속한 세션의 ID입니다.
        """
        pass

    @abstractmethod
    async def find_messages_by_session_id(self, session_id: str) -> list[Message]:
        """세션 ID를 기준으로 특정 세션에 속한 모든 메시지를 조회합니다."""
        pass


class IChatSessionRepository(ABC):
    """채팅 세션 저장소에 대한 인터페이스입니다."""

    @abstractmethod
    async def find_by_id(self, session_id: str) -> ChatSession | None:
        """고유 ID로 채팅 세션을 찾습니다."""
        pass

    @abstractmethod
    async def save(self, session: ChatSession) -> None:
        """채팅 세션을 저장합니다 (존재하지 않으면 생성, 존재하면 덮어쓰기)."""
        pass
