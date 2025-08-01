from google.adk.agents import LlmAgent, SequentialAgent
from .callback import modify_output_after_agent
from opsml.app import AppState
from .tools import build_tools
from typing import Optional
from pydantic import BaseModel


class ShipmentID(BaseModel):
    id: Optional[int] = None


def create_sequential_agent(app_state: AppState) -> SequentialAgent:
    """Creates a sequential agent with the assistant agent."""

    tool = build_tools(app_state)

    shipment_agent = LlmAgent(
        name="my_app",
        model="gemini-2.5-flash",
        description="Agent for extracting shipment IDs",
        after_agent_callback=modify_output_after_agent,
        tools=[tool],
    )

    code_pipeline_agent = SequentialAgent(
        name="CodePipelineAgent",
        sub_agents=[shipment_agent],
        description="Executes a sequence of getting user input",
    )

    return code_pipeline_agent
