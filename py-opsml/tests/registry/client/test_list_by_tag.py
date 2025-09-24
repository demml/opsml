from opsml.mock import OpsmlTestServer  # type: ignore
from opsml import (  # type: ignore
    CardRegistry,
    RegistryType,
    PromptCard,
    Prompt,
)
from opsml.card import RegistryMode
import pytest
from tests.conftest import WINDOWS_EXCLUDE


def crud_promptcard(prompt: Prompt, tags=["test"]):
    reg = CardRegistry(registry_type="prompt")

    assert reg.registry_type == RegistryType.Prompt
    assert reg.mode == RegistryMode.Client

    card = PromptCard(
        prompt=prompt,
        space="test",
        name="test",
        tags=tags,
    )

    reg.register_card(card)


@pytest.mark.skipif(WINDOWS_EXCLUDE, reason="skipping")
def test_list_card(
    chat_prompt: Prompt,
):
    # start server
    with OpsmlTestServer():
        crud_promptcard(chat_prompt, tags=["tag1", "team1"])
        crud_promptcard(chat_prompt, tags=["tag2"])
        crud_promptcard(chat_prompt, tags=["team1"])
        crud_promptcard(chat_prompt, tags=["team1"])

        reg = CardRegistry(registry_type="prompt")

        result = reg.list_cards(tags=["tag1"])
        assert len(result) == 1
        assert result[0].tags == ["tag1", "team1"]

        result = reg.list_cards(tags=["team1"])
        assert len(result) == 3
        assert result[0].tags == ["team1"]
