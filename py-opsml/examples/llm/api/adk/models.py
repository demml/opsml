from pydantic import BaseModel


class Answer(BaseModel):
    message: str


class Question(BaseModel):
    question: str
