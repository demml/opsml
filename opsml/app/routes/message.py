# pylint: disable=protected-access

# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Request

from opsml.app.routes.pydantic_models import Success
from opsml.helpers.logging import ArtifactLogger
from opsml.registry.sql.base.server import ServermessageRegistry
from opsml.types.extra import Message

logger = ArtifactLogger.get_logger()
router = APIRouter()


def organize_messages(messages: List[Message]) -> List[Dict[str, Any]]:
    """Organize messages into a hierarchical structure

    Args:
        messages:
            List of messages

    Returns:
        List of messages organized into parent and replies
    """

    message_dict = {}
    root_messages = []

    # First pass: Create a dictionary of all messages
    for message in messages:
        message_dict[message.message_id] = {"message": message, "replies": []}

    # Second pass: Organize messages into a hierarchical structure
    for message in messages:
        if message.parent_id is None:
            root_messages.append(message_dict[message.message_id])
        else:
            parent = message_dict.get(message.parent_id)
            if parent:
                parent["replies"].append(message_dict[message.message_id])

    return root_messages


@router.put("/{registry}/messages", response_model=Success)
def update_user(request: Request, message: Message) -> Success:
    """Inserts message into message table

    Args:
        request:
            FastAPI request object
        message:
            messageModel
    """

    messages_db = request.app.state.messages_db
    assert isinstance(messages_db, ServermessageRegistry)

    try:
        messages_db.insert_message(message)
        return Success(message="message inserted successfully")
    except Exception as e:
        logger.error("Error inserting message: {}", e)
        raise HTTPException(status_code=500, detail="Error inserting message")


# get messages or uid and registry
@router.get("/{registry}/messages", response_model=List[Optional[Dict[str, Any]]])
def get_message(request: Request, uid: str, registry: str) -> List[Optional[Dict[str, Any]]]:
    """Get message from message table

    Args:
        request:
            FastAPI request object
        uid:
            uid of the message
        registry:
            registry of the message
    """

    messages_db = request.app.state.messages_db
    assert isinstance(messages_db, ServermessageRegistry)

    try:
        messages = messages_db.get_messages(registry=registry, uid=uid)
        organized_messages = organize_messages(messages)

        return organized_messages

    except Exception as e:
        logger.error("Error getting message: {}", e)
        raise HTTPException(status_code=500, detail="Error getting message")
