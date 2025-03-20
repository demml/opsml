from opsml.potato_head import Prompt
import pytest


@pytest.fixture(scope="module")
def prompt_step1():
    return Prompt(
        model="openai:gpt-4o",
        prompt="Prompt for task 1. Context: $1",
        system_prompt="You are a helpful assistant.",
    )


@pytest.fixture(scope="module")
def prompt_step2():
    return Prompt(
        model="openai:gpt-4o",
        prompt="Prompt for task 2. Context: $1",
    )
