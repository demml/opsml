from .lifespan import app
from google.adk.agents.llm_agent import Agent

root_agent = Agent(
    model="gemini-3-flash-preview",
    name="root_agent",
    description="Tells the current time in a specified city.",
    instruction=app.service["recipe_prompt"].prompt.system_instructions[0].text,
)
