from google.adk.agents.callback_context import CallbackContext
from google.genai import types
from google.adk.events.event import Event
from .utils import get_text_from_content
from typing import Optional


def get_model_event_text(events: list[Event]) -> str | None:
    """
    Extracts the text from the first part of the content of the final response event.
    Returns None if no final response event is found or if it has no content.
    """
    for event in events:  # Debugging line to print the event
        if event.is_final_response():
            if event.content and event.content.parts:
                if event.content.role == "model":
                    # Debugging line to print the event content
                    return event.content.parts[0].text
    return None


def modify_output_after_agent(
    callback_context: CallbackContext,
) -> Optional[types.Content]:
    """
    Logs exit from an agent and checks 'add_concluding_note' in session state.
    If True, returns new Content to *replace* the agent's original output.
    If False or not present, returns None, allowing the agent's original output to be used.
    """

    user_content = get_text_from_content(callback_context.user_content)

    session_events = get_model_event_text(
        callback_context._invocation_context.session.events
    )

    if user_content and session_events:
        print("User Content:", user_content)
        print("Session Events:", session_events)
        return None

    return None
