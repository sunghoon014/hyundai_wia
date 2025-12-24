import os
from enum import Enum

import click
import uvicorn
from dotenv import load_dotenv

from app.common.logger import logger


class Environment(str, Enum):
    LOCAL = "local"
    DEV = "dev"
    PROD = "prod"


@click.command()
@click.option("-p", "--port", type=str, help="Port number")
@click.option("--ssl-keyfile", type=str, help="SSL keyfile")
@click.option("--ssl-certfile", type=str, help="SSL certfile")
def main(
    port: str | None = None,
    ssl_keyfile: str | None = None,
    ssl_certfile: str | None = None,
):
    # load ENV, LOG_LEVEL
    load_dotenv()
    if (os.getenv("ENV")) is None:
        raise ValueError("ENV is not set")
    if (os.getenv("LOG_LEVEL")) is None:
        raise ValueError("LOG_LEVEL is not set")

    # set ssl related settings
    ssl_enabled = ssl_keyfile and ssl_certfile
    if ssl_enabled:
        logger.info("SSL is enabled")
    elif not ssl_keyfile and not ssl_certfile:
        logger.info("SSL is disabled")
    else:
        raise ValueError("Invalid SSL configuration")

    # set port
    if port is None:
        logger.warning("PORT is not set. Force to set 8000.")
        port = int("8000")
    else:
        port = int(port)

    uvicorn.run(
        app="app.domains.server:app",
        host="0.0.0.0",
        port=port,
        factory=False,
        # NOTE: FastAPI 애플리케이션 생성 시점에 MCP 서버들도 서브 프로세스로 실행되기 때문에 자동 reload 설정 시 좀비 프로세스가 생성될 우려가 있습니다.
        reload=False,
        ssl_keyfile=ssl_keyfile,
        ssl_certfile=ssl_certfile,
    )


if __name__ == "__main__":
    main()
