from abc import ABC, abstractmethod

from app.domains.document.repositories.mongo_models import Document


class IDocumentRepository(ABC):
    """Document 저장소에 대한 인터페이스입니다."""

    @abstractmethod
    async def save(self, document: Document) -> None:
        """Document를 저장합니다."""
        pass

    @abstractmethod
    async def find_by_id(self, document_id: str) -> Document | None:
        """Find a document by its ID.

        Args:
            document_id: The ID of the document.

        Returns:
            The document if found, otherwise None.
        """
        ...

    @abstractmethod
    async def find_all(self) -> list[Document]:
        """Find all documents.

        Returns:
            A list of all documents.
        """
        ...
