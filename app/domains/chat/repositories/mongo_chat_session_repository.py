from datetime import datetime
from enum import Enum

import pytz
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.common.repositories.mongo_base_repository import MongoBaseRepository
from app.domains.chat.repositories.interface import IChatSessionRepository
from app.domains.chat.schemas.session import ChatSession


class MongoChatSessionRepository(
    IChatSessionRepository, MongoBaseRepository[ChatSession]
):
    """MongoDB 'chat_sessions' 컬렉션에 대한 리포지토리 구현체입니다."""

    def __init__(self, db: AsyncIOMotorDatabase):
        """MongoChatSessionRepository의 생성자입니다."""
        super().__init__(
            db=db, collection_name="chat_sessions", domain_model_cls=ChatSession
        )

    async def find_by_id(self, id: str) -> ChatSession | None:
        """고유 ID로 채팅 세션을 찾습니다."""
        document = await self.collection.find_one({"_id": id})
        if not document:
            return None
        # MongoDB의 `_id`를 Pydantic 모델의 `chat_session_id`로 매핑합니다.
        document["chat_session_id"] = str(document.pop("_id"))
        return self._to_domain(document)

    async def save(self, domain_obj: ChatSession) -> None:
        """채팅 세션 전체를 저장하거나 업데이트합니다 (upsert).

        효율성 개선 참고: 현재는 세션 전체를 덮어쓰고 있습니다.
        성능 최적화가 필요하다면, 변경된 필드만 업데이트하거나
        $push 연산자를 사용해 history/events에 메시지를 추가하는 방식으로 개선할 수 있습니다.
        """
        session_dict = domain_obj.model_dump(exclude_none=True)
        session_id = session_dict.pop("chat_session_id")

        # history와 events 리스트의 각 Message 객체를 DB에 저장하기 좋은 dict 형태로 변환합니다.
        # 이 때 role이 Enum 객체이면 .value를 사용해 문자열로 변환합니다.
        for msg_list_name in ["history", "events"]:
            if msg_list_name in session_dict:
                converted_list = []
                for msg_obj_dict in session_dict[msg_list_name]:
                    if "role" in msg_obj_dict and isinstance(
                        msg_obj_dict["role"], Enum
                    ):
                        msg_obj_dict["role"] = msg_obj_dict["role"].value
                    converted_list.append(msg_obj_dict)
                session_dict[msg_list_name] = converted_list

        session_dict["updated_at"] = datetime.now(pytz.utc)
        await self.collection.update_one(
            {"_id": session_id},
            {"$set": session_dict},
            upsert=True,
        )
