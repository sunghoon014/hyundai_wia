"""FastAPI 라우터 설정을 관리하는 모듈입니다.

애플리케이션의 주요 API 라우터들을 구성하고 등록합니다.
"""

from fastapi import APIRouter

from app.domains.chat.apis.v1 import chat_v1_router
from app.domains.document.apis.v1 import document_v1_router

app_router = APIRouter()

app_router.include_router(
    prefix="/api/v1",
    router=chat_v1_router,
    tags=["Chats"],
)
app_router.include_router(
    prefix="/api/v1",
    router=document_v1_router,
    tags=["Documents"],
)
