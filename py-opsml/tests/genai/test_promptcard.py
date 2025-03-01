from opsml import (  # type: ignore
    CardRegistry,
    RegistryType,
    ChatPrompt,
    PromptCard,
)
from opsml.test import OpsmlTestServer


def test_promptcard():
    with OpsmlTestServer():
        reg = CardRegistry(RegistryType.Prompt)

        prompt = ChatPrompt(
            model="gpt-4o",
            messages=[
                {"role": "developer", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello!"},
            ],
            logprobs=True,
            top_logprobs=2,
        )

        prompt_card = PromptCard(prompt=prompt, repository="test", name="test")
        reg.register_card(prompt_card)

        assert prompt_card.uid is not None
