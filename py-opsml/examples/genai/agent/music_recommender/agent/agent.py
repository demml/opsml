"""
Music Recommendation: Prompt Chaining with SequentialAgent

This demonstrates the Prompt Chaining pattern using Google ADK's SequentialAgent.
Each sub-agent performs one step and passes results via shared state using output_key.

Pipeline:
1. Preference Analyzer → Extracts user taste
2. Pattern Recognizer → Identifies listening themes
3. Search Specialist → Finds candidate tracks
4. Recommendation Generator → Produces final recommendations
"""

from starlette.responses import JSONResponse
from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from starlette.middleware.cors import CORSMiddleware
from .lifespan import app
from agent.sub_agents import (
    preference_analyzer,
    pattern_recognizer,
    search_specialist,
    recommendation_generator,
)


agent_card = app.service.agent_card()


root_agent = SequentialAgent(
    name=agent_card.skills[0].id,
    sub_agents=[
        preference_analyzer,
        pattern_recognizer,
        search_specialist,
        recommendation_generator,
    ],
    description="Chain-of-Thought music recommender using sequential agent pipeline.",
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
    return JSONResponse(
        {"status": "healthy", "service": "music-recommender-agent", "version": "1.0.0"}
    )
