# pylint: disable=redefined-builtin, invalid-name, dangerous-default-value

import datetime
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Sequence

class PromptTokenDetails:
    """Details about the prompt tokens used in a request."""

    @property
    def audio_tokens(self) -> int:
        """The number of audio tokens used in the request."""

    @property
    def cached_tokens(self) -> int:
        """The number of cached tokens used in the request."""

class CompletionTokenDetails:
    """Details about the completion tokens used in a model response."""

    @property
    def accepted_prediction_tokens(self) -> int:
        """The number of accepted prediction tokens used in the response."""

    @property
    def audio_tokens(self) -> int:
        """The number of audio tokens used in the response."""

    @property
    def reasoning_tokens(self) -> int:
        """The number of reasoning tokens used in the response."""

    @property
    def rejected_prediction_tokens(self) -> int:
        """The number of rejected prediction tokens used in the response."""

class Usage:
    """Usage statistics for a model response."""

    @property
    def completion_tokens(self) -> int:
        """The number of completion tokens used in the response."""

    @property
    def prompt_tokens(self) -> int:
        """The number of prompt tokens used in the request."""

    @property
    def total_tokens(self) -> int:
        """The total number of tokens used in the request and response."""

    @property
    def completion_tokens_details(self) -> CompletionTokenDetails:
        """Details about the completion tokens used in the response."""

    @property
    def prompt_tokens_details(self) -> "PromptTokenDetails":
        """Details about the prompt tokens used in the request."""

    @property
    def finish_reason(self) -> str:
        """The reason why the model stopped generating tokens"""

class ImageUrl:
    def __init__(
        self,
        url: str,
        kind: Literal["image-url"] = "image-url",
    ) -> None:
        """Create an ImageUrl object.

        Args:
            url (str):
                The URL of the image.
            kind (Literal["image-url"]):
                The kind of the content.
        """

    @property
    def url(self) -> str:
        """The URL of the image."""

    @property
    def kind(self) -> str:
        """The kind of the content."""

    @property
    def media_type(self) -> str:
        """The media type of the image URL."""

    @property
    def format(self) -> str:
        """The format of the image URL."""

class AudioUrl:
    def __init__(
        self,
        url: str,
        kind: Literal["audio-url"] = "audio-url",
    ) -> None:
        """Create an AudioUrl object.

        Args:
            url (str):
                The URL of the audio.
            kind (Literal["audio-url"]):
                The kind of the content.
        """

    @property
    def url(self) -> str:
        """The URL of the audio."""

    @property
    def kind(self) -> str:
        """The kind of the content."""

    @property
    def media_type(self) -> str:
        """The media type of the audio URL."""

    @property
    def format(self) -> str:
        """The format of the audio URL."""

class BinaryContent:
    def __init__(
        self,
        data: bytes,
        media_type: str,
        kind: str = "binary",
    ) -> None:
        """Create a BinaryContent object.

        Args:
            data (bytes):
                The binary data.
            media_type (str):
                The media type of the binary data.
            kind (str):
                The kind of the content
        """

    @property
    def media_type(self) -> str:
        """The media type of the binary content."""

    @property
    def format(self) -> str:
        """The format of the binary content."""

    @property
    def data(self) -> bytes:
        """The binary data."""

    @property
    def kind(self) -> str:
        """The kind of the content."""

class DocumentUrl:
    def __init__(
        self,
        url: str,
        kind: Literal["document-url"] = "document-url",
    ) -> None:
        """Create a DocumentUrl object.

        Args:
            url (str):
                The URL of the document.
            kind (Literal["document-url"]):
                The kind of the content.
        """

    @property
    def url(self) -> str:
        """The URL of the document."""

    @property
    def kind(self) -> str:
        """The kind of the content."""

    @property
    def media_type(self) -> str:
        """The media type of the document URL."""

    @property
    def format(self) -> str:
        """The format of the document URL."""

class Message:
    def __init__(self, content: str | ImageUrl | AudioUrl | BinaryContent | DocumentUrl) -> None:
        """Create a Message object.

        Args:
            content (str | ImageUrl | AudioUrl | BinaryContent | DocumentUrl):
                The content of the message.
        """

    @property
    def content(self) -> str | ImageUrl | AudioUrl | BinaryContent | DocumentUrl:
        """The content of the message"""

    def bind(self, name: str, value: str) -> "Message":
        """Bind context to a specific variable in the prompt. This is an immutable operation meaning that it
        will return a new Message object with the context bound.

            Example with Prompt that contains two messages

            ```python
                prompt = Prompt(
                    model="openai:gpt-4o",
                    message=[
                        "My prompt variable is ${variable}",
                        "This is another message",
                    ],
                    system_instruction="system_prompt",
                )
                bounded_prompt = prompt.message[0].bind("variable", "hello world").unwrap() # we bind "hello world" to "variable"
            ```

        Args:
            name (str):
                The name of the variable to bind.
            value (str):
                The value to bind the variable to.

        Returns:
            Message:
                The message with the context bound.
        """

    def bind_mut(self, name: str, value: str) -> "Message":
        """Bind context to a specific variable in the prompt. This is a mutable operation meaning that it
        will modify the current Message object.

            Example with Prompt that contains two messages

            ```python
                prompt = Prompt(
                    model="openai:gpt-4o",
                    message=[
                        "My prompt variable is ${variable}",
                        "This is another message",
                    ],
                    system_instruction="system_prompt",
                )
                prompt.message[0].bind_mut("variable", "hello world") # we bind "hello world" to "variable"
            ```

        Args:
            name (str):
                The name of the variable to bind.
            value (str):
                The value to bind the variable to.

        Returns:
            Message:
                The message with the context bound.
        """

    def unwrap(self) -> Any:
        """Unwrap the message content.

        Returns:
            A serializable representation of the message content, which can be a string, list, or dict.
        """

    def model_dump(self) -> Dict[str, Any]:
        """Unwrap the message content and serialize it to a dictionary.

        Returns:
            Dict[str, Any]:
                The message dictionary with keys "content" and "role".
        """

class ModelSettings:
    def __init__(
        self,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        timeout: Optional[float] = None,
        parallel_tool_calls: Optional[bool] = None,
        seed: Optional[int] = None,
        logit_bias: Optional[dict[str, int]] = None,
        stop_sequences: Optional[List[str]] = None,
        logprobs: Optional[bool] = None,
        extra_body: Optional[dict[str, Any]] = None,
    ) -> None:
        """ModelSettings for configuring the model.

        Args:
            model (Optional[str]):
                The model to use. This is required if model is not provided in the prompt.
                If not provided, defaults to `undefined`.
            provider (Optional[str]):
                The provider to use. This is required if provider is not provided in the prompt.
                If not provided, defaults to `undefined`.
            max_tokens (Optional[int]):
                The maximum number of tokens to generate.
            temperature (Optional[float]):
                The amount of randomness to use.
            top_p (Optional[float]):
                The top p to use.
            frequency_penalty (Optional[float]):
                The frequency penalty to use. Penalizes new tokens based on their
                frequency in the text.
            presence_penalty (Optional[float]):
                The presence penalty to use. Penalizes new tokens based
                on whether they already appear in  the text.
            timeout (Optional[float]):
                The timeout to use.
            parallel_tool_calls (Optional[bool]):
                Whether to allow parallel tool calls.
            seed (Optional[int]):
                The seed to use for the model allowing for reproducible results.
            logit_bias (Optional[dict[str, int]]):
                The logit bias to use. Modifies the likelihood of specified tokens appearing in
                the generated text.
            stop_sequences (Optional[List[str]]):
                The stop sequences to use that will cause the model to stop generating text.
            logprobs (Optional[bool]):
                Whether to include log probabilities in the response. This is a gemini specific setting.
            extra_body (Optional[dict[str, Any]]):
                The extra body to use. Must be a dictionary

        """

    @property
    def model(self) -> str:
        """The model to use."""

    @property
    def provider(self) -> str:
        """The provider to use."""

    @property
    def max_tokens(self) -> Optional[int]:
        """The maximum number of tokens to generate."""

    @property
    def temperature(self) -> Optional[float]:
        """The amount of randomness to use."""

    @property
    def top_p(self) -> Optional[float]:
        """The top p to use."""

    @property
    def frequency_penalty(self) -> Optional[float]:
        """The frequency penalty to use."""

    @property
    def presence_penalty(self) -> Optional[float]:
        """The presence penalty to use."""

    @property
    def timeout(self) -> Optional[float]:
        """The timeout to use."""

    @property
    def parallel_tool_calls(self) -> Optional[bool]:
        """Whether to allow parallel tool calls."""

    @property
    def seed(self) -> Optional[int]:
        """The seed to use for the model allowing for reproducible results."""

    @property
    def logit_bias(self) -> Optional[dict[str, int]]:
        """The logit bias to use."""

    @property
    def stop_sequences(self) -> Optional[List[str]]:
        """The stop sequences to use."""

    @property
    def extra_body(self) -> Optional[dict[str, Any]]:
        """The extra body to use."""

    def model_dump(self) -> Dict[str, Any]:
        """The model settings to use for the prompt."""

class Prompt:
    def __init__(
        self,
        message: (
            str
            | Sequence[str | ImageUrl | AudioUrl | BinaryContent | DocumentUrl]
            | Message
            | List[Message]
            | List[Dict[str, Any]]
        ),
        model: Optional[str] = None,
        provider: Optional[str] = None,
        system_instruction: Optional[str | List[str]] = None,
        model_settings: Optional[ModelSettings] = None,
        response_format: Optional[Any] = None,
    ) -> None:
        """Prompt for interacting with an LLM API.

        Args:
            message (str | Sequence[str | ImageUrl | AudioUrl | BinaryContent | DocumentUrl] | Message | List[Message]):
                The prompt to use.
            model (str | None):
                The model to use for the prompt. Required if model_settings is not provided.
                If not provided, defaults to `undefined`.
            provider (str | None):
                The provider to use for the prompt. Required if model_settings is not provided.
                If not provided, defaults `undefined`.
            system_instruction (Optional[str | List[str]]):
                The system prompt to use in the prompt.
            model_settings (None):
                The model settings to use for the prompt.
                Defaults to None which means no model settings will be used
            response_format (Optional[BaseModel | Score]):
                The response format to use for the prompt. This is used for Structured Outputs
                (https://platform.openai.com/docs/guides/structured-outputs?api-mode=chat).
                Currently, response_format only support Pydantic BaseModel classes and the PotatoHead Score class.
                The provided response_format will be parsed into a JSON schema.

        """

    @property
    def model(self) -> str:
        """The model to use for the prompt."""

    @property
    def provider(self) -> str:
        """The provider to use for the prompt."""

    @property
    def model_identifier(self) -> Any:
        """Concatenation of provider and model, used for identifying the model in the prompt. This
        is commonly used with pydantic_ai to identify the model to use for the agent.

        Example:
            ```python
                prompt = Prompt(
                    model="gpt-4o",
                    message="My prompt variable is ${variable}",
                    system_instruction="system_instruction",
                    provider="openai",
                )
                agent = Agent(
                    prompt.model_identifier, # "openai:gpt-4o"
                    system_instructions=prompt.system_instruction[0].unwrap(),
                )
            ```
        """

    @property
    def model_settings(self) -> ModelSettings:
        """The model settings to use for the prompt."""

    @property
    def message(
        self,
    ) -> List[Message]:
        """The user message to use in the prompt."""

    @property
    def system_instruction(self) -> List[Message]:
        """The system message to use in the prompt."""

    def save_prompt(self, path: Optional[Path] = None) -> None:
        """Save the prompt to a file.

        Args:
            path (Optional[Path]):
                The path to save the prompt to. If None, the prompt will be saved to
                the current working directory.
        """

    @staticmethod
    def from_path(path: Path) -> "Prompt":
        """Load a prompt from a file.

        Args:
            path (Path):
                The path to the prompt file.

        Returns:
            Prompt:
                The loaded prompt.
        """

    @staticmethod
    def model_validate_json(json_string: str) -> "Prompt":
        """Validate the model JSON.

        Args:
            json_string (str):
                The JSON string to validate.
        Returns:
            Prompt:
                The prompt object.
        """

    def model_dump_json(self) -> str:
        """Dump the model to a JSON string.

        Returns:
            str:
                The JSON string.
        """

    def bind(
        self,
        name: Optional[str] = None,
        value: Optional[str | int | float | bool | list] = None,
        **kwargs: Any,
    ) -> "Prompt":
        """Bind context to a specific variable in the prompt. This is an immutable operation meaning that it
        will return a new Prompt object with the context bound. This will iterate over all user messages.

        Args:
            name (str):
                The name of the variable to bind.
            value (str | int | float | bool | list):
                The value to bind the variable to. Must be a JSON serializable type.
            **kwargs (Any):
                Additional keyword arguments to bind to the prompt. This can be used to bind multiple variables at once.

        Returns:
            Prompt:
                The prompt with the context bound.
        """

    def bind_mut(
        self,
        name: Optional[str] = None,
        value: Optional[str | int | float | bool | list] = None,
        **kwargs: Any,
    ) -> "Prompt":
        """Bind context to a specific variable in the prompt. This is a mutable operation meaning that it
        will modify the current Prompt object. This will iterate over all user messages.

        Args:
            name (str):
                The name of the variable to bind.
            value (str | int | float | bool | list):
                The value to bind the variable to. Must be a JSON serializable type.
            **kwargs (Any):
                Additional keyword arguments to bind to the prompt. This can be used to bind multiple variables at once.

        Returns:
            Prompt:
                The prompt with the context bound.
        """

    @property
    def response_json_schema(self) -> Optional[str]:
        """The JSON schema for the response if provided."""

    def __str__(self): ...

class Provider:
    OpenAI: "Provider"
    Gemini: "Provider"

class TaskStatus:
    Pending: "TaskStatus"
    Running: "TaskStatus"
    Completed: "TaskStatus"
    Failed: "TaskStatus"

class ResponseLogProbs:
    @property
    def token(self) -> str:
        """The token for which the log probabilities are calculated."""

    @property
    def logprob(self) -> float:
        """The log probability of the token."""

class LogProbs:
    @property
    def tokens(self) -> List[ResponseLogProbs]:
        """The log probabilities of the tokens in the response.
        This is primarily used for debugging and analysis purposes.
        """

    def __str__(self) -> str:
        """String representation of the log probabilities."""

class AgentResponse:
    @property
    def id(self) -> str:
        """The ID of the agent response."""

    @property
    def result(self) -> Any:
        """The result of the agent response. This can be a Pydantic BaseModel class or a supported potato_head response type such as `Score`.
        If neither is provided, the response json will be returned as a dictionary.
        """

    @property
    def token_usage(self) -> Usage:
        """Returns the token usage of the agent response if supported"""

    @property
    def log_probs(self) -> List["ResponseLogProbs"]:
        """Returns the log probabilities of the agent response if supported.
        This is primarily used for debugging and analysis purposes.
        """

class Task:
    def __init__(
        self,
        agent_id: str,
        prompt: Prompt,
        dependencies: List[str] = [],
        id: Optional[str] = None,
    ) -> None:
        """Create a Task object.

        Args:
            agent_id (str):
                The ID of the agent that will execute the task.
            prompt (Prompt):
                The prompt to use for the task.
            dependencies (List[str]):
                The dependencies of the task.
            id (Optional[str]):
                The ID of the task. If None, a random uuid7 will be generated.
        """

    @property
    def prompt(self) -> Prompt:
        """The prompt to use for the task."""

    @property
    def dependencies(self) -> List[str]:
        """The dependencies of the task."""

    @property
    def id(self) -> str:
        """The ID of the task."""

    @property
    def status(self) -> TaskStatus:
        """The status of the task."""

class TaskList:
    def __init__(self) -> None:
        """Create a TaskList object."""

class Agent:
    def __init__(
        self,
        provider: Provider | str,
        system_instruction: Optional[str | List[str] | Message | List[Message]] = None,
    ) -> None:
        """Create an Agent object.

        Args:
            provider (Provider | str):
                The provider to use for the agent. This can be a Provider enum or a string
                representing the provider.
            system_instruction (Optional[str | List[str] | Message | List[Message]]):
                The system message to use for the agent. This can be a string, a list of strings,
                a Message object, or a list of Message objects. If None, no system message will be used.
                This is added to all tasks that the agent executes. If a given task contains it's own
                system message, the agent's system message will be prepended to the task's system message.

        Example:
        ```python
            agent = Agent(
                provider=Provider.OpenAI,
                system_instruction="You are a helpful assistant.",
            )
        ```
        """

    @property
    def system_instruction(self) -> List[Message]:
        """The system message to use for the agent. This is a list of Message objects."""

    def execute_task(
        self,
        task: Task,
        output_type: Optional[Any] = None,
        model: Optional[str] = None,
    ) -> AgentResponse:
        """Execute a task.

        Args:
            task (Task):
                The task to execute.
            output_type (Optional[Any]):
                The output type to use for the task. This can either be a Pydantic `BaseModel` class
                or a supported PotatoHead response type such as `Score`.
            model (Optional[str]):
                The model to use for the task. If not provided, defaults to the `model` provided within
                the Task's prompt. If the Task's prompt does not have a model, an error will be raised.

        Returns:
            AgentResponse:
                The response from the agent after executing the task.
        """

    def execute_prompt(
        self,
        prompt: Prompt,
        output_type: Optional[Any] = None,
        model: Optional[str] = None,
    ) -> AgentResponse:
        """Execute a prompt.

        Args:
            prompt (Prompt):`
                The prompt to execute.
            output_type (Optional[Any]):
                The output type to use for the task. This can either be a Pydantic `BaseModel` class
                or a supported potato_head response type such as `Score`.
            model (Optional[str]):
                The model to use for the task. If not provided, defaults to the `model` provided within
                the Prompt. If the Prompt does not have a model, an error will be raised.

        Returns:
            AgentResponse:
                The response from the agent after executing the task.
        """

    @property
    def id(self) -> str:
        """The ID of the agent. This is a random uuid7 that is generated when the agent is created."""

class Workflow:
    def __init__(self, name: str) -> None:
        """Create a Workflow object.

        Args:
            name (str):
                The name of the workflow.
        """

    @property
    def name(self) -> str:
        """The name of the workflow."""

    @property
    def task_list(self) -> TaskList:
        """The tasks in the workflow."""

    @property
    def agents(self) -> Dict[str, Agent]:
        """The agents in the workflow."""

    @property
    def is_workflow(self) -> bool:
        """Returns True if the workflow is a valid workflow, otherwise False.
        This is used to determine if the workflow can be executed.
        """

    def __workflow__(self) -> str:
        """Returns a string representation of the workflow."""

    def add_task_output_types(self, task_output_types: Dict[str, Any]) -> None:
        """Add output types for tasks in the workflow. This is primarily used for
        when loading a workflow as python objects are not serializable.

        Args:
            task_output_types (Dict[str, Any]):
                A dictionary mapping task IDs to their output types.
                This can either be a Pydantic `BaseModel` class or a supported potato_head response type such as `Score`.
        """

    def add_task(self, task: Task, output_type: Optional[Any]) -> None:
        """Add a task to the workflow.

        Args:
            task (Task):
                The task to add to the workflow.
            output_type (Optional[Any]):
                The output type to use for the task. This can either be a Pydantic `BaseModel` class
                or a supported potato_head response type such as `Score`.
        """

    def add_tasks(self, tasks: List[Task]) -> None:
        """Add multiple tasks to the workflow.

        Args:
            tasks (List[Task]):
                The tasks to add to the workflow.
        """

    def add_agent(self, agent: Agent) -> None:
        """Add an agent to the workflow.

        Args:
            agent (Agent):
                The agent to add to the workflow.
        """

    def is_complete(self) -> bool:
        """Check if the workflow is complete.

        Returns:
            bool:
                True if the workflow is complete, False otherwise.
        """

    def pending_count(self) -> int:
        """Get the number of pending tasks in the workflow.

        Returns:
            int:
                The number of pending tasks in the workflow.
        """

    def execution_plan(self) -> Dict[str, List[str]]:
        """Get the execution plan for the workflow.

        Returns:
            Dict[str, List[str]]:
                A dictionary where the keys are task IDs and the values are lists of task IDs
                that the task depends on.
        """

    def run(
        self,
        global_context: Optional[Dict[str, Any]] = None,
    ) -> WorkflowResult:
        """Run the workflow. This will execute all tasks in the workflow and return when all tasks are complete.

        Args:
            global_context (Optional[Dict[str, Any]]):
                A dictionary of global context to bind to the workflow.
                All tasks in the workflow will have this context bound to them.
        """

    def model_dump_json(self) -> str:
        """Dump the workflow to a JSON string.

        Returns:
            str:
                The JSON string.
        """

    @staticmethod
    def model_validate_json(json_string: str, output_types: Optional[Dict[str, Any]]) -> "Workflow":
        """Load a workflow from a JSON string.

        Args:
            json_string (str):
                The JSON string to validate.
            output_types (Optional[Dict[str, Any]]):
                A dictionary mapping task IDs to their output types.
                This can either be a Pydantic `BaseModel` class or a supported potato_head response type such as `Score`.

        Returns:
            Workflow:
                The workflow object.
        """

class PyTask:
    """Python-specific task interface for Task objects and results"""

    @property
    def prompt(self) -> Prompt:
        """The prompt to use for the task."""

    @property
    def dependencies(self) -> List[str]:
        """The dependencies of the task."""

    @property
    def id(self) -> str:
        """The ID of the task."""

    @property
    def agent_id(self) -> str:
        """The ID of the agent that will execute the task."""

    @property
    def status(self) -> TaskStatus:
        """The status of the task."""

    @property
    def result(self) -> Optional[AgentResponse]:
        """The result of the task if it has been executed, otherwise None."""

    def __str__(self) -> str: ...

class ChatResponse:
    def to_py(self) -> Any:
        """Convert the ChatResponse to it's Python representation."""

    def __str__(self) -> str:
        """Return a string representation of the ChatResponse."""

class EventDetails:
    @property
    def prompt(self) -> Optional[Prompt]:
        """The prompt used for the task."""

    @property
    def response(self) -> Optional[ChatResponse]:
        """The response from the agent after executing the task."""

    @property
    def duration(self) -> Optional[datetime.timedelta]:
        """The duration of the task execution."""

    @property
    def start_time(self) -> Optional[datetime.datetime]:
        """The start time of the task execution."""

    @property
    def end_time(self) -> Optional[datetime.datetime]:
        """The end time of the task execution."""

    @property
    def error(self) -> Optional[str]:
        """The error message if the task failed, otherwise None."""

class TaskEvent:
    @property
    def id(self) -> str:
        """The ID of the event"""

    @property
    def workflow_id(self) -> str:
        """The ID of the workflow that the task is part of."""

    @property
    def task_id(self) -> str:
        """The ID of the task that the event is associated with."""

    @property
    def status(self) -> TaskStatus:
        """The status of the task at the time of the event."""

    @property
    def timestamp(self) -> datetime.datetime:
        """The timestamp of the event. This is the time when the event occurred."""

    @property
    def updated_at(self) -> datetime.datetime:
        """The timestamp of when the event was last updated. This is useful for tracking changes to the event."""

    @property
    def details(self) -> EventDetails:
        """Additional details about the event. This can include information such as error messages or other relevant data."""

class WorkflowResult:
    @property
    def tasks(self) -> Dict[str, PyTask]:
        """The tasks in the workflow result."""

    @property
    def events(self) -> List[TaskEvent]:
        """The events that occurred during the workflow execution. This is a list of dictionaries
        where each dictionary contains information about the event such as the task ID, status, and timestamp.
        """

class Score:
    """A class representing a score with a score value and a reason. This is typically used
    as a response type for tasks/prompts that require scoring or evaluation of results.

    Example:
    ```python
        Prompt(
            model="openai:gpt-4o",
            message="What is the score of this response?",
            system_instruction="system_prompt",
            response_format=Score,
        )
    ```
    """

    @property
    def score(self) -> int:
        """The score value."""

    @property
    def reason(self) -> str:
        """The reason for the score."""

    @staticmethod
    def model_validate_json(json_string: str) -> "Score":
        """Validate the score JSON.

        Args:
            json_string (str):
                The JSON string to validate.

        Returns:
            Score:
                The score object.
        """

    def __str__(self): ...
