from opsml import (  # type: ignore
    CardRegistry,
    RegistryType,
    ChatPrompt,
    PromptCard,
)
from opsml.test import OpsmlTestServer


def test_promptcard_crud() -> None:
    with OpsmlTestServer():
        reg: CardRegistry[PromptCard] = CardRegistry(RegistryType.Prompt)

        prompt = ChatPrompt(
            model="gpt-4o",
            messages=[
                {"role": "developer", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello!"},
            ],
            logprobs=True,
            top_logprobs=2,
        )

        card = PromptCard(prompt=prompt, repository="test", name="test")
        reg.register_card(card)

        assert card.uid is not None

        loaded_card = reg.load_card(uid=card.uid)
        assert loaded_card.name == card.name

        assert loaded_card.version == card.version

        loaded_card.name = "updated"
        reg.update_card(loaded_card)

        loaded_card2 = reg.load_card(uid=card.uid)
        assert loaded_card2.name == "updated"

        # list cards
        cards = reg.list_cards()

        assert cards.__len__() == 1

        # delete the card
        reg.delete_card(loaded_card)

        cards = reg.list_cards()

        assert cards.__len__() == 0
    a
