from opsml.llm import Prompt
from opsml.card import PromptCard
from opsml.scouter.drift import LLMDriftConfig
from opsml.scouter.alert import LLMAlertConfig
from opsml.scouter.types import CommonCrons
from .prompt_metrics import shipment_eta_task_evaluation

# take user input and reformulate it into a question for the LLM
get_shipment_eta = """
You are an expert assistant for supply chain operations.

Your task is to:
1. Extract the shipment ID (an integer) from the user's query.
2. Call the tool `get_shipment_eta_by_id(shipment_id: int)` to retrieve the estimated delivery time, destination, and shipment status for that shipment.
3. Return the result in a structured format.

Tool usage:
- Use `get_shipment_eta_by_id` with the extracted shipment ID to get the ETA and details.

Example Query: "What is the estimated delivery time for shipment ID 12345?"
Example Tool Call: get_shipment_eta_by_id(12345)
Example Tool Result: {"eta": "0.5 hours", "shipment_id": 12345, "destination": "Philadelphia", "shipment_status": "in-transit"}
Example Response: eta: 0.5 hours, shipment_id: 12345, destination: Philadelphia, shipment_status: in-transit

User query: ${user_query}

Response:
"""


def create_shipment_eta_prompt():
    """
    Builds a prompt for extracting the shipment ID from a user's query.

    Returns:
        Prompt: A prompt that extracts the shipment ID in JSON format.
    """
    return Prompt(
        user_message=get_shipment_eta,
        model="gemini-2.5-flash",
        provider="gemini",
    )


def create_shipment_prompt_card() -> PromptCard:
    """
    Creates a response prompt card for extracting shipment IDs.

    Returns:
        PromptCard: A prompt card for extracting shipment IDs.
    """
    shipment_extraction_card = PromptCard(
        prompt=create_shipment_eta_prompt(),
        space="opsml",
        name="shipment_eta",
    )

    shipment_extraction_card.create_drift_profile(
        alias="shipment_metrics",
        config=LLMDriftConfig(
            sample_rate=1,
            alert_config=LLMAlertConfig(schedule=CommonCrons.Every6Hours),
        ),
        metrics=[shipment_eta_task_evaluation],
    )

    return shipment_extraction_card
