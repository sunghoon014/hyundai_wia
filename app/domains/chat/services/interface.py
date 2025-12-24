"""Interface for chat agents that handle conversation flow with SSE messaging support."""

from abc import ABC, abstractmethod

from mcp import ClientSession

from app.common.messaging.message_queue import MessageQueue
from app.domains.chat.schemas.chat_request import ChatRequest
from app.domains.chat.schemas.message import Message


class IChatAgent(ABC):
    """Interface for chat agents that can handle conversations with streaming support.

    This interface defines the contract for agents that can:
    1. Process user requests through multiple iteration steps
    2. Send SSE messages during human interaction
    3. Stream final responses back to the user
    """

    @abstractmethod
    async def run(
        self,
        chat_request: ChatRequest,
        messages: list[Message],
        message_queue: MessageQueue,
        mcp_sessions: dict[str, ClientSession] | None = None,
    ) -> None:
        """Run the agent with the given chat context.

        The agent should iterate through steps (up to max_steps) to process the request,
        sending SSE messages via message_queue when:
        - Asking for human input/clarification
        - Generating the final response
        - Providing status updates during processing

        Args:
            chat_request: Chat request including the latest user request
            messages: Chat messages including the latest user request
            message_queue: Queue for sending SSE messages to the client

        Returns:
            Final response string from the agent

        Raises:
            Exception: If agent encounters an error during processing
        """
        pass
