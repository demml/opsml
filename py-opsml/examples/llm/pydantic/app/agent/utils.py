from typing import Dict

from pydantic import BaseModel
from pydantic_ai.agent import AgentRunResult
from pydantic_ai.messages import ToolCallPart, ToolReturnPart, UserPromptPart


class ShipmentEvents(BaseModel):
    """
    A model to hold the parsed shipment events.
    """

    tool_call: str
    tool_response: str
    llm_response: str
    user_query: str


def parse_shipment_events(response: AgentRunResult) -> Dict[str, str]:
    """
    Extracts the text from the first part of the content of the final response event.
    Returns None if no final response event is found or if it has no content.
    """

    response_dict: Dict[str, str] = {}

    msgs = response.all_messages()

    for msg in msgs:
        for part in msg.parts:
            if isinstance(part, ToolCallPart):
                response_dict["tool_call"] = part.__str__()
            elif isinstance(part, ToolReturnPart):
                response_dict["tool_response"] = part.__str__()
            elif isinstance(part, UserPromptPart):
                if isinstance(part.content, str):
                    response_dict["user_query"] = part.content

    response_dict["llm_response"] = response.output

    return response_dict


def parse_response_events(response: AgentRunResult) -> Dict[str, str]:
    """
    Extracts the text from the first part of the content of the final response event.
    Returns None if no final response event is found or if it has no content.
    """

    response_dict = {
        "llm_response": response.output,
    }

    return response_dict
