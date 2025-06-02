from pydantic_ai import Agent, RunContext, models

from pydantic_ai.models.test import TestModel
from opsml.potato_head import Prompt, SanitizationConfig, PromptSanitizer
from dataclasses import dataclass
import os
from opsml.mock import OpenAITestServer

models.ALLOW_MODEL_REQUESTS = False
os.environ["OPENAI_API_KEY"] = "mock_api_key"


@dataclass
class Prompts:
    prompt_step1: Prompt
    prompt_step2: Prompt


def _test_simple_workflow(prompt_step1: Prompt):
    agent = Agent(
        prompt_step1.model_identifier,
        system_prompt=prompt_step1.system_prompt[0].unwrap(),
    )

    with agent.override(model=TestModel()):
        agent.run_sync(prompt_step1.prompt[0].unwrap())


def _test_simple_dep_workflow(prompt_step1: Prompt, prompt_step2: Prompt):
    agent = Agent(
        prompt_step1.model_identifier,
        system_prompt=prompt_step1.system_prompt[0].unwrap(),
        deps_type=Prompts,
    )

    @agent.system_prompt
    def get_system_prompt(ctx: RunContext[Prompts]) -> str:
        return ctx.deps.prompt_step1.system_prompt[0].unwrap()

    with agent.override(model=TestModel()):
        agent.run_sync(
            "hello",
            deps=Prompts(
                prompt_step1=prompt_step1,
                prompt_step2=prompt_step2,
            ),
        )


def _test_binding_workflow(prompt_step1: Prompt, prompt_step2: Prompt):
    agent = Agent(
        "openai:gpt-4o",
        system_prompt=prompt_step1.system_prompt[0].unwrap(),
        deps_type=Prompts,
    )

    @agent.tool
    def bind_context(ctx: RunContext[Prompts], search_query: str) -> str:
        bound = ctx.deps.prompt_step1.prompt[0].bind(search_query).unwrap()
        return bound

    with agent.override(model=TestModel()):
        result = agent.run_sync(
            "potatohead",
            deps=Prompts(
                prompt_step1=prompt_step1,
                prompt_step2=prompt_step2,
            ),
        )

        # make sure tool was called
        assert result.all_messages()[2].parts[0].tool_name == "bind_context"  # type: ignore


def _test_sanitization_workflow(prompt_step1: Prompt):
    santization_config = SanitizationConfig.standard()
    santization_config.error_on_high_risk = False

    sanitizer = PromptSanitizer(santization_config)

    agent = Agent(
        prompt_step1.model_identifier,
        system_prompt=prompt_step1.system_prompt[0].unwrap(),
    )

    with agent.override(model=TestModel()):
        # make sure the prompt was sanitized
        prompt = """{
            "bob":
            {
                "phone": "123-456-7890",
                "ssn": "123-45-6789",
            },
            "alice":
            {
                "phone": "123-456-7890",
                "ssn": "123-45-6789",
            },
        }"""

        result = sanitizer.sanitize(prompt)
        agent.run_sync(result.sanitized_text)

        assert len(result.detected_issues) == 2


def test_opsml_agent_workflow():
    with OpenAITestServer():
        print("hello world")
