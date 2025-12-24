import asyncio
import os
from contextlib import AsyncExitStack, asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware

from app.agents.mcp.mcp_manager import MCPManager

# from pymilvus import connections
from app.common.logger import logger
from app.domains import API_VERSION
from app.domains.containers import BaseContainer
from app.domains.index.apis import index_router
from app.domains.routers import app_router

# NOTE: MCP 서버와의 세션을 애플리케이션 주기로 생성
exit_stack: AsyncExitStack = AsyncExitStack()
cleanup_lock: asyncio.Lock = asyncio.Lock()


async def cleanup_mcp_sessions(app: FastAPI) -> None:
    """MCP 클라이언트 정리."""
    async with cleanup_lock:
        await exit_stack.aclose()

        for key, session in app.state.mcp_sessions.items():
            await session.aclose()
            logger.info(f"MCP Session for the server {key} is cleaned up")
        app.state.mcp_sessions.clear()


# # NOTE: alias는 "default"로 통일. 나중에 설정값으로 추가 필요
# async def init_milvus_connection(app: FastAPI) -> None:
#     """Milvus 연결 초기화."""
#     load_dotenv()
#     try:
#         alias = "default"
#         if not connections.has_connection(alias):
#             connections.connect(alias, address="127.0.0.1:19530")
#             logger.info("Milvus connection initialized at 127.0.0.1:19530")

#         app.state.milvus_connection_alias = alias
#     except Exception as e:
#         logger.error(f"Failed to initialize Milvus connection: {e}")
#         raise


# async def cleanup_milvus_connection(app: FastAPI) -> None:
#     """Milvus 연결 정리."""
#     try:
#         if hasattr(app.state, "milvus_connection_alias"):
#             alias = app.state.milvus_connection_alias
#             if connections.has_connection(alias):
#                 connections.disconnect(alias)
#                 logger.info(f"Milvus connection '{alias}' disconnected")
#     except Exception as e:
#         logger.warning(f"Error during Milvus cleanup: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI 앱의 생명주기 동안 MCP 서버를 관리합니다."""
    # Startup: 앱 시작 시 MCP 서버들을 실행합니다.
    # config 파일 경로를 올바르게 지정합니다.
    mcp_config_path = Path(__file__).parent.parent / "agents" / "mcp" / "mcp.json"
    mcp_manager = MCPManager(config_path=mcp_config_path)
    await mcp_manager.startup()
    # 생성된 세션을 앱 상태에 저장하여 다른 곳에서 참조할 수 있도록 합니다.
    app.state.mcp_sessions = mcp_manager.get_sessions()

    yield

    # Shutdown: 앱 종료 시 MCP 서버들을 정리합니다.
    await mcp_manager.shutdown()


def make_middleware() -> list[Middleware]:
    """FastAPI 미들웨어 리스트를 생성합니다.

    Returns:
        list[Middleware]: CORS 미들웨어가 포함된 미들웨어 리스트
    """
    middlewares = [
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        ),
    ]
    return middlewares


def init_routers(app: FastAPI) -> None:
    """FastAPI 앱에 라우터를 등록합니다.

    Args:
        app (FastAPI): FastAPI 애플리케이션 인스턴스
    """
    app.include_router(app_router)
    app.include_router(index_router)


def init_app_home() -> None:
    """프로젝트 경로 설정."""
    os.environ["APP_HOME"] = os.path.abspath(Path(__file__).parents[1])


def init_container(app: FastAPI) -> None:
    base_container = BaseContainer()
    app.state.base_container = base_container


def create_app() -> FastAPI:
    """FastAPI 앱을 생성하고 구성합니다.

    - `BaseContainer`를 초기화하고 앱에 연결합니다.
    - API 라우터를 포함시킵니다.
    """
    app = FastAPI(
        title="AX Consulting APIs",
        version=API_VERSION,
        contact={"name": "AX, Coxwave"},
        docs_url="/docs",
        redoc_url="/redoc",
        debug=True,
        middleware=make_middleware(),
        lifespan=lifespan,
    )

    init_app_home()
    init_routers(app=app)
    init_container(app=app)

    return app


app = create_app()
