"""
Agent with A2A support and custom healthcheck endpoints.

This module demonstrates how to:
1. Convert an ADK agent to A2A format
2. Add custom healthcheck endpoints for production deployments
3. Properly expose agent capabilities via agent card
"""

from starlette.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from .lifespan import app
from google.adk.agents.llm_agent import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a

# Define the core agent
root_agent = Agent(
    model="gemini-3-flash-lite",
    name="vegetarian_recipe_agent",
    description="A vegetarian recipe agent service that generates recipes and suggests substitutions.",
    instruction=app.service["recipe_prompt"].prompt.system_instructions[0].text,
)

# Convert to A2A-compatible Starlette app
a2a_app = to_a2a(root_agent, host="localhost", port=8080, protocol="http")

# Add CORS middleware to allow requests from the UI
a2a_app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your UI origin
    allow_methods=["*"],  # Allow all HTTP methods (including OPTIONS)
    allow_headers=["*"],  # Allow all headers
    allow_credentials=True,
)


# Add custom healthcheck endpoints for production deployment
@a2a_app.route("/health", methods=["GET"])
async def health_check(request):
    """Basic health check endpoint for load balancers."""
    return JSONResponse({"status": "healthy", "service": "vegetarian-recipe-agent", "version": "1.0.0"})
