from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from opsml.app import AppState
from opsml.card import PromptCard
from opsml.logging import LoggingConfig, LogLevel, RustyLogger
from opsml.scouter import LLMRecord, Queue


from .agents import get_agents
from .utils import parse_response_events, parse_shipment_events

logger = RustyLogger.get_logger(
    LoggingConfig(log_level=LogLevel.Info),
)


class AgentHelper:
    """Helper class to manage agent-related operations."""

    def __init__(
        self,
        app_name: str,
        app_state: AppState,
    ):
        shipment_agent, response_agent = get_agents(app_state)

        self.session_service = InMemorySessionService()
        shipment_runner = Runner(
            app_name=app_name,
            agent=shipment_agent,
            session_service=self.session_service,
        )

        response_runner = Runner(
            app_name=app_name,
            agent=response_agent,
            session_service=self.session_service,
        )

        self.shipment_runner = shipment_runner
        self.response_runner = response_runner
        self.shipment_prompt: PromptCard = app_state.service["shipment"]
        self.response_prompt: PromptCard = app_state.service["response"]
        self.app_name = app_name
        self.eta_queue: Queue = app_state.queue["eta_metrics"]
        self.shipment_reply_queue: Queue = app_state.queue["shipment_reply_metrics"]
        self.shipment_metrics_queue: Queue = app_state.queue["shipment_metrics"]

    async def check_session_async(
        self,
        user_id: str,
        session_id: str,
    ) -> None:
        """Retrieves the session for the given app, user, and session ID."""
        session = await self.session_service.get_session(
            app_name=self.app_name,
            user_id=user_id,
            session_id=session_id,
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

    async def call_shipment_agent_async(self, query: str, user_id, session_id) -> str:
        """Sends a query to the shipment agent and returns the response."""

        parameterized_query = self.shipment_prompt.prompt.bind(user_query=query).message[0].unwrap()

        # Prepare the user's message in ADK format
        content = types.Content(role="user", parts=[types.Part(text=parameterized_query)])

        events = [
            event
            async for event in self.shipment_runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=content,
            )
        ]

        response = parse_shipment_events(events)
        response["user_query"] = parameterized_query

        # Insert into the metric queue for evaluation
        self.shipment_metrics_queue.insert(LLMRecord(context=response))

        return response.get("llm_response", "No response from agent")

    async def call_response_agent_async(self, shipment_eta_info: str, user_id, session_id) -> str:
        """Sends a query to the response agent and returns the response."""

        parameterized_query = self.response_prompt.prompt.bind(shipment_eta_info=shipment_eta_info).message[0].unwrap()

        # Prepare the user's message in ADK format
        content = types.Content(role="user", parts=[types.Part(text=parameterized_query)])

        events = [
            event
            async for event in self.response_runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=content,
            )
        ]

        response = parse_response_events(events)
        response["shipment_eta_info"] = shipment_eta_info

        # Insert into the reply queue for evaluation
        self.shipment_reply_queue.insert(LLMRecord(context=response))

        return response.get("llm_response", "No response from agent")

    async def process_query(self, query: str, user_id: str, session_id: str) -> str:
        """Processes the query and returns the agent's response."""
        await self.check_session_async(user_id=user_id, session_id=session_id)
        response = await self.call_shipment_agent_async(query, user_id, session_id)
        return await self.call_response_agent_async(response, user_id, session_id)
