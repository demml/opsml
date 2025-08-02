from pydantic import BaseModel, Field
import uuid


class Answer(BaseModel):
    message: str


class Question(BaseModel):
    user_id: str = Field(
        default_factory=lambda: "user-123",
        description="Unique user identifier",
    )
    session_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique session identifier",
    )
    question: str
