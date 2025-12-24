from loguru import logger
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.common.repositories.mongo_base_repository import MongoBaseRepository
from app.domains.document.repositories.interface import IDocumentRepository
from app.domains.document.repositories.mongo_models import Document as MongoDocument


class MongoDocumentRepository(IDocumentRepository, MongoBaseRepository[MongoDocument]):
    """MongoDB 'documents' 컬렉션에 대한 리포지토리 구현체입니다.

    BaseRepository의 기능을 최소한으로 사용하며,
    대부분의 변환 로직을 이 클래스 내에 직접 구현합니다.
    """

    def __init__(self, db: AsyncIOMotorDatabase):
        """MongoDocumentRepository의 생성자입니다."""
        super().__init__(
            db=db, collection_name="documents", domain_model_cls=MongoDocument
        )

    async def save(self, domain_obj: MongoDocument) -> None:
        """Document를 저장하거나 업데이트합니다 (upsert)."""
        document_dict = domain_obj.model_dump(exclude_none=True)
        document_id = document_dict.pop("document_id")

        await self.collection.update_one(
            {"_id": document_id},
            {"$set": document_dict},
            upsert=True,
        )

    async def find_by_id(self, document_id: str) -> MongoDocument | None:
        """ID로 문서를 찾습니다."""
        document = await self.collection.find_one({"_id": document_id})
        if not document:
            logger.warning(f"Document not found: {document_id}")
            return None
        document_id = document.pop("_id")
        document["document_id"] = document_id
        return MongoDocument.model_validate(document) if document else None

    async def find_by_user_id(self, user_id: str) -> list[MongoDocument]:
        """User ID로 문서를 찾습니다."""
        documents = await self.collection.find({"user_id": user_id}).to_list(
            length=None
        )
        results = []
        for doc in documents:
            results.append(
                MongoDocument(
                    document_id=doc.pop("_id"),
                    title=doc.pop("title"),
                    summary=doc.pop("summary"),
                    content=doc.pop("content"),
                    document_url=doc.pop("document_url"),
                    user_id=doc.pop("user_id"),
                    updated_at=doc.pop("updated_at"),
                )
            )
        return results

    async def find_all(self) -> list[MongoDocument]:
        """모든 문서를 찾아 리스트로 반환합니다."""
        documents = await self.collection.find().to_list(length=None)
        return [MongoDocument.model_validate(doc) for doc in documents]

    async def delete(self, document_id: str) -> None:
        """문서를 삭제합니다."""
        await self.collection.delete_one({"_id": document_id})
