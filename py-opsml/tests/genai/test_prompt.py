from pydantic_ai import Agent
from pydantic_ai.models.test import TestModel
from opsml.potato_head import Prompt, ImageUrl
import httpx


def test_string_prompt():
    prompt = Prompt(
        model="openai:gpt-4o",
        prompt="prompt",
        system_prompt="system_prompt",
    )

    agent = Agent("openai:gpt-4o", system_prompt=prompt.system_prompt)
    with agent.override(model=TestModel()):
        agent.run_sync(user_prompt=prompt.prompt)


def test_image_prompt():
    prompt = Prompt(
        model="openai:gpt-4o",
        prompt=[
            "What company is this logo from?",
            ImageUrl(url="https://iili.io/3Hs4FMg.png"),
        ],
        system_prompt="system_prompt",
    )

    agent = Agent("openai:gpt-4o", system_prompt=prompt.system_prompt)
    with agent.override():
        agent.run_sync(user_prompt=prompt.prompt)


def test_binary_prompt():
    image_response = httpx.get("https://iili.io/3Hs4FMg.png")

    prompt = Prompt(
        model="openai:gpt-4o",
        prompt=[
            "What company is this logo from?",
            BinaryContent(data=image_response.content, media_type="image/png"),
        ],
        system_prompt="system_prompt",
    )

    agent = Agent("openai:gpt-4o", system_prompt=prompt.system_prompt)
    with agent.override():
        agent.run_sync(user_prompt=prompt.prompt)
