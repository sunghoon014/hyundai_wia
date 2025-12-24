import uuid
from typing import Self

from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict, Field, model_validator


class CreateSessionRequest(BaseModel):
    user_id: str = Field(..., description="사용자 ID")
    document_ids: list[str] = Field(..., description="문서 ID 목록")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_id": "string",
                "document_ids": [],
            }
        }
    )


class ChatRequest(BaseModel):
    session_id: str = Field(..., description="세션 ID")
    tool_server_ids: list[str] = Field(
        [], description="사용할 MCP 서버 ID 목록 (mcp.json)"
    )
    content: str = Field(..., max_length=1024, description="사용자 입력 내용")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "session_id": str(uuid.uuid4().hex),
                "tool_server_ids": ["web_search"],
                "content": "안녕. 너는 누구야?",
            }
        }
    )

    @model_validator(mode="after")
    def check_fields_not_empty(self) -> Self:
        """Check that user_id, session_id, and content are not empty or whitespace only."""
        if not self.session_id or self.session_id.strip() == "":
            raise HTTPException(
                status_code=422,
                detail="session_id cannot be empty or contain only whitespace",
            )

        if not self.content or self.content.strip() == "":
            raise HTTPException(
                status_code=422,
                detail="content cannot be empty or contain only whitespace",
            )

        return self
