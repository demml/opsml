# pylint: disable=invalid-name
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from opsml.app import AppState
from opsml.logging import LoggingConfig, LogLevel, RustyLogger
from opsml.scouter import HTTPConfig
from pydantic import BaseModel, Field

from .agent.helper import AgentHelper
from .db.commands import shutdown_db, startup_db

logger = RustyLogger.get_logger(
    LoggingConfig(log_level=LogLevel.Info),
)


def get_session_id() -> str:
    """Generates a unique session ID."""
    return str(uuid.uuid4().hex)


def get_user_id() -> str:
    """Generates a unique user ID."""
    return "user-123"


class Answer(BaseModel):
    message: str


class Question(BaseModel):
    user_id: str = Field(
        default_factory=lambda: "user-123",
        description="Unique user identifier",
    )
    session_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique session identifier",
    )
    question: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up FastAPI app")

    startup_db()
    app_state = AppState.from_path(
        path=Path("app/service_artifacts"),
        transport_config=HTTPConfig(),
    )

    agent_helper = AgentHelper("opsml_app", app_state)
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
    response = await agent_helper.process_query(query=payload.question)

    return Answer(message=response)
