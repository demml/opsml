from opsml.card import CardRegistry, RegistryType, PromptCard
from opsml.types import DriftArgs
from opsml.scouter.evaluate import GenAIEvalConfig, LLMJudgeTask, ComparisonOperator
from opsml.genai import Prompt
from opsml.mock import OpsmlTestServer, LLMTestServer
import pytest
from tests.conftest import WINDOWS_EXCLUDE


@pytest.mark.skipif(WINDOWS_EXCLUDE, reason="skipping")
def test_promptcard_crud(reformulation_evaluation_prompt: Prompt) -> None:
    with OpsmlTestServer():
        with LLMTestServer():
            reg: CardRegistry[PromptCard] = CardRegistry(RegistryType.Prompt)

            prompt = Prompt(
                model="gpt-4o",
                provider="openai",
                messages="Hello!",
                system_instructions="You are a helpful assistant.",
            )

            card = PromptCard(prompt=prompt, space="test", name="test")

            card.create_eval_profile(
                alias="genai_eval",
                config=GenAIEvalConfig(),
                tasks=[
                    LLMJudgeTask(
                        id="score_assertion",
                        prompt=reformulation_evaluation_prompt,
                        field_path="score",
                        operator=ComparisonOperator.GreaterThan,
                        expected_value=1,
                        description="Check that score is greater than 1",
                    ),
                ],
            )

            assert card.eval_profile is not None

            reg.register_card(
                card,
                save_kwargs={
                    "drift": DriftArgs(  # we want to set the drift profile to active
                        active=True,
                        deactivate_others=True,
                    ),
                },
            )

            assert card.uid is not None

            loaded_card = reg.load_card(uid=card.uid)
            assert loaded_card.name == card.name
            assert loaded_card.eval_profile is not None

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
