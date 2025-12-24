from pathlib import Path

from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Dependency, Factory, Singleton

from app.agents.adaptor.openai_adaptor import OpenAILLMAdapter
from app.agents.domains import AGENT_REGISTRY
from app.common.logger import logger
from app.common.messaging.message_dispatcher import MessageDispatcher
from app.config.utils import init_config
from app.domains.chat.handlers.indexer.milvus import MilvusIndexer
from app.domains.chat.repositories.mongo_chat_session_repository import (
    MongoChatSessionRepository,
)
from app.domains.chat.services.agent_adapter import AgentAdapter
from app.domains.chat.services.chat_service import ChatService
from app.domains.document.repositories.mongo_document_repository import (
    MongoDocumentRepository,
)


def _get_agent_setup_from_config(
    config: Configuration, llm_config: dict
) -> dict[str, str]:
    domain = config.agent.domain()
    model_name = llm_config.get("model")
    mode = llm_config.get("mode")

    # 1. 설정에서 모델 타입 찾기
    model_types_config = config.agent.model_types()
    model_type = None
    if model_name in model_types_config.get("frontier", []):
        model_type = "frontier"
    elif model_name in model_types_config.get("mini", []):
        model_type = "mini"

    if not model_type:
        raise ValueError(
            f"Model '{model_name}' not found in any model_types in config. "
            "Please define it in local.yaml."
        )

    # 2. 키 경로로 프롬프트 직접 조회
    domain_prompts = config.agent_prompts()[domain]
    if domain_prompts.get(model_type):  # Kearney
        model_prompts = domain_prompts[model_type][mode]
    elif domain_prompts.get(mode):  # AX
        model_prompts = domain_prompts[mode]
    else:
        raise ValueError(
            f"Prompts for domain='{domain}', (optional) model_type='{model_type}', mode='{mode}' not found in prompts.yaml."
        )

    prompt_dict = {
        "system_prompt": model_prompts.get("system_prompt"),
        "next_step_prompt": model_prompts.get("next_step_prompt"),
    }
    prompt_dict["tool_prompts"] = domain_prompts["tools"]
    logger.info(f"Successfully loaded {domain} prompts:\n{prompt_dict}")

    # 3. 도구 설정
    tool_list_config = config.agent.domain_tools()[domain]
    if tool_list_config.get(model_type):
        tool_list = tool_list_config[model_type][mode]
    elif tool_list_config.get(mode):
        tool_list = tool_list_config[mode]
    else:
        raise ValueError(
            f"Tools for domain='{domain}', (optional) model_type='{model_type}', mode='{mode}' not found in local.yaml."
        )
    logger.info(f"Successfully loaded {domain} tools:\n{tool_list}")
    return {
        "model_type": model_type,
        "prompt_dict": prompt_dict,
        "tool_list": tool_list,
    }


class ChatContainer(DeclarativeContainer):
    root: Path = Path(__file__).parents[2]

    # --- 기본 설정 ---
    config = Configuration()
    init_config(config)
    mongo_db = Dependency()
    message_dispatcher = Singleton(MessageDispatcher)

    # --- 리포지토리 및 인덱서 ---
    mongo_chat_session_repository = Singleton(
        MongoChatSessionRepository,
        db=mongo_db,
    )
    mongo_document_repository = Singleton(MongoDocumentRepository, db=mongo_db)
    milvus_indexer = Singleton(
        MilvusIndexer,
        connection_alias=config.milvus.indexing.connection_alias(),
        embedding_model=config.milvus.indexing.embedding_model(),
        dense_vector_dim=config.milvus.indexing.dense_vector_dim(),
        enable_nltk=config.milvus.indexing.enable_nltk(),
    )

    # --- LLM 어댑터 설정 ---
    llm_config = config.agent.domain_configs()[config.agent.domain()]
    # API 통신과 토큰 수 관리를 하기 때문에 Factory로 설정
    llm_adapter = Factory(
        OpenAILLMAdapter,
        model=llm_config.get("model"),
        provider=llm_config.get("provider"),
        api_key=config.openrouter.api_key()
        if llm_config.get("provider") == "openrouter"
        else config.openai.api_key(),
        params=llm_config.get("params"),
        **llm_config.get("config"),
    )

    # --- 에이전트 설정 ---
    agent_cls = AGENT_REGISTRY[config.agent.domain()]
    agent = Factory(
        agent_cls.create,
        llm=llm_adapter,
        agent_setup=_get_agent_setup_from_config(config, llm_config),
        max_steps=config.agent.max_steps(),
    )

    # --- 채팅 서비스 정의 ---
    chat_adapter = Factory(AgentAdapter, agent=agent)

    chat_service = Factory(
        ChatService,
        chat_agent=chat_adapter,
        chat_session_repository=mongo_chat_session_repository,
        milvus_indexer=milvus_indexer,
        document_repository=mongo_document_repository,
    )
