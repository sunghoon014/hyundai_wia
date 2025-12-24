import uuid

from fastapi import HTTPException
from mcp import ClientSession
from pydantic import ValidationError

from app.agents.context.schema import Message as AgentMessage
from app.common.exceptions.custom_exceptions import MessageQueueNeverStoppedError
from app.common.logger import logger
from app.common.messaging.message_queue import MessageQueue
from app.domains.chat.handlers.indexer.milvus import MilvusIndexer
from app.domains.chat.repositories.interface import IChatSessionRepository
from app.domains.chat.schemas.chat_request import ChatRequest, CreateSessionRequest
from app.domains.chat.schemas.chat_response import CreateSessionResponse
from app.domains.chat.schemas.enums import Role
from app.domains.chat.schemas.message import (
    ErrorEvent,
    Message,
    StopMessage,
    UserMessage,
)
from app.domains.chat.schemas.session import ChatSession
from app.domains.chat.services.interface import IChatAgent
from app.domains.document.repositories.interface import IDocumentRepository


class ChatService:
    """채팅 서비스 클래스입니다.

    사용자의 채팅 요청을 처리하고, 대화 기록과 이벤트(오류, 도구 호출 등)를 분리하여 관리합니다.
    """

    def __init__(
        self,
        chat_agent: IChatAgent,
        chat_session_repository: IChatSessionRepository,
        milvus_indexer: MilvusIndexer,
        document_repository: IDocumentRepository,
    ) -> None:
        self._chat_agent = chat_agent
        self._chat_session_repository = chat_session_repository
        self._milvus_indexer = milvus_indexer
        self._document_repository = document_repository

    async def create_session(
        self, create_session_request: CreateSessionRequest
    ) -> CreateSessionResponse:
        """세션을 생성합니다."""
        session_id = uuid.uuid4().hex
        user_id = create_session_request.user_id
        selected_document_ids = create_session_request.document_ids
        if not selected_document_ids:
            chat_session = ChatSession(chat_session_id=session_id, user_id=user_id)
            await self._chat_session_repository.save(chat_session)
            return CreateSessionResponse(session_id=session_id)

        documents = await self._document_repository.find_by_user_id(user_id)
        if not documents:
            raise HTTPException(status_code=404, detail="Documents not found")

        all_documents = []
        for doc in documents:
            doc_dict = doc.model_dump()
            if doc_dict["document_id"] in selected_document_ids:
                doc_dict["collection_name"] = f"c_{user_id}_{session_id}"
                all_documents.append(doc_dict)

        await self._milvus_indexer.aindex_documents(all_documents)
        return CreateSessionResponse(session_id=session_id)

    async def chat(
        self,
        chat_request: ChatRequest,
        message_queue: MessageQueue,
        mcp_sessions: dict[str, ClientSession] | None = None,
    ) -> None:
        """사용자의 요청에 대한 채팅을 처리하고 전체 대화 내용과 이벤트를 저장합니다."""
        # 1. 채팅 세션을 조회하거나 새로 생성합니다.
        chat_session = await self._chat_session_repository.find_by_id(
            chat_request.session_id
        )
        if chat_session is None:
            await message_queue.put(StopMessage())
            raise HTTPException(status_code=404, detail="Session not found")

        # 2. 사용자 메시지를 생성하여 history에 추가합니다.
        user_message = UserMessage(content=chat_request.content)
        chat_session.history.append(user_message)

        # 3. 에이전트를 실행하고, 발생할 수 있는 예외는 'events'에 기록합니다.
        try:
            await self._chat_agent.run(
                chat_request, chat_session.history, message_queue, mcp_sessions
            )
        except Exception as e:
            logger.error(f"Error during chat agent execution: {e}")
            status_code = getattr(e, "status_code", 500)
            error_code = getattr(e, "error_code", "INTERNAL_SERVER_ERROR")
            # NOTE: [비즈니스 요구사항] 에이전트 실행 중 발생한 오류를 나타내는 메시지입니다.
            error_event = ErrorEvent(
                content=str(e),
                metadata={"status_code": status_code, "error_code": error_code},
            )
            await message_queue.put(error_event)
            chat_session.events.append(error_event)
        finally:
            # NOTE: [비즈니스 요구사항] 클라이언트에게 스트리밍 종료를 알리는 메시지입니다.
            await message_queue.put(StopMessage())

        # 4. 스트리밍 종료를 기다립니다.
        await message_queue.wait_for_finished()
        if not message_queue.is_stop_message_processed():
            logger.error(
                f"StopMessage was not processed for session {chat_request.session_id}. This might indicate an issue in the service logic if it wasn't an error flow."
            )
            raise MessageQueueNeverStoppedError()

        # 5. 스트리밍 된 메시지들을 최종적으로 분류하여 세션에 추가합니다.
        new_history, new_events = self._process_agent_output(message_queue.messages)
        chat_session.history.extend(new_history)
        chat_session.events.extend(new_events)

        # 6. 모든 내용이 담긴 세션 전체를 한 번에 저장합니다.
        await self._chat_session_repository.save(chat_session)
        logger.info(
            f"Chat session {chat_session.chat_session_id} saved. "
            f"History: {len(chat_session.history)} messages, "
            f"Events: {len(chat_session.events)} items."
        )

    def _process_agent_output(
        self, agent_messages: list[AgentMessage]
    ) -> tuple[list[Message], list[Message]]:
        """에이전트의 최종 메모리 출력을 history와 events용으로 분류합니다.

        - history: 다음 대화의 LLM 문맥으로 사용될 AI의 최종 답변만 저장합니다.
        - events: AI가 답변을 만들기까지의 중간 과정(실행, 링크 참조 등)을 저장합니다.
        """
        new_history: list[Message] = []
        new_events: list[Message] = []
        interaction_id = uuid.uuid4().hex  # 이번 상호작용(turn)에 대한 고유 ID 생성

        for agent_msg in agent_messages:
            agent_msg_data = agent_msg.model_dump()

            # 1. metadata에서 상태(state) 값을 추출
            state_from_meta = (
                agent_msg_data.get("metadata", {}).get("state")
                if agent_msg_data.get("metadata")
                else None
            )

            # 2. 상태값이나 원래 role을 기반으로 chat 도메인에 맞는 최종 role 결정
            target_role_str = state_from_meta or agent_msg_data.get("role")
            agent_msg_data["role"] = target_role_str

            # 3. 매핑 ID 추가
            if "metadata" not in agent_msg_data or agent_msg_data["metadata"] is None:
                agent_msg_data["metadata"] = {}
            agent_msg_data["metadata"]["interaction_id"] = interaction_id

            # 4. 변환된 데이터로 chat.Message 생성
            try:
                chat_msg = Message(**agent_msg_data)
            except ValidationError as e:
                logger.warning(
                    f"Skipping agent message with unmappable role '{target_role_str}': {e}"
                )
                continue

            # 5. 최종 role에 따라 history와 events에 분리 저장
            if chat_msg.role == Role.ASSISTANT_FINISHED:
                new_history.append(chat_msg)
            elif chat_msg.role in [
                Role.ASSISTANT_RUNNING,
                Role.DOC_LINK,
                Role.WEB_LINK,
            ]:
                new_events.append(chat_msg)

        return new_history, new_events

    async def get_all_milvus_collections(self) -> list[str]:
        """Milvus에 있는 모든 컬렉션의 이름을 조회합니다."""
        return await self._milvus_indexer.alist_collections()

    async def delete_milvus_collection(self, collection_name: str) -> None:
        """지정된 이름의 Milvus 컬렉션을 삭제합니다."""
        await self._milvus_indexer.adelete_collection(collection_name)

    async def clear_all_milvus_collections(self) -> None:
        """Milvus의 모든 컬렉션을 삭제합니다."""
        await self._milvus_indexer.aclear_all_collections()
