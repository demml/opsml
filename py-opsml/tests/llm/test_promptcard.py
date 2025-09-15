from opsml import (  # type: ignore
    CardRegistry,
    RegistryType,
    Prompt,
    PromptCard,
)
from opsml.types import DriftArgs
from opsml.scouter.drift import LLMDriftConfig, LLMDriftMetric, LLMDriftProfile
from opsml.scouter.alert import AlertThreshold
from opsml.llm import Score, Agent, Task, Workflow
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
                message="Hello!",
                system_instruction="You are a helpful assistant.",
            )

            card = PromptCard(prompt=prompt, space="test", name="test")

            card.create_drift_profile(
                alias="llm_drift",
                config=LLMDriftConfig(),
                metrics=[
                    LLMDriftMetric(
                        name="reformulation_quality",
                        prompt=reformulation_evaluation_prompt,
                        value=3.0,
                        alert_threshold=AlertThreshold.Below,
                    )
                ],
            )

            assert not card.drift_profile.is_empty()

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
                message="${input} + ${response}?",
                system_instruction="You are a helpful assistant.",
                model="gpt-4o",
                provider="openai",
            )

            end_prompt = Prompt(
                message="Foo bar",
                system_instruction="You are a helpful assistant.",
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

            metric = LLMDriftMetric(
                name="relevance",
                value=5.0,
                alert_threshold=AlertThreshold.Below,
            )

            prompt = Prompt(
                model="gpt-4o",
                provider="openai",
                message="Hello!",
                system_instruction="You are a helpful assistant.",
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
