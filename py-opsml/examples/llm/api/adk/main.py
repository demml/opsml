# pylint: disable=invalid-name
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from opsml.logging import RustyLogger, LogLevel, LoggingConfig
from .models import Answer, Question
from google.genai import types

logger = RustyLogger.get_logger(
    LoggingConfig(log_level=LogLevel.Debug),
)


def get_session_id() -> str:
    """Generates a unique session ID."""
    return "session-12345"  # Replace with actual session ID generation logic


def get_user_id() -> str:
    """Generates a unique user ID."""
    return "user-123"


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up FastAPI app")

    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="my_app",
        user_id=get_user_id(),
        session_id=get_session_id(),
    )

    app.state.session = session

    print(session_service.sessions)

    app.state.runner = Runner(
        app_name="my_app",
        agent=Agent(
            name="echo_agent",
            model="gemini-2.5-flash",
            description="Gemini agent",
            instruction="You are a helpful assistant.",
        ),
        session_service=session_service,
    )

    yield

    logger.info("Shutting down FastAPI app")


app = FastAPI(lifespan=lifespan)


async def call_agent_async(query: str, runner: Runner, user_id, session_id) -> str:
    """Sends a query to the agent and returns the response."""

    # Prepare the user's message in ADK format
    content = types.Content(role="user", parts=[types.Part(text=query)])

    # Execute the agent and find the final response
    async for event in runner.run_async(
        user_id=user_id, session_id=session_id, new_message=content
    ):
        if event.is_final_response():
            if event.content and event.content.parts:
                final_response_text = event.content.parts[0].text
            break

    if final_response_text is None:
        logger.error("No final response received from the agent.")
        final_response_text = "No response from the agent."

    return final_response_text


@app.post("/predict", response_model=Answer)
async def predict(request: Request, payload: Question) -> Answer:
    # Grab the reformulated prompt and response prompt from the app state
    runner: Runner = request.app.state.runner

    # Generate session and user IDs
    session_id = get_session_id()
    user_id = get_user_id()
    # Call the agent asynchronously
    response = await call_agent_async(
        query=payload.question,
        runner=runner,
        user_id=user_id,
        session_id=session_id,
    )

    return Answer(message=response)
