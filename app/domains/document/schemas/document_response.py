from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.common.utils import get_kst_now


class Document(BaseModel):
    """Document schema for responses."""

    document_id: str = Field(..., description="Document ID")
    title: str = Field(..., description="Document title")
    uploaded_at: datetime = Field(
        default_factory=get_kst_now, description="Document upload timestamp"
    )
    summary: str = Field(..., description="Document summary")
    document_url: str = Field(..., description="Document URL")
    user_id: str = Field(..., description="User ID who owns the document")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "document_id": "ef1ef89372ea44dfaf6ab7da3b5ce16a",
                "title": "화성시 스마트시티 기본계획서",
                "uploaded_at": "2025-08-21T09:00:00Z",
                "summary": "화성시 스마트시티 구축을 위한 기본계획 및 로드맵을 제시하는 문서입니다. IoT 기반 인프라 구축, 빅데이터 활용 방안, 시민 서비스 개선 등을 포함합니다.",
                "document_url": "https://hwaseong.go.kr/documents/smart-city-master-plan.pdf",
                "user_id": "ssuhoon",
            }
        }
    )


class CreateDocumentSSEResponse(BaseModel):
    """Create document SSE response model."""

    status: str = Field(..., description="Processing status")
    document_id: str = Field(..., description="Document ID")
    percentage: int = Field(..., description="Processing percentage (0-100)")
    content: str = Field(..., description="Processing content")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "PARSING",
                "document_id": "doc-hwaseong-smart-city-001",
                "percentage": 25,
                "content": "Downloading PDF from URL...",
            }
        }
    )
