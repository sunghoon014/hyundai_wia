from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from loguru import logger

from app.domains.containers import BaseContainer
from app.domains.document.schemas.document_request import (
    CreateDocumentRequest,
    DeleteDocumentRequest,
)
from app.domains.document.schemas.document_response import Document
from app.domains.document.services.document_service import DocumentService

document_v1_router = APIRouter(prefix="/documents", tags=["Documents"])


@document_v1_router.get(
    path="/{document_id}",
    summary="Get document by ID",
    description="Get a single document by its ID",
    response_model=Document,
)
@inject
async def get_document(
    document_id: str,
    document_service: DocumentService = Depends(
        Provide[BaseContainer.document_container.document_service]
    ),
) -> Document:
    """Get a single document by ID.

    Args:
        document_id: Get document request
        document_service: Document service instance.

    Returns:
        Document: Document data
    """
    logger.info(f"GET /documents/{document_id} called")

    try:
        response = await document_service.get_document(document_id)
        logger.info("Successfully retrieved document")
        return response
    except ValueError as e:
        logger.error(f"Document not found: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Error getting document: {str(e)}")
        raise e


@document_v1_router.get(
    path="",
    summary="Get documents",
    description="Get documents filtered by user ID",
    response_model=list[Document],
)
@inject
async def get_documents(
    user_id: str = Query(..., description="User ID to filter documents"),
    document_service: DocumentService = Depends(
        Provide[BaseContainer.document_container.document_service]
    ),
) -> list[Document]:
    """Get documents filtered by user ID.

    Args:
        user_id: User ID to filter documents
        document_service: Document service instance.

    Returns:
        list[Document]: Documents data
    """
    logger.info(f"GET /documents called with user_id: {user_id}")

    try:
        response = await document_service.get_documents(user_id)
        logger.info(f"Successfully get {len(response)} documents")
        return response
    except ValueError as e:
        logger.error(f"Error getting documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@document_v1_router.post(
    path="",
    summary="Create document",
    description="Create a new document with SSE processing updates",
    response_class=StreamingResponse,
)
@inject
async def create_document(
    create_request: CreateDocumentRequest,
    document_service: DocumentService = Depends(
        Provide[BaseContainer.document_container.document_service]
    ),
) -> StreamingResponse:
    """Create a new document with SSE processing updates.

    Args:
        create_request: Create document request
        document_service: Document service instance.

    Returns:
        StreamingResponse: SSE stream with processing updates
    """
    logger.info(f"POST /documents called with URL: {create_request.document_url}")

    try:

        async def generate_sse():
            async for update in document_service.create_document(create_request):
                sse_data = f"{update.model_dump_json()}\n\n"
                yield sse_data

        return StreamingResponse(
            generate_sse(),
            media_type="text/event-stream",
        )
    except Exception as e:
        logger.error(f"Error creating document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@document_v1_router.post(
    path="/delete",
    summary="Delete document",
    description="Delete a document",
    response_model=dict,
)
@inject
async def delete_document(
    delete_request: DeleteDocumentRequest,
    document_service: DocumentService = Depends(
        Provide[BaseContainer.document_container.document_service]
    ),
) -> dict:
    """Delete a document.

    Args:
        delete_request: Delete document request
        document_service: Document service instance.

    Returns:
        DeleteDocumentResponse: Delete document response
    """
    logger.info(
        f"POST /documents/delete called for document: {delete_request.document_id}"
    )

    try:
        response = await document_service.delete_document(delete_request.document_id)
        return response
    except ValueError as e:
        logger.error(f"Document not found: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e)) from e
