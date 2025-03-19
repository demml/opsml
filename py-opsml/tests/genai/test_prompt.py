from pydantic_ai import Agent
from pydantic_ai.models.test import TestModel
from opsml.potato_head import Prompt, ImageUrl, BinaryContent, Message
import httpx


def test_string_prompt():
    # test string prompt
    prompt = Prompt(
        model="openai:gpt-4o",
        prompt="My prompt $1 is $2",
        system_prompt="system_prompt",
    )
    assert prompt.prompt[0].unwrap() == "My prompt $1 is $2"
    assert prompt.system_prompt[0].unwrap() == "system_prompt"

    # test string message
    prompt = Prompt(
        model="openai:gpt-4o",
        prompt=Message(content="My prompt $1 is $2"),
        system_prompt="system_prompt",
    )

    assert prompt.prompt[0].unwrap() == "My prompt $1 is $2"

    # test list of string messages
    prompt = Prompt(
        model="openai:gpt-4o",
        prompt=[
            Message(content="My prompt $1 is $2"),
            Message(content="My prompt $3 is $4"),
        ],
        system_prompt="system_prompt",
    )

    assert prompt.prompt[0].unwrap() == "My prompt $1 is $2"
    assert prompt.prompt[1].unwrap() == "My prompt $3 is $4"

    # test list of strings
    prompt = Prompt(
        model="openai:gpt-4o",
        prompt=[
            "My prompt $1 is $2",
            "My prompt $3 is $4",
        ],
        system_prompt="system_prompt",
    )

    assert prompt.prompt[0].unwrap() == "My prompt $1 is $2"
    assert prompt.prompt[1].unwrap() == "My prompt $3 is $4"


def _test_image_prompt():
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


def _test_binary_prompt():
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
