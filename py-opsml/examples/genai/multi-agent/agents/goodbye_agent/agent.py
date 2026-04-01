from google.adk import Agent
from google.adk.agents import LlmAgent

from .lifespan import get_app_state
from .tools import get_current_time


def create_agent() -> Agent:
    _, prompts, agent_spec = get_app_state()

    return LlmAgent(
        name=agent_spec.skills[0].id,
        model=prompts.goodbye.prompt.model,
        instruction=prompts.goodbye.prompt.messages[0].text,
        tools=[get_current_time],
    )


root_agent = create_agent()
