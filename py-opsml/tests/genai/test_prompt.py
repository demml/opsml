from pydantic_ai import (
    ImageUrl as PydanticImageUrl,
    BinaryContent as PydanticBinaryContent,
    DocumentUrl as PydanticDocumentUrl,
)
from pydantic import BaseModel
from pydantic_ai.settings import ModelSettings as PydanticModelSettings
from opsml.genai import (
    Prompt,
    ImageUrl,
    BinaryContent,
    Message,
    DocumentUrl,
    ModelSettings,
)
from typing import List
import httpx


class CityLocation(BaseModel):
    city: str
    country: str
    zip_codes: List[int]


def test_string_prompt():
    # test string prompt
    prompt = Prompt(
        model="gpt-4o",
        provider="openai",
        user_message="My prompt ${1} is ${2}",
        system_message="system_prompt",
    )
    assert prompt.user_message[0].unwrap() == "My prompt ${1} is ${2}"
    assert prompt.system_message[0].unwrap() == "system_prompt"

    # test string message
    prompt = Prompt(
        model="gpt-4o",
        provider="openai",
        user_message=Message(content="My prompt ${1} is ${2}"),
        system_message="system_prompt",
    )

    assert prompt.user_message[0].unwrap() == "My prompt ${1} is ${2}"

    # test list of string messages
    prompt = Prompt(
        model="gpt-4o",
        provider="openai",
        user_message=[
            Message(content="My prompt ${1} is ${2}"),
            Message(content="My prompt ${3} is ${4}"),
        ],
        system_message="system_prompt",
    )

    assert prompt.user_message[0].unwrap() == "My prompt ${1} is ${2}"
    assert prompt.user_message[1].unwrap() == "My prompt ${3} is ${4}"

    # test list of strings
    prompt = Prompt(
        model="gpt-4o",
        provider="openai",
        user_message=[
            "My prompt ${1} is ${2}",
            "My prompt ${3} is ${4}",
        ],
        system_message="system_prompt",
    )

    assert prompt.user_message[0].unwrap() == "My prompt ${1} is ${2}"
    assert prompt.user_message[1].unwrap() == "My prompt ${3} is ${4}"

    bounded_message = prompt.user_message[0].bind("1", "world").unwrap()
    assert bounded_message == "My prompt world is ${2}"


def test_image_prompt():
    prompt = Prompt(
        model="gpt-4o",
        provider="openai",
        user_message=[
            "What company is this logo from?",
            ImageUrl(url="https://iili.io/3Hs4FMg.png"),
        ],
        system_message="system_prompt",
    )

    assert prompt.user_message[0].unwrap() == "What company is this logo from?"

    # unwrap for image url will convert to expected pydantic dataclass
    assert isinstance(prompt.user_message[1].unwrap(), PydanticImageUrl)


def test_binary_prompt():
    image_response = httpx.get("https://iili.io/3Hs4FMg.png")

    prompt = Prompt(
        model="gpt-4o",
        provider="openai",
        user_message=[
            "What company is this logo from?",
            BinaryContent(data=image_response.content, media_type="image/png"),
        ],
        system_message="system_prompt",
    )

    assert prompt.user_message[0].unwrap() == "What company is this logo from?"
    assert isinstance(prompt.user_message[1].unwrap(), PydanticBinaryContent)


def test_document_prompt():
    prompt = Prompt(
        model="gpt-4o",
        provider="openai",
        user_message=[
            "What is the main content of this document?",
            DocumentUrl(
                url="https://storage.googleapis.com/cloud-samples-data/generative-ai/pdf/2403.05530.pdf"
            ),
        ],
        system_message="system_prompt",
    )

    assert (
        prompt.user_message[0].unwrap() == "What is the main content of this document?"
    )
    assert isinstance(prompt.user_message[1].unwrap(), PydanticDocumentUrl)


def test_model_settings_prompt():
    settings = ModelSettings(
        model="gpt-4o",
        provider="openai",
        temperature=0.5,
        max_tokens=100,
        top_p=0.9,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        extra_body={"key": "value"},
    )

    prompt = Prompt(
        user_message=[
            "My prompt ${1} is ${2}",
            "My prompt ${3} is ${4}",
        ],
        model_settings=settings,
    )

    settings = PydanticModelSettings(**prompt.model_settings.model_dump())


def test_prompt_response_format():
    prompt = Prompt(
        model="gpt-4o",
        provider="openai",
        user_message="My prompt ${1} is ${2}",
        system_message="system_prompt",
        response_format=CityLocation,
    )

    assert prompt.response_format is not None
