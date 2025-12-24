import json
from contextlib import AsyncExitStack
from pathlib import Path
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from app.common.logger import logger


class MCPManager:
    """Manages the lifecycle of MCP server subprocesses and their client sessions."""

    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.sessions: dict[str, ClientSession] = {}
        self._exit_stack = AsyncExitStack()

    async def startup(self):
        """Starts all enabled MCP servers as subprocesses and establishes sessions."""
        logger.info("Starting up MCP servers...")
        config = self._load_config()
        for server_id, server_config in config.get("mcpServers", {}).items():
            try:
                params = StdioServerParameters(
                    command=server_config["command"],
                    args=server_config["args"],
                    env=server_config.get("env"),
                )

                # Start the server process and get read/write streams
                read, write = await self._exit_stack.enter_async_context(
                    stdio_client(params)
                )

                # Establish a client session
                session = await self._exit_stack.enter_async_context(
                    ClientSession(read, write)
                )
                await session.initialize()
                self.sessions[server_id] = session
                logger.info(
                    f"Successfully started and connected to MCP server: {server_id}"
                )

            except Exception as e:
                logger.error(f"Failed to start MCP server {server_id}: {e}")

    async def shutdown(self):
        """Shuts down all MCP servers and closes sessions."""
        logger.info("Shutting down MCP servers...")
        await self._exit_stack.aclose()
        self.sessions.clear()
        logger.info("All MCP servers have been shut down.")

    def get_sessions(self) -> dict[str, ClientSession]:
        """Returns the currently active MCP sessions."""
        return self.sessions

    def _load_config(self) -> dict[str, Any]:
        """Loads the MCP server configuration from a JSON file."""
        if not self.config_path.exists():
            logger.warning(f"MCP config file not found at {self.config_path}")
            return {}
        try:
            with open(self.config_path, encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse MCP config file {self.config_path}: {e}")
            return {}
        except Exception as e:
            logger.error(f"Failed to read MCP config file {self.config_path}: {e}")
            return {}
