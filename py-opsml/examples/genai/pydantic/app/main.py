# pylint: disable=invalid-name
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from opsml.app import AppState
from opsml.scouter import GrpcConfig
from pydantic import BaseModel, Field

from .agent.helper import AgentHelper
from .db.commands import shutdown_db, startup_db
from opsml.scouter.tracing import get_tracer, init_tracer

init_tracer(
    service_name="agent-delivery-service",
    transport_config=GrpcConfig(),
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
    startup_db()

    tracer = get_tracer("agent-delivery-service")
    app_state = AppState.from_path(
        path=Path("app/service_artifacts"),
        transport_config=GrpcConfig(),
    )
    tracer.set_scouter_queue(app_state.queue)

    agent_helper = AgentHelper("agent-delivery-service", app_state, tracer)
    app.state.agent_helper = agent_helper
    app.state.app_state = app_state

    yield

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
