from pydantic_ai import Agent
from opsml.app import AppState
from .tools import build_tools
from typing import Tuple


def get_agents(app_state: AppState) -> Tuple[Agent, Agent]:
    """Creates agents for shipment and response handling."""

    tool = build_tools(app_state)

    shipment_agent = Agent(
        name="shipment_agent",
        model="openai:o4-mini",
        tools=[tool],
    )

    response_agent = Agent(
        name="response_agent",
        model="openai:o4-mini",
    )

    return shipment_agent, response_agent
