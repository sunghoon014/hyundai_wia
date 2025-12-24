import asyncio

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.responses import StreamingResponse
from mcp import ClientSession

from app.common.messaging.message_dispatcher import MessageDispatcher
from app.domains.chat.schemas.chat_request import ChatRequest, CreateSessionRequest
from app.domains.chat.schemas.chat_response import CreateSessionResponse
from app.domains.chat.services.chat_service import ChatService
from app.domains.containers import BaseContainer

chat_v1_router = APIRouter(prefix="/chats", tags=["Chats"])


@chat_v1_router.post(
    path="/sessions",
    summary="Create chat session",
    description="Create a new chat session with selected documents",
    response_model=CreateSessionResponse,
)
@inject
async def create_session(
    create_session_request: CreateSessionRequest,
    chat_service: ChatService = Depends(
        Provide[BaseContainer.chat_container.chat_service]
    ),
) -> CreateSessionResponse:
    return await chat_service.create_session(create_session_request)


@chat_v1_router.post(
    path="/stream",
    summary="Send chat message",
    description="Send a chat message and receive SSE streaming responses",
    response_class=StreamingResponse,
)
@inject
async def chat(
    request: Request,
    chat_request: ChatRequest,
    chat_service: ChatService = Depends(
        Provide[BaseContainer.chat_container.chat_service]
    ),
    message_dispatcher: MessageDispatcher = Depends(
        Provide[BaseContainer.chat_container.message_dispatcher]
    ),
) -> StreamingResponse:
    # app.state에서 중앙 관리되는 mcp_sessions를 가져옵니다.
    mcp_sessions: dict[str, ClientSession] = request.app.state.mcp_sessions
    message_queue = message_dispatcher.create_message_queue(chat_request.session_id)

    asyncio.create_task(
        chat_service.chat(
            chat_request=chat_request,
            message_queue=message_queue,
            mcp_sessions=mcp_sessions,  # ChatService로 세션을 전달합니다.
        )
    )
    return StreamingResponse(
        message_dispatcher.dispatch(chat_request.session_id),
        media_type="text/event-stream",
    )


# 헬퍼 함수
@chat_v1_router.get(
    path="/milvus/collections",
    summary="Get all Milvus collection names",
    description="Retrieve a list of all collection names from Milvus.",
    response_model=list[str],
)
@inject
async def get_all_milvus_collections(
    chat_service: ChatService = Depends(
        Provide[BaseContainer.chat_container.chat_service]
    ),
) -> list[str]:
    return await chat_service.get_all_milvus_collections()


@chat_v1_router.delete(
    path="/milvus/collections/{collection_name}",
    summary="Delete a Milvus collection by name",
    description="Delete a specific Milvus collection by its name.",
    status_code=status.HTTP_204_NO_CONTENT,
)
@inject
async def delete_milvus_collection(
    collection_name: str,
    chat_service: ChatService = Depends(
        Provide[BaseContainer.chat_container.chat_service]
    ),
) -> Response:
    await chat_service.delete_milvus_collection(collection_name)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@chat_v1_router.delete(
    path="/milvus/collections",
    summary="Clear all Milvus collections",
    description="Delete all collections from Milvus.",
    status_code=status.HTTP_204_NO_CONTENT,
)
@inject
async def clear_all_milvus_collections(
    chat_service: ChatService = Depends(
        Provide[BaseContainer.chat_container.chat_service]
    ),
) -> Response:
    await chat_service.clear_all_milvus_collections()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
