from asyncio import Event, Queue

from loguru import logger

from app.domains.chat.schemas.message import StopMessage


class MessageQueue(Queue):
    """메시지 큐 클래스.

    MessageDispatcher에 주입되어 사용자 요청 주기로 발생되는 모든 Server-Sent Event를 받아서 Dispatcher에 전달
    서비스 계층에서 SSE 메시지 중 유저, 어시스턴트 메시지를 저장할 수 있도록 messages에 따로 acculmulate
    """

    def __init__(self):
        super().__init__()
        self._messages = []
        self._stop_message_processed = Event()  # Event to signal StopMessage processing

    def __del__(self):
        logger.info(f"MessageQueue {id(self)} is being deleted")

    @property
    def messages(self) -> list:
        """큐를 통과한 모든 메시지들의 누적 리스트입니다."""
        return self._messages

    async def wait_for_finished(self) -> None:
        """큐의 모든 메시지가 처리될 때까지 대기합니다."""
        await self._stop_message_processed.wait()

    def is_stop_message_processed(self) -> bool:
        """StopMessage가 이미 처리되었는지 여부를 반환합니다."""
        return self._stop_message_processed.is_set()

    async def __aiter__(self):
        """큐의 메시지들을 비동기적으로 반복합니다.

        StopMessage를 감지하면 내부 이벤트를 설정하고 반복을 종료합니다.
        """
        while True:
            message = await self.get()

            self._messages.append(message)

            if isinstance(message, StopMessage):
                self._stop_message_processed.set()

            try:
                yield message
            finally:
                self.task_done()

            if isinstance(message, StopMessage):
                break
