# pylint: disable=invalid-name
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from opsml.logging import RustyLogger, LogLevel, LoggingConfig
from opsml.app import AppState
from .models import Answer, Question
from .agent.sequential import create_sequential_agent
from .agent.helper import AgentHelper
from .db.commands import startup_db, shutdown_db
import uuid
from opsml.card import PromptCard

logger = RustyLogger.get_logger(
    LoggingConfig(log_level=LogLevel.Debug),
)


def get_session_id() -> str:
    """Generates a unique session ID."""
    return str(uuid.uuid4().hex)


def get_user_id() -> str:
    """Generates a unique user ID."""
    return "user-123"


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up FastAPI app")

    startup_db()
    app_state = AppState.from_path(
        path=Path("app/service_artifacts"),
    )

    session_service = InMemorySessionService()
    runner = Runner(
        app_name="my_app",
        agent=create_sequential_agent(app_state),
        session_service=session_service,
    )

    agent_helper = AgentHelper(runner, session_service)
    app.state.agent_helper = agent_helper
    app.state.app_state = app_state

    yield

    logger.info("Shutting down FastAPI app")
    shutdown_db()
    app.state.app_state = None
    app.state.agent_helper = None


app = FastAPI(lifespan=lifespan)


@app.post("/predict", response_model=Answer)
async def predict(request: Request, payload: Question) -> Answer:
    # Grab the reformulated prompt and response prompt from the app state
    agent_helper: AgentHelper = request.app.state.agent_helper

    # Prefer to user before_model_callback, but context mutatbility doesn't seem to work for google adk
    service_prompt: PromptCard = app.state.app_state.service["shipment"]

    # Call the agent asynchronously
    response = await agent_helper.process_query(
        query=service_prompt.prompt.bind(
            user_query=payload.question,
        )
        .user_message[0]
        .unwrap(),
        user_id=payload.user_id,
        session_id=payload.session_id,
    )

    return Answer(message=response)
