# this suite of tests runs through the basic pydanictic_ai workflows
# These tests require a user to have api keys configured in their environment
from opsml.genai import Prompt  # type: ignore
from pydantic_ai import Agent
from pydantic import BaseModel


class TodaysDate(BaseModel):
    date: str


def test_string_openai_prompt():
    # test string prompt
    prompt = Prompt(
        model="gpt-4o-mini",
        user_message="What is today's date?",
        provider="openai",
        system_message="You are a helpful assistant.",
    )

    agent = Agent(
        prompt.model_identifier,
        system_prompt=prompt.system_message[0].unwrap(),
        result_type=TodaysDate,
    )
    result = agent.run_sync(prompt.user_message[0].unwrap())

    assert result.data.date is not None
