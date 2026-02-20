"""
Agent with A2A support and custom healthcheck endpoints.

This module demonstrates how to:
1. Convert an ADK agent to A2A format
2. Add custom healthcheck endpoints for production deployments
3. Extract messageId from client requests for tracking/logging
"""

from starlette.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from .lifespan import app
from typing import Optional
from google.adk.agents.llm_agent import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse, LlmRequest
from google.genai import types


def my_before_agent_callback(
    callback_context: CallbackContext,
) -> Optional[types.Content]:
    """Extract messageId from user context and store in state."""
    # The A2A message context is NOT directly exposed in ADK callbacks by default
    # But we can try to extract it from the invocation context if available

    # For now, log what we have
    print(f"=== Before Agent Callback ===")
    print(f"User content: {callback_context.user_content}")

    # Check if user_content has any metadata we can extract
    if callback_context.user_content:
        # The context field from A2A message should be somewhere here
        # It might be in parts or metadata
        print(
            f"User content parts: {callback_context.user_content.parts if callback_context.user_content.parts else 'None'}"
        )

    return None  # Allow agent to proceed


def my_before_model_logic(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """Access messageId from the LlmRequest contents."""

    print(callback_context._invocation_context.model_dump_json())

    return None  # Allow the model call to proceed


# Define the core agent with both callbacks
root_agent = Agent(
    model=app.service["recipe_prompt"].prompt.model,
    name="vegetarian_recipe_agent",
    description="A vegetarian recipe agent service that generates recipes and suggests substitutions.",
    instruction=app.service["recipe_prompt"].prompt.system_instructions[0].text,
    before_agent_callback=my_before_agent_callback,
    before_model_callback=my_before_model_logic,
)

# Convert to A2A-compatible Starlette app
a2a_app = to_a2a(root_agent, host="localhost", port=8080, protocol="http")

# Add CORS middleware to allow requests from the UI
a2a_app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Your UI origins
    allow_methods=["*"],
    allow_headers=["*"],  # This allows X-Message-ID and X-Request-ID headers
    allow_credentials=True,
)


# Custom middleware to extract headers and log them
@a2a_app.middleware("http")
async def log_request_headers(request, call_next):
    """Log incoming headers for debugging."""
    if request.method == "POST":
        message_id = request.headers.get("x-message-id")
        request_id = request.headers.get("x-request-id")

        if message_id or request_id:
            print(f"\n=== Incoming Request ===")
            print(f"Headers - Message-ID: {message_id}, Request-ID: {request_id}")
            print(f"Path: {request.url.path}")

    response = await call_next(request)
    return response


# Add custom healthcheck endpoints for production deployment
@a2a_app.route("/health", methods=["GET"])
async def health_check(request):
    """Basic health check endpoint for load balancers."""
    return JSONResponse(
        {"status": "healthy", "service": "vegetarian-recipe-agent", "version": "1.0.0"}
    )
