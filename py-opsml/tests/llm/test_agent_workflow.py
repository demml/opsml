from pydantic_ai import Agent as PydanticAgent, RunContext, models

from pydantic_ai.models.test import TestModel
from opsml.llm import (
    Prompt,
    SanitizationConfig,
    PromptSanitizer,
    Agent,
    Task,
    Workflow,
    Provider,
)
from dataclasses import dataclass
import os
from opsml.mock import LLMTestServer

models.ALLOW_MODEL_REQUESTS = False
os.environ["OPENAI_API_KEY"] = "mock_api_key"


@dataclass
class Prompts:
    prompt_step1: Prompt
    prompt_step2: Prompt


def test_simple_workflow(prompt_step1: Prompt):
    agent = PydanticAgent(
        prompt_step1.model_identifier,
        system_prompt=prompt_step1.system_message[0].unwrap(),
    )

    with agent.override(model=TestModel()):
        agent.run_sync(prompt_step1.user_message[0].unwrap())


def test_simple_dep_workflow(prompt_step1: Prompt, prompt_step2: Prompt):
    agent = PydanticAgent(
        prompt_step1.model_identifier,
        system_prompt=prompt_step1.system_message[0].unwrap(),
        deps_type=Prompts,
    )

    @agent.system_prompt
    def get_system_message(ctx: RunContext[Prompts]) -> str:
        return ctx.deps.prompt_step1.system_message[0].unwrap()

    with agent.override(model=TestModel()):
        agent.run_sync(
            "hello",
            deps=Prompts(
                prompt_step1=prompt_step1,
                prompt_step2=prompt_step2,
            ),
        )


def test_binding_workflow(prompt_step1: Prompt, prompt_step2: Prompt):
    agent = PydanticAgent(
        "openai:gpt-4o",
        system_prompt=prompt_step1.system_message[0].unwrap(),
        deps_type=Prompts,
    )

    @agent.tool
    def bind_context(ctx: RunContext[Prompts], search_query: str) -> str:
        bound = (
            ctx.deps.prompt_step1.user_message[0]
            .bind(name="query_one", value=search_query)
            .unwrap()
        )
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


def test_sanitization_workflow(prompt_step1: Prompt):
    santization_config = SanitizationConfig.standard()
    santization_config.error_on_high_risk = False

    sanitizer = PromptSanitizer(santization_config)

    agent = PydanticAgent(
        prompt_step1.model_identifier,
        system_prompt=prompt_step1.system_message[0].unwrap(),
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


def test_opsml_agent_task_execution():
    with LLMTestServer():
        prompt = Prompt(
            user_message="Hello, how are you?",
            system_message="You are a helpful assistant.",
            model="gpt-4o",
            provider="openai",
        )
        agent = Agent(Provider.OpenAI)
        agent.execute_task(Task(prompt=prompt, agent_id=agent.id))


def test_opsml_agent_workflow():
    with LLMTestServer():
        prompt = Prompt(
            user_message="Hello, how are you?",
            system_message="You are a helpful assistant.",
            model="gpt-4o",
            provider="openai",
        )

        open_agent1 = Agent(Provider.OpenAI)
        open_agent2 = Agent(Provider.OpenAI)

        workflow = Workflow(
            name="test_workflow"
        )  # expand named argument to allow agents and tasks
        workflow.add_agent(open_agent1)  # allow adding list of agents
        workflow.add_agent(open_agent2)
        workflow.add_task(  # allow adding list of tasks
            Task(
                prompt=prompt,
                agent_id=open_agent1.id,
                id="task1",
            ),
        )

        workflow.add_task(
            Task(
                prompt=prompt,
                agent_id=open_agent1.id,
                id="task2",
            ),
        )
        workflow.add_task(
            Task(
                prompt=prompt,
                agent_id=open_agent2.id,  # maybe default this to first agent if none
                id="task3",
                dependencies=["task1", "task2"],
            ),
        )

        workflow.add_task(
            Task(
                prompt=prompt,
                agent_id=open_agent2.id,
                id="task4",
                dependencies=["task1"],
            ),
        )

        workflow.add_task(
            Task(
                prompt=prompt,
                agent_id=open_agent1.id,
                id="task5",
                dependencies=["task4", "task3"],
            ),
        )

        workflow.run()
