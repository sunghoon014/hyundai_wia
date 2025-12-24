"""Chat agent adapter for Kearney agent to implement IChatAgent interface."""

import re

from mcp import ClientSession

from app.agents.context.schema import Role as AgentRole
from app.agents.interface import IAgent
from app.agents.tools.mcp_client import MCPClientTool
from app.common.logger import logger
from app.common.messaging.message_queue import MessageQueue
from app.domains.chat.schemas.chat_request import ChatRequest
from app.domains.chat.schemas.message import Message, Role
from app.domains.chat.services.interface import IChatAgent


class AgentAdapter(IChatAgent):
    """Adapter that wraps agent to implement IChatAgent interface.

    This adapter handles:
    1. Converting chat messages to agent's internal format
    2. Sending SSE messages during processing
    3. Managing the agent's execution flow
    """

    def __init__(
        self,
        agent: IAgent,
    ):
        """Initialize the adapter with a agent instance.

        Args:
            agent: The agent instance to wrap
        """
        self._agent = agent

    async def run(
        self,
        chat_request: ChatRequest,
        messages: list[Message],
        message_queue: MessageQueue,
        mcp_sessions: dict[str, ClientSession] | None = None,
    ) -> None:
        """Run the agent with SSE messaging support."""
        if mcp_sessions and chat_request.tool_server_ids:
            selected_tools = await self._setup_mcp_tools(
                mcp_sessions, chat_request.tool_server_ids
            )
            self._agent.available_tools.add_tools(*selected_tools)
            logger.info(
                f"Dynamically added tools for session {chat_request.session_id}"
            )
            for (
                tool_name,
                tool_instance,
            ) in self._agent.available_tools.tool_map.items():
                logger.debug(f"[Tool: {tool_name}] {tool_instance}")

        self._setup_chat_context(chat_request, messages)
        await self._agent.run_with_sse(message_queue)

    def _setup_chat_context(
        self, chat_request: ChatRequest, messages: list[Message]
    ) -> str:
        """Setup chat context in agent's memory.

        Args:
            chat_request: Chat request including the latest user request
            messages: Previous chat messages to add to context
        """
        # 이전 메시지를 에이전트의 단기 메모리에 추가합니다.
        for msg in messages:
            agent_role: AgentRole | None = None
            if msg.role == Role.USER:
                agent_role = AgentRole.USER
            elif msg.role == Role.ASSISTANT_FINISHED:
                agent_role = AgentRole.ASSISTANT

            if agent_role and msg.content:
                self._agent.update_memory(agent_role, msg.content)

    async def _setup_mcp_tools(
        self, mcp_sessions: dict[str, ClientSession], tool_server_ids: list[str]
    ) -> list[MCPClientTool]:
        """Setup MCP tools for the agent."""
        selected_tools = []
        for server_id, session in mcp_sessions.items():
            if server_id in tool_server_ids:
                try:
                    response = await session.list_tools()
                    for tool in response.tools:
                        original_name = tool.name
                        tool_name = f"mcp_{server_id}_{original_name}"
                        tool_name = self._sanitize_tool_name(tool_name)

                        server_tool = MCPClientTool(
                            name=tool_name,
                            description=tool.description,
                            parameters=tool.inputSchema,
                            session=session,
                            server_id=server_id,
                            original_name=original_name,
                        )
                        selected_tools.append(server_tool)
                except Exception as e:
                    logger.error(
                        f"Failed to list or create tools for MCP server {server_id}: {e}"
                    )
        return selected_tools

    def _sanitize_tool_name(self, name: str) -> str:
        """Sanitize tool name to match MCPClientTool requirements."""
        sanitized = re.sub(r"[^a-zA-Z0-9_-]", "_", name)
        sanitized = re.sub(r"_+", "_", sanitized)
        sanitized = sanitized.strip("_")
        if len(sanitized) > 64:
            sanitized = sanitized[:64]
        return sanitized
