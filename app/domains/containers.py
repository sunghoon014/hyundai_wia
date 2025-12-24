from dependency_injector.containers import DeclarativeContainer, WiringConfiguration
from dependency_injector.providers import Configuration, Container, Object
from motor.motor_asyncio import AsyncIOMotorClient

from app.config.utils import init_config


class BaseContainer(DeclarativeContainer):
    """BaseContainer.

    - BaseContainer에서 설정값(env, yaml) 주입 받은 후, 도메인별 container 정의와 wiring 설정
    - 도메인별 container는 설정값만 주입 받음
    """

    # API 라우터 wiring 설정
    wiring_config = WiringConfiguration(
        packages=[
            "app.domains.chat.apis.v1",
            "app.domains.document.apis.v1",
            "app.domains.question.apis.v1",
        ]
    )

    # 설정값 주입
    config = Configuration()
    init_config(config)

    # MongoDB 설정
    _mongo_client_instance = AsyncIOMotorClient(config.mongo.db_url())
    _mongo_db_instance = _mongo_client_instance.get_database(config.mongo.db_name())
    mongo_db = Object(_mongo_db_instance)

    ########################################################
    # Domain Containers
    ########################################################
    from app.domains.chat.containers import ChatContainer
    from app.domains.document.containers import DocumentContainer

    chat_container = Container(ChatContainer, mongo_db=mongo_db)
    document_container = Container(DocumentContainer, mongo_db=mongo_db)
