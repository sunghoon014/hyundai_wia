from typing import Self

from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict, Field, model_validator


class CreateDocumentRequest(BaseModel):
    """Create document request model."""

    user_id: str = Field(..., description="User ID who owns the document")
    document_url: str = Field(..., description="Document URL")
    file_name: str = Field(..., description="File name")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_id": "ssuhoon",
                "document_url": "https://hwaseong.go.kr/documents/smart-city-plan.pdf",
                "file_name": "smart-city-plan.pdf",
            }
        }
    )

    @model_validator(mode="after")
    def validate_fields(self) -> Self:
        """Validate that required fields are not empty."""
        if not self.document_url or self.document_url.strip() == "":
            raise HTTPException(
                status_code=422,
                detail="Document URL cannot be empty or contain only whitespace",
            )
        if not self.user_id or self.user_id.strip() == "":
            raise HTTPException(
                status_code=422,
                detail="User ID cannot be empty or contain only whitespace",
            )
        return self


class DeleteDocumentRequest(BaseModel):
    """Delete document request model."""

    document_id: str = Field(..., description="Document ID")

    model_config = ConfigDict(
        json_schema_extra={"example": {"document_id": "doc-hwaseong-smart-city-001"}}
    )

    @model_validator(mode="after")
    def validate_document_id(self) -> Self:
        """Validate that document_id is not empty."""
        if not self.document_id or self.document_id.strip() == "":
            raise HTTPException(
                status_code=422,
                detail="Document ID cannot be empty or contain only whitespace",
            )
        return self
