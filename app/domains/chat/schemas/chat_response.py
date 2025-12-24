import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.common.utils import get_kst_now


class CreateSessionResponse(BaseModel):
    session_id: str = Field(..., description="세션 ID")
    updated_at: datetime = Field(
        default_factory=get_kst_now, description="세션 업데이트 시간"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "session_id": uuid.uuid4().hex,
                "updated_at": get_kst_now(),
            }
        }
    )
