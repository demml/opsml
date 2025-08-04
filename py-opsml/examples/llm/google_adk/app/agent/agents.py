from google.adk.agents import LlmAgent
from opsml.app import AppState
from .tools import build_tools
from typing import Tuple


def get_agents(app_state: AppState) -> Tuple[LlmAgent, LlmAgent]:
    """Creates agents for shipment and response handling."""

    tool = build_tools(app_state)

    shipment_agent = LlmAgent(
        name="my_app",
        model="gemini-2.5-flash",
        description="Agent for extracting shipment IDs",
        tools=[tool],
    )

    response_agent = LlmAgent(
        name="my_app",
        model="gemini-2.5-flash",
        description="Agent for generating a response",
    )

    return shipment_agent, response_agent
