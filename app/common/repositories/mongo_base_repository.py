from typing import Any, TypeVar

from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel

from app.common.repositories.interface import IBaseRepository

DomainModel = TypeVar("DomainModel", bound=BaseModel)


class MongoBaseRepository(IBaseRepository[DomainModel]):
    """MongoDB 상호작용을 위한 기본 리포지토리입니다."""

    def __init__(
        self,
        db: AsyncIOMotorDatabase,
        collection_name: str,
        domain_model_cls: type[DomainModel],
    ):
        """MongoBaseRepository의 생성자입니다.

        Args:
            db (AsyncIOMotorDatabase): Motor 데이터베이스 인스턴스입니다.
            collection_name (str): 상호작용할 MongoDB 컬렉션의 이름입니다.
            domain_model_cls (type[DomainModel]): 이 리포지토리에서 처리할 도메인 모델의 실제 클래스입니다.
        """
        self._db = db
        self._collection = self._db.get_collection(collection_name)
        self._domain_model_cls = domain_model_cls

    @property
    def collection(self):
        return self._collection

    def _to_domain(self, document: dict) -> DomainModel:
        """MongoDB 문서를 도메인 모델로 변환."""
        return self._domain_model_cls(**document)

    def _to_document(self, domain_obj: DomainModel) -> dict:
        """도메인 모델을 MongoDB 문서로 변환."""
        return domain_obj.model_dump(by_alias=True)

    async def get_all(self) -> list[DomainModel]:
        """컬렉션의 모든 문서를 조회하여 도메인 모델 리스트로 반환합니다."""
        models = []
        async for model in self._collection.find():
            models.append(self._to_domain(model))
        return models

    async def get_by_id(self, model_id: str) -> DomainModel | None:
        """ID를 기준으로 특정 문서를 데이터베이스에서 조회합니다."""
        model = await self._collection.find_one({"id": model_id})
        return self._to_domain(dict(model)) if model else None

    async def create(self, schema: DomainModel) -> DomainModel:
        """단일 도메인 모델 인스턴스를 기반으로 문서를 데이터베이스에 생성합니다."""
        entity = self._to_document(schema)
        await self._collection.insert_one(entity)
        return self._to_domain(entity)

    async def update_by_id(self, model_id: str, params: dict) -> None:
        """ID를 기준으로 특정 문서의 정보를 업데이트합니다."""
        await self._collection.update_one({"id": model_id}, {"$set": params})

    async def delete_by_id(self, model_id: str) -> None:
        """ID를 기준으로 특정 문서를 데이터베이스에서 삭제합니다."""
        await self._collection.delete_one({"id": model_id})

    async def bulk_create(self, models: list[DomainModel]) -> int:
        """여러 도메인 모델 인스턴스들을 데이터베이스에 한 번에 생성합니다."""
        return await super().bulk_create(models)
