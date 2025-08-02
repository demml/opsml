from google.adk.events.event import Event
from typing import Dict
from pydantic import BaseModel


class ShipmentEvents(BaseModel):
    """
    A model to hold the parsed shipment events.
    """

    tool_call: str
    tool_response: str
    llm_response: str
    user_query: str


def parse_shipment_events(events: list[Event]) -> Dict[str, str]:
    """
    Extracts the text from the first part of the content of the final response event.
    Returns None if no final response event is found or if it has no content.
    """

    response_dict: Dict[str, str] = {}

    for event in events:
        for call in event.get_function_calls() or []:
            if call.name == "get_shipment_eta_by_id":
                response_dict["tool_call"] = call.model_dump_json()
        for response in event.get_function_responses() or []:
            if response.name == "get_shipment_eta_by_id":
                response_dict["tool_response"] = response.model_dump_json()
        if (
            event.is_final_response()
            and getattr(event, "content", None)
            and getattr(event.content, "parts", None)
            and getattr(event.content, "role", None) == "model"
        ):
            response_dict["llm_response"] = event.content.parts[0].text or "No response"  # type: ignore

    return response_dict


def parse_response_events(events: list[Event]) -> Dict[str, str]:
    """
    Extracts the text from the first part of the content of the final response event.
    Returns None if no final response event is found or if it has no content.
    """

    response_dict: Dict[str, str] = {}

    for event in events:
        if (
            event.is_final_response()
            and getattr(event, "content", None)
            and getattr(event.content, "parts", None)
            and getattr(event.content, "role", None) == "model"
        ):
            response_dict["llm_response"] = event.content.parts[0].text or "No response"  # type: ignore

    return response_dict
