# pylint: disable=protected-access

# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


from typing import List, Dict, Any

from fastapi import APIRouter, HTTPException, Request

from opsml.app.routes.pydantic_models import Success
from opsml.helpers.logging import ArtifactLogger
from opsml.registry.sql.base.server import ServerCommentRegistry
from opsml.types.extra import Comment

logger = ArtifactLogger.get_logger()
router = APIRouter()


def organize_comments(comments: List[Comment]) -> List[Dict[str, Any]]:
    """Organize comments into a hierarchical structure

    Args:
        comments:
            List of comments

    Returns:
        List of comments organized into parent and replies
    """

    comment_dict = {}
    root_comments = []

    # First pass: Create a dictionary of all comments
    for comment in comments:
        comment_dict[comment.comment_id] = {"comment": comment, "replies": []}

    # Second pass: Organize comments into a hierarchical structure
    for comment in comments:
        if comment.parent_id is None:
            root_comments.append(comment_dict[comment.comment_id])
        else:
            parent = comment_dict.get(comment.parent_id)
            if parent:
                parent["replies"].append(comment_dict[comment.comment_id])

    return root_comments


@router.put("/{registry}/comments", response_model=Success)
def update_user(request: Request, comment: Comment) -> Success:
    """Inserts comment into comment table

    Args:
        request:
            FastAPI request object
        comment:
            CommentModel
    """

    comments_db = request.app.state.comments_db
    assert isinstance(comments_db, ServerCommentRegistry)

    try:
        comments_db.insert_comment(comment)
        return Success(message="Comment inserted successfully")
    except Exception as e:
        logger.error("Error inserting comment: {}", e)
        raise HTTPException(status_code=500, detail="Error inserting comment")


# get comments or uid and registry
@router.get("/{registry}/comments", response_model=List[Comment])
def get_comment(request: Request, uid: str, registry: str) -> List[Dict[str, Any]]:
    """Get comment from comment table

    Args:
        request:
            FastAPI request object
        uid:
            uid of the comment
        registry:
            registry of the comment
    """

    comments_db = request.app.state.comments_db
    assert isinstance(comments_db, ServerCommentRegistry)

    try:
        comments = comments_db.get_comments(registry=registry, uid=uid)

        return organize_comments(comments)

    except Exception as e:
        logger.error("Error getting comment: {}", e)
        raise HTTPException(status_code=500, detail="Error getting comment")
