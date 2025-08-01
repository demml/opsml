from opsml.llm import Prompt
from opsml.card import PromptCard
from opsml.scouter.drift import LLMDriftConfig
from opsml.scouter.alert import LLMAlertConfig
from opsml.scouter.types import CommonCrons
from .prompt_metrics import shipment_eta_task_evaluation, shipment_eta_reply_evaluation

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

get_shipment_eta_reply = """
You are an expert assistant for supply chain operations.

Given the following shipment ETA information, craft a clear, friendly, and helpful reply for the user.
Include all relevant details: estimated delivery time, shipment ID, destination, and shipment status.
If any information is missing, politely mention it.

Example Input:
eta: 0.5 hours, shipment_id: 12345, destination: Philadelphia, shipment_status: in-transit

Example Reply:
Your shipment (ID: 12345) is currently in transit to Philadelphia and is expected to arrive in 0.5 hours.

Shipment ETA Information:
${shipment_eta_info}

Reply:
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


def create_shipment_eta_reply_prompt():
    """
    Builds a prompt for crafting a reply based on the shipment ETA information.

    Returns:
        Prompt: A prompt that formats the reply with shipment details.
    """
    return Prompt(
        user_message=get_shipment_eta_reply,
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


def create_shipment_reply_prompt_card() -> PromptCard:
    """
    Creates a response prompt card for crafting replies based on shipment ETA information.

    Returns:
        PromptCard: A prompt card for crafting shipment replies.
    """
    shipment_reply_card = PromptCard(
        prompt=create_shipment_eta_reply_prompt(),
        space="opsml",
        name="shipment_eta_reply",
    )

    shipment_reply_card.create_drift_profile(
        alias="shipment_reply_metrics",
        config=LLMDriftConfig(
            sample_rate=1,
            alert_config=LLMAlertConfig(schedule=CommonCrons.Every6Hours),
        ),
        metrics=[shipment_eta_reply_evaluation],
    )

    return shipment_reply_card
