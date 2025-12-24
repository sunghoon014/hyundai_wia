from datetime import datetime

import pytz
from pydantic import BaseModel, Field

from app.domains.chat.schemas.message import Message


class ChatSession(BaseModel):
    """채팅 세션을 나타내는 도메인 모델입니다."""

    chat_session_id: str = Field(..., description="채팅 세션의 고유 ID")
    user_id: str = Field(..., description="사용자의 고유 ID")
    documents: list[str] = Field(
        default_factory=list,
        description="문서 ID 목록",
    )

    history: list[Message] = Field(
        default_factory=list,
        description="AI 컨텍스트용, 사용자와 어시스턴트의 대화 기록",
    )
    events: list[Message] = Field(
        default_factory=list,
        description="분석/로깅용, Tool-call, Error, Assistant 중간 응답 등의 이벤트 기록",
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(pytz.UTC), description="세션 생성 시간"
    )
