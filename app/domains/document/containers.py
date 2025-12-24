from pathlib import Path

from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Dependency, Factory, Singleton

from app.common.llm_clients.langchain_clients import (
    LangchainClient,
    MultiModalLangchainClient,
)
from app.config.utils import init_config
from app.domains.document.handlers.langchain.adapter import LangchainAdapter
from app.domains.document.handlers.langchain.chain import (
    get_extract_document_summary_runnable,
    get_extract_image_summary_runnable,
    get_extract_page_summary_runnable,
    get_extract_table_summary_runnable,
)
from app.domains.document.handlers.node.llm import (
    ImageSummaryNode,
    PageSummaryNode,
    TableSummaryNode,
)
from app.domains.document.handlers.node.loader import SplitPDFFilesNode
from app.domains.document.handlers.node.parser import PostParseNode, UpstageParseNode
from app.domains.document.handlers.node.preprocessing import LangchainDocumentNode
from app.domains.document.handlers.node.utils import WorkingQueueNode
from app.domains.document.repositories.mongo_document_repository import (
    MongoDocumentRepository,
)
from app.domains.document.services.document_service import DocumentService
from app.domains.document.services.parsing_service import ParsingService


class DocumentContainer(DeclarativeContainer):
    root: Path = Path(__file__).parents[2]

    # --- 기본 설정 ---
    config = Configuration()
    init_config(config)
    mongo_db = Dependency()

    # --- 리포지토리 ---
    mongo_document_repository = Singleton(MongoDocumentRepository, db=mongo_db)

    # --- 각 노드별 LLM 클라이언트 및 어댑터 설정 ---
    # 1. 페이지 요약 (Page Summary) & 2. 문서 전체 요약 (Document Summary)
    page_summary_config = config.document.page_summary_node()
    page_summary_llm_client = Singleton(
        LangchainClient,
        model=page_summary_config.get("model"),
        provider=page_summary_config.get("provider"),
        api_key=config.openrouter.api_key()
        if page_summary_config.get("provider") == "openrouter"
        else config.openai.api_key(),
        params=page_summary_config.get("params"),
    )
    page_summary_adapter = Singleton(
        LangchainAdapter, llm_client=page_summary_llm_client
    )
    extract_page_summary_chain = Singleton(
        get_extract_page_summary_runnable, adapter=page_summary_adapter
    )
    extract_document_summary_chain = Singleton(
        get_extract_document_summary_runnable, adapter=page_summary_adapter
    )

    # 3. 이미지 요약 (Image Summary) - 멀티모달
    image_summary_config = config.document.image_summary_node()
    image_summary_llm_client = Singleton(
        MultiModalLangchainClient,
        model=image_summary_config.get("model"),
        provider=image_summary_config.get("provider"),
        api_key=config.openrouter.api_key()
        if image_summary_config.get("provider") == "openrouter"
        else config.openai.api_key(),
        params=image_summary_config.get("params"),
    )
    image_summary_adapter = Singleton(
        LangchainAdapter, multi_modal_client=image_summary_llm_client
    )
    extract_image_summary_chain = Singleton(
        get_extract_image_summary_runnable, adapter=image_summary_adapter
    )

    # 4. 테이블 요약 (Table Summary) - 멀티모달
    table_summary_config = config.document.table_summary_node()
    table_summary_llm_client = Singleton(
        MultiModalLangchainClient,
        model=table_summary_config.get("model"),
        provider=table_summary_config.get("provider"),
        api_key=config.openrouter.api_key()
        if table_summary_config.get("provider") == "openrouter"
        else config.openai.api_key(),
        params=table_summary_config.get("params"),
    )
    table_summary_adapter = Singleton(
        LangchainAdapter, multi_modal_client=table_summary_llm_client
    )
    extract_table_summary_chain = Singleton(
        get_extract_table_summary_runnable, adapter=table_summary_adapter
    )

    # --- 파싱 파이프라인 노드 정의 ---
    split_pdf_files_node = Singleton(
        SplitPDFFilesNode,
        batch_size=config.document.split_pdf_files_node.batch_size(),
        save_dir=config.document.split_pdf_files_node.save_dir(),
        test_page=config.document.split_pdf_files_node.test_page(),
    )
    upstage_parse_node = Singleton(
        UpstageParseNode,
        api_key=config.upstage.api_key(),
        is_save=config.document.upstage_parse_node.is_save(),
    )
    post_parse_node = Singleton(PostParseNode)
    working_queue_node = Singleton(WorkingQueueNode)

    page_summary_node = Singleton(
        PageSummaryNode,
        page_summary_chain=extract_page_summary_chain,
        document_summary_chain=extract_document_summary_chain,
        page_summary_system_prompt=config.document_prompts.page_summary_node.system_prompt(),
        document_summary_system_prompt=config.document_prompts.page_summary_node.system_prompt_2(),
    )
    image_summary_node = Singleton(
        ImageSummaryNode,
        chain=extract_image_summary_chain,
        system_prompt=config.document_prompts.image_summary_node.system_prompt(),
    )
    table_summary_node = Singleton(
        TableSummaryNode,
        chain=extract_table_summary_chain,
        system_prompt=config.document_prompts.table_summary_node.system_prompt(),
    )
    langchain_document_node = Singleton(
        LangchainDocumentNode,
        chunk_size=config.document.langchain_document_node.chunk_size(),
        chunk_overlap=config.document.langchain_document_node.chunk_overlap(),
        strategy=config.document.langchain_document_node.strategy(),
        embedding_model=config.document.langchain_document_node.embedding_model(),
    )

    # --- 서비스 정의 ---
    parsing_service = Factory(
        ParsingService,
        split_pdf_files_node=split_pdf_files_node,
        upstage_parse_node=upstage_parse_node,
        post_parse_node=post_parse_node,
        working_queue_node=working_queue_node,
        page_summary_node=page_summary_node,
        image_summary_node=image_summary_node,
        table_summary_node=table_summary_node,
        langchain_document_node=langchain_document_node,
        langchain_adapter=page_summary_adapter,
    )
    document_service = Factory(
        DocumentService,
        parsing_service=parsing_service,
        document_repository=mongo_document_repository,
    )
