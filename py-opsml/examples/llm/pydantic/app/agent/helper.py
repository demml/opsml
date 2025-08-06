from .utils import parse_shipment_events, parse_response_events
from .agents import get_agents
from opsml.app import AppState
from opsml.card import PromptCard
from opsml.logging import RustyLogger, LogLevel, LoggingConfig
from opsml.scouter.queue import Queue, LLMRecord

logger = RustyLogger.get_logger(
    LoggingConfig(log_level=LogLevel.Info),
)


class AgentHelper:
    """Helper class to manage agent-related operations."""

    def __init__(
        self,
        app_name: str,
        app_state: AppState,
    ):
        shipment_agent, response_agent = get_agents(app_state)

        self.shipment_agent = shipment_agent
        self.response_agent = response_agent
        self.shipment_prompt: PromptCard = app_state.service["shipment"]
        self.response_prompt: PromptCard = app_state.service["response"]
        self.app_name = app_name
        self.eta_queue: Queue = app_state.queue["eta_metrics"]
        self.shipment_reply_queue: Queue = app_state.queue["shipment_reply_metrics"]
        self.shipment_metrics_queue: Queue = app_state.queue["shipment_metrics"]

    async def call_shipment_agent(self, query: str) -> str:
        """Sends a query to the shipment agent and returns the response."""

        parameterized_query = (
            self.shipment_prompt.prompt.bind(user_query=query).message[0].unwrap()
        )

        # Prepare the user's message
        agent_response = await self.shipment_agent.run(user_prompt=parameterized_query)
        response = parse_shipment_events(agent_response)

        # Insert into the metric queue for evaluation
        self.shipment_metrics_queue.insert(LLMRecord(context=response))

        return agent_response.output

    async def call_response_agent(self, shipment_eta_info: str) -> str:
        """Sends a query to the response agent and returns the response."""

        parameterized_query = (
            self.response_prompt.prompt.bind(shipment_eta_info=shipment_eta_info)
            .message[0]
            .unwrap()
        )

        agent_response = await self.response_agent.run(user_prompt=parameterized_query)

        response = parse_response_events(agent_response)
        response["shipment_eta_info"] = shipment_eta_info

        # Insert into the reply queue for evaluation
        self.shipment_reply_queue.insert(LLMRecord(context=response))

        return agent_response.output

    async def process_query(self, query: str) -> str:
        """Processes the query and returns the agent's response."""
        response = await self.call_shipment_agent(query)
        return await self.call_response_agent(response)
