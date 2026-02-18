from .lifespan import app
from google.adk.agents.llm_agent import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from starlette.middleware.cors import CORSMiddleware

root_agent = Agent(
    model="gemini-3-flash-preview",
    name="root_agent",
    description="Tells the current time in a specified city.",
    instruction=app.service["recipe_prompt"].prompt.system_instructions[0].text,
)

# Convert the agent to an A2A-compatible Starlette app
a2a_app = to_a2a(root_agent, host="localhost", port=8888, protocol="http")

# Add CORS middleware to allow requests from the UI
a2a_app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)
