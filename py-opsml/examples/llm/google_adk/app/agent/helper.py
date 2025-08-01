from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from .utils import get_final_event
from google.genai import types
from opsml.logging import RustyLogger, LogLevel, LoggingConfig

logger = RustyLogger.get_logger(
    LoggingConfig(log_level=LogLevel.Debug),
)


class AgentHelper:
    """Helper class to manage agent-related operations."""

    def __init__(self, runner: Runner, session_service: InMemorySessionService):
        self.app_name = runner.app_name
        self.runner = runner
        self.session_service = session_service

    async def check_session_async(
        self,
        user_id: str,
        session_id: str,
    ) -> None:
        """Retrieves the session for the given app, user, and session ID."""
        session = await self.session_service.get_session(
            app_name=self.app_name, user_id=user_id, session_id=session_id
        )
        if not session:
            # create a new session if it doesn't exist
            logger.info(
                "Session not found for user {} with session ID {}. Creating a new session.",
                user_id,
                session_id,
            )
            session = await self.session_service.create_session(
                app_name=self.app_name,
                user_id=user_id,
                session_id=session_id,
            )

    async def call_agent_async(self, query: str, user_id, session_id) -> str:
        """Sends a query to the agent and returns the response."""

        # Prepare the user's message in ADK format
        content = types.Content(role="user", parts=[types.Part(text=query)])

        events = [
            event
            async for event in self.runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=content,
            )
        ]

        return get_final_event(events) or "No response generated."

    async def process_query(self, query: str, user_id: str, session_id: str) -> str:
        """Processes the query and returns the agent's response."""
        await self.check_session_async(user_id=user_id, session_id=session_id)
        return await self.call_agent_async(query, user_id, session_id)
