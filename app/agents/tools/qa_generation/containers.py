from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Container, Object
from motor.motor_asyncio import AsyncIOMotorClient

from app.config.utils import init_config
from app.domains.question.containers import QuestionContainer


class QAGenerationContainer(DeclarativeContainer):
    """Dependency injection container for QA Generation tools."""

    config = Configuration()
    init_config(config)

    # MongoDB 설정
    _mongo_client_instance = AsyncIOMotorClient(config.mongo.db_url())
    _mongo_db_instance = _mongo_client_instance.get_database(config.mongo.db_name())
    mongo_db = Object(_mongo_db_instance)

    question_container = Container(QuestionContainer, mongo_db=mongo_db)
