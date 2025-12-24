from datetime import datetime

from pydantic import BaseModel, Field

from app.domains import API_VERSION


class HealthCheckResponse(BaseModel):
    status: str = Field(description="서버 상태", default="ok")
    current_time: datetime = Field(
        description="서버 현재 시각", default_factory=datetime.now
    )

    class Config:
        json_schema_extra = {
            "example": {
                "status": "ok",
                "current_time": "2025-02-25T00:14:11.192043",
            }
        }


class APIInfoResponse(BaseModel):
    status: str = Field(description="API Status", default="ok")
    api_version: str = Field(description="API Version", default=API_VERSION)

    class Config:
        json_schema_extra = {
            "example": {
                "status": "ok",
                "api_version": API_VERSION,
            }
        }
