"""
Recipe Generator: Orchestrator + Sequential Response Pattern

Pipeline:
1. Recipe Orchestrator (LlmAgent) → Routes to the appropriate recipe sub-agent and stores result
2. Response Agent (LlmAgent) → Reads the recipe result and returns a polished response to the user
"""

from agent.sub_agents import (
    dessert_recipe_agent,
    meat_recipe_agent,
    vegan_recipe_agent,
)
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.agents import LlmAgent, SequentialAgent
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from .lifespan import app, prompts

agent_card = app.service.agent_card()

recipe_orchestrator = LlmAgent(
    model=prompts.recipe.prompt.model,
    name=agent_card.skills[0].id,
    sub_agents=[
        meat_recipe_agent,
        vegan_recipe_agent,
        dessert_recipe_agent,
    ],
    description="Recipe generator agent that creates meal and dessert recipes based on user preferences and dietary restrictions.",
    instruction=prompts.recipe.prompt.messages[0].text,
)

response_agent = LlmAgent(
    name="RecipeResponseAgent",
    model=prompts.response.prompt.model,
    instruction=prompts.response.prompt.messages[0].text,
)

root_agent = SequentialAgent(
    name="RecipePipeline",
    sub_agents=[recipe_orchestrator, response_agent],
)

# Convert to A2A-compatible Starlette app
a2a_app = to_a2a(
    root_agent,
    host="localhost",
    port=8888,
    protocol="http",
)


# Add CORS middleware to allow requests from the UI
a2a_app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


@a2a_app.route("/health", methods=["GET"])
async def health_check(request):
    """Basic health check endpoint for load balancers."""
    return JSONResponse({"status": "healthy", "service": "music-recommender-agent", "version": "1.0.0"})
