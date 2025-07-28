from opsml import (  # type: ignore
    CardRegistry,
    RegistryType,
    Prompt,
    PromptCard,
)
from opsml.scouter.drift import LLMDriftConfig, LLMMetric, LLMDriftProfile
from opsml.scouter.alert import AlertThreshold
from opsml.llm import Score, Agent, Task, Workflow
from opsml.mock import OpsmlTestServer, LLMTestServer
import pytest
from tests.conftest import WINDOWS_EXCLUDE


def create_reformulation_evaluation_prompt():
    """
    Builds a prompt for evaluating the quality of a reformulated query.

    Returns:
        Prompt: A prompt that asks for a JSON evaluation of the reformulation.

    Example:
        >>> prompt = create_reformulation_evaluation_prompt()
    """
    return Prompt(
        user_message=(
            "You are an expert evaluator of search query reformulations. "
            "Given the original user query and its reformulated version, your task is to assess how well the reformulation improves the query. "
            "Consider the following criteria:\n"
            "- Does the reformulation make the query more explicit and comprehensive?\n"
            "- Are relevant synonyms, related concepts, or specific features added?\n"
            "- Is the original intent preserved without changing the meaning?\n"
            "- Is the reformulation clear and unambiguous?\n\n"
            "Provide your evaluation as a JSON object with the following attributes:\n"
            "- score: An integer from 1 (poor) to 5 (excellent) indicating the overall quality of the reformulation.\n"
            "- reason: A brief explanation for your score.\n\n"
            "Format your response as:\n"
            "{\n"
            '  "score": <integer 1-5>,\n'
            '  "reason": "<your explanation>"\n'
            "}\n\n"
            "Original Query:\n"
            "${user_query}\n\n"
            "Reformulated Query:\n"
            "${response}\n\n"
            "Evaluation:"
        ),
        model="gemini-2.5-flash-lite-preview-06-17",
        provider="gemini",
        response_format=Score,
    )


@pytest.mark.skipif(WINDOWS_EXCLUDE, reason="skipping")
def test_promptcard_crud() -> None:
    with OpsmlTestServer():
        with LLMTestServer():
            reg: CardRegistry[PromptCard] = CardRegistry(RegistryType.Prompt)

            prompt = Prompt(
                model="gpt-4o",
                provider="openai",
                user_message="Hello!",
                system_message="You are a helpful assistant.",
            )

            card = PromptCard(prompt=prompt, space="test", name="test")

            card.create_drift_profile(
                alias="llm_drift",
                config=LLMDriftConfig(),
                metrics=[
                    LLMMetric(
                        name="reformulation_quality",
                        prompt=create_reformulation_evaluation_prompt(),
                        value=3.0,
                        alert_threshold=AlertThreshold.Below,
                    )
                ],
            )

            assert not card.drift_profile.is_empty()

            reg.register_card(card)

            assert card.uid is not None

            loaded_card = reg.load_card(uid=card.uid)
            assert loaded_card.name == card.name
            assert not loaded_card.drift_profile.is_empty()

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


@pytest.mark.skipif(WINDOWS_EXCLUDE, reason="skipping")
def test_promptcard_drift_workflow() -> None:
    with OpsmlTestServer():
        with LLMTestServer():
            reg: CardRegistry[PromptCard] = CardRegistry(RegistryType.Prompt)
            start_prompt = Prompt(
                user_message="${input} + ${response}?",
                system_message="You are a helpful assistant.",
                model="gpt-4o",
                provider="openai",
            )

            end_prompt = Prompt(
                user_message="Foo bar",
                system_message="You are a helpful assistant.",
                model="gpt-4o",
                provider="openai",
                response_format=Score,
            )

            open_agent = Agent("openai")
            workflow = Workflow(name="test_workflow")
            workflow.add_agent(open_agent)
            workflow.add_tasks(
                [  # allow adding list of tasks
                    Task(
                        prompt=start_prompt,
                        agent_id=open_agent.id,
                        id="start_task",
                    ),
                    Task(
                        prompt=end_prompt,
                        agent_id=open_agent.id,
                        id="relevance",
                        dependencies=["start_task"],
                    ),
                ]
            )

            metric = LLMMetric(
                name="relevance",
                value=5.0,
                alert_threshold=AlertThreshold.Below,
            )

            prompt = Prompt(
                model="gpt-4o",
                provider="openai",
                user_message="Hello!",
                system_message="You are a helpful assistant.",
            )

            card = PromptCard(prompt=prompt, space="test", name="test")

            card.create_drift_profile(
                alias="llm_drift",
                config=LLMDriftConfig(),
                metrics=[metric],
                workflow=workflow,
            )

            assert not card.drift_profile.is_empty()

            reg.register_card(card)

            # Feed profile directly to PromptCard
            profile = LLMDriftProfile(
                config=LLMDriftConfig(),
                workflow=workflow,
                metrics=[metric],
            )

            card = PromptCard(
                prompt=prompt,
                space="test",
                name="test",
                drift_profile={"llm_drift": profile},
            )
