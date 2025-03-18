from pydantic_ai import Agent
from pydantic_ai.models.test import TestModel
from opsml.potato_head import Prompt


def test_string_prompt():
    prompt = Prompt(
        model="openai:gpt-4o",
        prompt="prompt",
        system_prompt="system_prompt",
    )

    agent = Agent("openai:gpt-4o", system_prompt=prompt.system_prompt)
    with agent.override(model=TestModel()):
        result = agent.run_sync(user_prompt=prompt.prompt)


def test_image_prompt():
    prompt = Prompt(
        model="openai:gpt-4o",
        prompt="prompt",
        system_prompt="system_prompt",
    )

    agent = Agent("openai:gpt-4o", system_prompt=prompt.system_prompt)
    with agent.override(model=TestModel()):
        result = agent.run_sync(user_prompt=prompt.prompt)
