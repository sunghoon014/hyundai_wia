import json
import weakref
from collections.abc import AsyncGenerator

from app.common.messaging.message_queue import MessageQueue
from app.domains.chat.schemas.message import Message, StopMessage


class MessageDispatcher:
    def __init__(self):
        self._message_queues: dict[str, weakref.ref[MessageQueue]] = {}

    def create_message_queue(self, session_id: str) -> MessageQueue:
        # If message queue already exists, remove it first
        # 메시지 큐는 사용자 요청에 대한 생성 주기를 가지며, 이미 존재하는 큐는 삭제하고 새로 생성합니다.
        # weakref로 자동으로 삭제되도록 설정
        if (
            message_queue_ref := self._message_queues.get(session_id)
        ) and message_queue_ref():
            self.remove_message_queue(session_id)

        new_message_queue = MessageQueue()
        self._message_queues[session_id] = weakref.ref(new_message_queue)

        return new_message_queue

    def get_message_queue(self, session_id: str) -> MessageQueue:
        if not (message_queue_ref := self._message_queues.get(session_id)):
            raise ValueError(f"Message queue for session {session_id} not found")

        if not (message_queue := message_queue_ref()):
            raise ValueError(f"Message queue for session {session_id} is deleted")

        return message_queue

    def remove_message_queue(self, session_id: str) -> None:
        del self._message_queues[session_id]

    async def dispatch(self, session_id: str) -> AsyncGenerator[str, None]:
        if not (message_queue_ref := self._message_queues.get(session_id)):
            raise ValueError(f"Message queue for session {session_id} not found")

        if not (message_queue := message_queue_ref()):
            raise ValueError(f"Message queue for session {session_id} is deleted")

        async for message in message_queue:
            if isinstance(message, StopMessage):
                yield f"data: {self._to_json(message)}\n\n"
                break

            yield f"data: {self._to_json(message)}\n\n"

    def _to_json(self, message: Message) -> str:
        data = {
            "role": message.role.value,
            "content": message.content,
            "metadata": message.metadata if message.metadata else {},
        }
        return json.dumps(data, default=lambda x: x.__dict__, ensure_ascii=False)
