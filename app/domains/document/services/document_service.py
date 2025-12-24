import re
import uuid
from collections.abc import AsyncGenerator

from fastapi import HTTPException

from app.common.logger import logger
from app.domains.document.enums import DocumentProcessingStatus
from app.domains.document.repositories.interface import IDocumentRepository
from app.domains.document.repositories.mongo_models import Document as MongoDocument
from app.domains.document.schemas.document_request import CreateDocumentRequest
from app.domains.document.schemas.document_response import (
    CreateDocumentSSEResponse,
    Document,
    get_kst_now,
)
from app.domains.document.services.parsing_service import ParsingService


class DocumentService:
    """Document 서비스 클래스입니다.

    Knowledge Center의 문서 관리 및 처리를 담당합니다.
    """

    def __init__(
        self,
        parsing_service: ParsingService,
        document_repository: IDocumentRepository,
    ):
        """Initialize the document service.

        Args:
            parsing_service: Parsing service instance
            document_repository: Document repository instance
        """
        self.parsing_service = parsing_service
        self.document_repository = document_repository

    def _extract_tag_content(self, content, tag):
        pattern = rf"<{tag}>(.*?)</{tag}>"
        match = re.search(pattern, content, re.DOTALL)

        if match:
            return match.group(1).strip()
        else:
            return None

    async def create_document(
        self, request: CreateDocumentRequest
    ) -> AsyncGenerator[CreateDocumentSSEResponse, None]:
        """Create a new document with SSE processing updates.

        Args:
            request: Create document request
        """
        # # 1. 문서 파싱 & 파싱 중간 결과 SSE로 전송
        document_id = uuid.uuid4().hex

        parsed_docs = None
        async for event in self.parsing_service.parse_document(
            request.document_url, request.file_name
        ):
            if event.get("node") == "final_state":
                parsed_docs = event
                break
            if event.get("role"):
                yield CreateDocumentSSEResponse(
                    document_id=document_id,
                    status=event.get("role"),
                    percentage=event.get("percentage"),
                    content=event.get("content"),
                )

        if not parsed_docs:
            raise ValueError(
                "문서 파싱 결과가 없습니다. parsed_docs가 None 또는 비어 있습니다."
            )

        # 2. MongoDB에 저장
        document_to_save = MongoDocument(
            document_id=document_id,
            title=request.file_name,
            summary=parsed_docs.get("summary"),
            content=parsed_docs.get("content"),
            document_url=parsed_docs.get("document_url"),
            user_id=request.user_id,
        )

        await self.document_repository.save(document_to_save)

        yield CreateDocumentSSEResponse(
            document_id=document_id,
            status=DocumentProcessingStatus.SAVED.status,
            percentage=100,
            content="Completed saving documents.",
        )

    async def delete_document(self, document_id: str) -> dict:
        """Delete a document.

        Args:
            document_id: Document ID
        """
        await self.document_repository.delete(document_id)
        logger.info(f"Document {document_id} deleted successfully")

        return {"message": f"Document {document_id} deleted successfully"}

    async def get_document(self, document_id: str) -> Document:
        """Get a single document by ID.

        Args:
            document_id: Document ID

        Raises:
            HTTPException: 404 if document not found
        """
        result = await self.document_repository.find_by_id(document_id)
        if not result:
            raise HTTPException(
                status_code=404, detail=f"Document {document_id} not found"
            )

        result_dict = result.model_dump()
        result_dict["uploaded_at"] = result_dict.pop("updated_at")
        extracted_summary = self._extract_tag_content(
            result_dict["summary"], "one_line_summary"
        )
        if extracted_summary:
            result_dict["summary"] = extracted_summary

        return Document(**result_dict)

    async def get_documents(self, user_id: str | None = None) -> list[Document]:
        """Get documents filtered by user ID.

        Args:
            user_id: User ID to filter documents
        """
        documents = await self.document_repository.find_by_user_id(user_id)
        if not documents:
            raise HTTPException(
                status_code=404, detail=f"No documents found for user {user_id}"
            )

        results = []
        for doc in documents:
            doc_dict = doc.model_dump()
            doc_dict["uploaded_at"] = doc_dict.pop("updated_at")
            extracted_summary = self._extract_tag_content(
                doc_dict["summary"], "one_line_summary"
            )
            if extracted_summary:
                doc_dict["summary"] = extracted_summary
            results.append(Document(**doc_dict))
        return results
