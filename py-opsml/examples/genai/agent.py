from opsml.potato_head import (
    Prompt,
    Agent,
    Task,
    Workflow,
    Provider,
)
from pydantic import BaseModel
from opsml.logging import RustyLogger, LoggingConfig, LogLevel


RustyLogger.setup_logging(LoggingConfig(log_level=LogLevel.Debug))


class Answer(BaseModel):
    number: int


class FinalAnswer(BaseModel):
    is_4: bool


if __name__ == "__main__":
    first_prompt = Prompt(
        user_message="What is 1 + 1?",
        model="o3-mini",
        provider="openai",
        response_format=Answer,
    )

    second_prompt = Prompt(
        user_message="Please add the result of the previous task to 2.",
        model="o3-mini",
        provider="openai",
        response_format=Answer,
    )

    third_prompt = Prompt(
        user_message="Is the result of the previous task equal to 4?",
        model="o3-mini",
        provider="openai",
        response_format=FinalAnswer,
    )

    open_agent = Agent(Provider.OpenAI)

    workflow = Workflow(
        name="Math Workflow"
    )  # expand named argument to allow agents and tasks
    workflow.add_agent(open_agent)  # allow adding list of agents
    workflow.add_tasks(  # allow adding list of tasks
        [
            Task(
                prompt=first_prompt,
                agent_id=open_agent.id,
                id="task1",
            ),
            Task(
                prompt=second_prompt,
                agent_id=open_agent.id,
                id="task2",
                dependencies=["task1"],
            ),
            Task(
                prompt=third_prompt,
                agent_id=open_agent.id,
                id="task3",
                dependencies=["task2"],
            ),
        ]
    )
    workflow.run()
    for task in workflow.tasks.tasks.values():
        print(f"Task {task.id} result: {task.result}")
