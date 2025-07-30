# pylint: disable=invalid-name
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from google.adk.agents import Agent
from opsml.logging import RustyLogger, LogLevel, LoggingConfig
from .models import Answer, Question

logger = RustyLogger.get_logger(
    LoggingConfig(log_level=LogLevel.Debug),
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up FastAPI app")

    app.state.agent = Agent(
        name="echo_agent",
        model="gemini-2.5-flash",  # Or use LiteLlm for multi-model
        description="Gemini agent",
        instruction="You are a helpful assistant.",
    )

    yield

    logger.info("Shutting down FastAPI app")


app = FastAPI(lifespan=lifespan)


@app.post("/predict", response_model=Answer)
async def predict(request: Request, payload: Question) -> Answer:
    # Grab the reformulated prompt and response prompt from the app state
    agent: Agent = request.app.state.agent
    return Answer(message=response)
