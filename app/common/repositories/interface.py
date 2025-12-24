from abc import ABC, abstractmethod
from typing import Generic, TypeVar

PersistenceModel = TypeVar("PersistenceModel")


class IBaseRepository(ABC, Generic[PersistenceModel]):
    """제네릭 기본 리포지토리 인터페이스입니다.

    모든 리포지토리 구현체가 상속해야 하는 기본 CRUD (생성, 읽기, 갱신, 삭제)
    메서드들을 정의합니다.

    Type Args:
        PersistenceModel: 리포지토리가 처리하는 퍼시스턴스 모델의 타입입니다.
    """

    @abstractmethod
    async def create(self, model: PersistenceModel) -> PersistenceModel:
        """단일 퍼시스턴스 모델 인스턴스를 생성합니다.

        Args:
            model (PersistenceModel): 생성할 퍼시스턴스 모델 인스턴스입니다.

        Returns:
            PersistenceModel: 생성된 퍼시스턴스 모델 인스턴스입니다.
        """
        pass

    @abstractmethod
    async def bulk_create(self, models: list[PersistenceModel]) -> int:
        """여러 퍼시스턴스 모델 인스턴스들을 한 번에 생성합니다.

        Args:
            models (list[PersistenceModel]): 생성할 퍼시스턴스 모델 인스턴스들의 리스트입니다.

        Returns:
            int: 성공적으로 생성된 인스턴스의 개수입니다.
        """
        pass

    @abstractmethod
    async def update_by_id(
        self,
        model_id: str,
        params: dict,
    ) -> PersistenceModel:
        """ID를 기준으로 특정 퍼시스턴스 모델 인스턴스의 정보를 업데이트합니다.

        Args:
            model_id (str): 업데이트할 모델의 ID입니다.
            params (dict): 업데이트할 필드와 값들을 담은 딕셔너리입니다.

        Returns:
            PersistenceModel: 업데이트된 퍼시스턴스 모델 인스턴스입니다.

        Raises:
            ValueError: 해당 ID의 모델을 찾을 수 없는 경우 발생할 수 있습니다.
        """
        pass

    @abstractmethod
    async def get_all(self) -> list[PersistenceModel]:
        """해당 퍼시스턴스 모델의 모든 인스턴스를 조회합니다.

        Returns:
            list[PersistenceModel]: 조회된 퍼시스턴스 모델 인스턴스들의 리스트입니다.
        """
        pass

    @abstractmethod
    async def get_by_id(self, model_id: str) -> PersistenceModel | None:
        """ID를 기준으로 특정 퍼시스턴스 모델 인스턴스를 조회합니다.

        Args:
            model_id (str): 조회할 모델의 ID입니다.

        Returns:
            PersistenceModel | None: 조회된 퍼시스턴스 모델 인스턴스 또는 찾지 못한 경우 None입니다.
        """
        pass

    @abstractmethod
    async def delete_by_id(self, model_id: str) -> None:
        """ID를 기준으로 특정 퍼시스턴스 모델 인스턴스를 삭제합니다.

        Args:
            model_id (str): 삭제할 모델의 ID입니다.
        """
        pass
