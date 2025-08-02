from google.adk.events.event import Event
from google.genai import types


def get_final_event(events: list[Event]) -> str | None:
    """Returns the last event from the list of events."""
    for event in events:  # Debugging line to print the event
        if event.is_final_response():
            if event.content and event.content.parts:
                # Return the text of the first part of the content
                return event.content.parts[0].text
    return None


def get_text_from_content(content: types.Content | None) -> str | None:
    """Extracts text from the content."""
    if content and content.parts:
        return content.parts[0].text if content.parts else ""
    return ""
