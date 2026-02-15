from pathlib import Path
from typing import cast
from opsml.card import CardRegistry, RegistryType, PromptCard
from opsml.types import DriftArgs
from opsml.scouter.evaluate import GenAIEvalConfig, LLMJudgeTask, ComparisonOperator
from opsml.genai import Prompt, Provider
from opsml.genai.google import GeminiSettings
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
            card = PromptCard(
                prompt=prompt,
                space="test",
                name="test",
            )

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


def test_load_prompt_from_file():
    file_path = Path(__file__).parent / "assets" / "prompt.yaml"
    prompt_card = PromptCard.from_path(file_path)

    assert prompt_card.name == "my-prompt"
    assert prompt_card.space == "opsml"
    assert prompt_card.prompt.model == "gemini-2.5-flash"
    assert prompt_card.prompt.provider == Provider.Google

    assert (
        prompt_card.prompt.message.text
        == "Analyze the sentiment of the provided text {input}"
    )
    assert (
        prompt_card.prompt.system_instructions[0].text == "You are a helpful assistant"
    )
    settings = cast(GeminiSettings, prompt_card.prompt.model_settings)

    assert round(settings.generation_config.temperature, 1) == 0.7
    assert settings.generation_config.max_output_tokens == 1024
    assert round(settings.generation_config.top_p, 1) == 0.9
    assert settings.generation_config.frequency_penalty == 0.0
    assert settings.generation_config.stop_sequences == ["###"]

    profile = prompt_card.eval_profile
    assert profile is not None
    assert profile.alias == "sentiment_analysis_eval"
    assert profile.has_assertions()
    tasks = profile.assertion_tasks
    task1 = tasks[0]
    assert task1.id == "sentiment_score_assertion"
    assert task1.field_path == "sentiment.score"
    task2 = tasks[1]
    assert task2.id == "validate_email"
    assert task2.field_path == "user.email"
