from google.adk import Agent
from google.adk.agents import LlmAgent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent

from .config import config
from .lifespan import get_app_state


def create_agent() -> Agent:
    _, prompts, agent_spec = get_app_state()

    hello_remote = RemoteA2aAgent(
        name="hello_agent",
        description="Greets users warmly by name. Use this agent when the user wants to say hello, be welcomed, or needs a friendly greeting.",
        agent_card=f"{config.hello_agent_url.unicode_string().rstrip('/')}/.well-known/agent.json",
    )

    goodbye_remote = RemoteA2aAgent(
        name="goodbye_agent",
        description="Bids farewell to users by name. Use this agent when the user wants to say goodbye, end a conversation, or needs a parting message.",
        agent_card=f"{config.goodbye_agent_url.unicode_string().rstrip('/')}/.well-known/agent.json",
    )

    return LlmAgent(
        name=agent_spec.skills[0].id,
        model=prompts.greeting.prompt.model,
        instruction=prompts.greeting.prompt.messages[0].text,
        description=agent_spec.description,
        sub_agents=[hello_remote, goodbye_remote],
    )


root_agent = create_agent()
