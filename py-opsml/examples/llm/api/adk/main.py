# pylint: disable=invalid-name
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from opsml.logging import RustyLogger, LogLevel, LoggingConfig
from .models import Answer, Question
from .agent.sequential import root_agent
from .agent.utils import get_final_event
from google.genai import types
from google.adk.events.event import Event
import uuid
from google.adk.cli.fast_api import get_fast_api_app

logger = RustyLogger.get_logger(
    LoggingConfig(log_level=LogLevel.Debug),
)

# session = await session_service.get_session(
#        app_name=req.app_name, user_id=req.user_id, session_id=req.session_id
#    )
#    if not session:
#      raise HTTPException(status_code=404, detail="Session not found")
#    runner = await _get_runner_async(req.app_name)
#    events = [
#        event
#        async for event in runner.run_async(
#            user_id=req.user_id,
#            session_id=req.session_id,
#            new_message=req.new_message,
#        )
#    ]
#    logger.info("Generated %s events in agent run", len(events))
#    logger.debug("Events generated: %s", events)
#    return events
#


def get_session_id() -> str:
    """Generates a unique session ID."""
    return str(uuid.uuid4().hex)


def get_user_id() -> str:
    """Generates a unique user ID."""
    return "user-123"


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


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up FastAPI app")

    session_service = InMemorySessionService()
    runner = Runner(
        app_name="my_app",
        agent=root_agent,
        session_service=session_service,
    )

    agent_helper = AgentHelper(runner, session_service)
    app.state.agent_helper = agent_helper

    yield

    logger.info("Shutting down FastAPI app")


app = FastAPI(lifespan=lifespan)


@app.post("/predict", response_model=Answer)
async def predict(request: Request, payload: Question) -> Answer:
    # Grab the reformulated prompt and response prompt from the app state
    agent_helper: AgentHelper = request.app.state.agent_helper

    # Call the agent asynchronously
    response = await agent_helper.process_query(
        query=payload.question,
        user_id=payload.user_id,
        session_id=payload.session_id,
    )

    return Answer(message=response)
