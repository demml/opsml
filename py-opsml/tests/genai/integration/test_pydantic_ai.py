# this suite of tests runs through the basic pydanictic_ai workflows
# These tests require a user to have api keys configured in their environment
from opsml.potato_head import Prompt
from pydantic_ai import Agent
from pydantic import BaseModel


class TodaysDate(BaseModel):
    date: str


def test_string_openai_prompt():
    # test string prompt
    prompt = Prompt(
        model="openai:gpt-4o-mini",
        prompt="What is today's date?",
        system_prompt="You are a helpful assistant.",
    )

    agent = Agent(
        prompt.model,
        system_prompt=prompt.system_prompt[0].unwrap(),
        result_type=TodaysDate,
    )
    result = agent.run_sync(prompt.prompt[0].unwrap())

    assert result.data.date is not None
