from opsml.app import AppState
from opsml.card import PromptCard
from opsml.scouter import GenAIEvalRecord
from opsml.scouter.tracing import Tracer
from .agents import get_agents
from .utils import parse_response_events, parse_shipment_events


class AgentHelper:
    """Helper class to manage agent-related operations."""

    def __init__(
        self,
        app_name: str,
        app_state: AppState,
        tracer: Tracer,
    ):
        shipment_agent, response_agent = get_agents(tracer, app_state)

        self.shipment_agent = shipment_agent
        self.response_agent = response_agent
        self.shipment_prompt: PromptCard = app_state.service["shipment"]
        self.response_prompt: PromptCard = app_state.service["response"]
        self.app_name = app_name
        self.tracer = tracer

    async def call_shipment_agent(self, query: str) -> str:
        """Sends a query to the shipment agent and returns the response."""

        with self.tracer.start_as_current_span(name="call_shipment_agent") as span:
            parameterized_query = (
                self.shipment_prompt.prompt.bind(user_query=query)
                .messages[0]
                .content[0]
                .text
            )

            # Prepare the user's message
            agent_response = await self.shipment_agent.run(
                user_prompt=parameterized_query
            )
            response = parse_shipment_events(agent_response)

            span.add_queue_item(
                alias="shipment_metrics",
                item=GenAIEvalRecord(context=response),
            )

            return agent_response.output

    async def call_response_agent(self, shipment_eta_info: str) -> str:
        """Sends a query to the response agent and returns the response."""

        with self.tracer.start_as_current_span(name="call_response_agent") as span:
            parameterized_query = (
                self.response_prompt.prompt.bind(shipment_eta_info=shipment_eta_info)
                .messages[0]
                .content[0]
                .text
            )
            agent_response = await self.response_agent.run(
                user_prompt=parameterized_query
            )

            response = parse_response_events(agent_response)
            response["shipment_eta_info"] = shipment_eta_info

            # Insert into the reply queue for evaluation
            span.add_queue_item(
                alias="shipment_reply_metrics",
                item=GenAIEvalRecord(context=response),
            )

            return agent_response.output

    async def process_query(self, query: str) -> str:
        """Processes the query and returns the agent's response."""

        with self.tracer.start_as_current_span(name="process_query") as _span:
            response = await self.call_shipment_agent(query)
            return await self.call_response_agent(response)
