import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.common.utils import get_kst_now


# TODO: 몽고 디비에 한국 시간 저장이 안됨. 모델 레벨에서 한국 시간으로 변환하는 로직 추가 필요
class Document(BaseModel):
    """MongoDB 'documents' 컬렉션에 저장될 문서의 영속성 모델입니다."""

    document_id: str = Field(
        default_factory=lambda: uuid.uuid4().hex, description="MongoDB 문서의 고유 ID"
    )
    title: str = Field(..., description="문서 제목")
    summary: str = Field(..., description="문서 요약")
    content: list[Any] = Field(..., description="문서 내용")
    document_url: str = Field(..., description="문서 URL")
    user_id: str = Field(..., description="문서를 소유한 사용자 ID")
    updated_at: datetime = Field(
        default_factory=get_kst_now, description="문서 생성 시간 (업로드 시간)"
    )
