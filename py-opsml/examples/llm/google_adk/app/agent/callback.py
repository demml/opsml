from google.adk.agents.callback_context import CallbackContext
from google.genai import types
from google.adk.events.event import Event
from .utils import get_text_from_content
from typing import Optional, Dict


def parse_model_events(events: list[Event]) -> Dict[str, str]:
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


def parse_model_output(
    callback_context: CallbackContext,
) -> Optional[types.Content]:
    """
    Logs exit from an agent and checks 'add_concluding_note' in session state.
    If True, returns new Content to *replace* the agent's original output.
    If False or not present, returns None, allowing the agent's original output to be used.
    """

    user_content = get_text_from_content(callback_context.user_content)
    events = parse_model_events(callback_context._invocation_context.session.events)

    if user_content:
        print(f"User content: {user_content}")
        print(f"Events: {events}")

    return None
