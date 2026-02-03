# AUTO-GENERATED STUB FILE. DO NOT EDIT.
# pylint: disable=redefined-builtin, invalid-name, dangerous-default-value
### header.pyi ###
# pylint: disable=redefined-builtin, invalid-name, dangerous-default-value, missing-final-newline

import datetime
from pathlib import Path
from types import TracebackType
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    List,
    Literal,
    Optional,
    ParamSpec,
    Protocol,
    Sequence,
    Tuple,
    Type,
    TypeAlias,
    Union,
    overload,
)

from typing_extensions import TypeVar

SerializedType: TypeAlias = Union[str, int, float, dict, list]
Context: TypeAlias = Union[Dict[str, Any], "BaseModel"]

P = ParamSpec("P")
R = TypeVar("R")

class BaseModel(Protocol):
    """Protocol for pydantic BaseModel to ensure compatibility with context"""

    def model_dump(self) -> Dict[str, Any]:
        """Dump the model as a dictionary"""

    def model_dump_json(self) -> str:
        """Dump the model as a JSON string"""

    def __str__(self) -> str:
        """String representation of the model"""

### logging.pyi ###
class LogLevel:
    Debug: "LogLevel"
    Info: "LogLevel"
    Warn: "LogLevel"
    Error: "LogLevel"
    Trace: "LogLevel"

class WriteLevel:
    Stdout: "WriteLevel"
    Stderror: "WriteLevel"

class LoggingConfig:
    show_threads: bool
    log_level: LogLevel
    write_level: WriteLevel
    use_json: bool

    def __init__(
        self,
        show_threads: bool = True,
        log_level: LogLevel = LogLevel.Info,
        write_level: WriteLevel = WriteLevel.Stdout,
        use_json: bool = False,
    ) -> None:
        """
        Logging configuration options.

        Args:
            show_threads:
                Whether to include thread information in log messages.
                Default is True.

            log_level:
                Log level for the logger.
                Default is LogLevel.Info.

            write_level:
                Write level for the logger.
                Default is WriteLevel.Stdout.

            use_json:
                Whether to write log messages in JSON format.
                Default is False.
        """

    @staticmethod
    def json_default() -> "LoggingConfig":
        """Gets a default JSON configuration.

        show_threads: True
        log_level: Env or LogLevel.Info
        write_level: WriteLevel.Stdout
        use_json: True

        Returns:
            LoggingConfig:
                The default JSON configuration.
        """

    @staticmethod
    def default() -> "LoggingConfig":
        """Gets a default configuration.

        show_threads: True
        log_level: Env or LogLevel.Info
        write_level: WriteLevel.Stdout
        use_json: False

        Returns:
            LoggingConfig:
                The default JSON configuration.
        """

class RustyLogger:
    """The Rusty Logger class to use with your python and rust-backed projects."""

    @staticmethod
    def setup_logging(config: Optional[LoggingConfig] = None) -> None:
        """Sets up the logger with the given configuration.

        Args:
            config (LoggingConfig):
                The configuration to use for the logger.
        """

    @staticmethod
    def get_logger(config: Optional[LoggingConfig] = None) -> "RustyLogger":
        """Gets the logger instance.

        Args:
            config (LoggingConfig):
                The configuration to use for the logger.

        Returns:
            RustyLogger:
                The logger instance.
        """

    def debug(self, message: str, *args) -> None:
        """Logs a debug message.

        Args:
            message (str):
                The message to log.

            *args:
                Additional arguments to log.
        """

    def info(self, message: str, *args) -> None:
        """Logs an info message.

        Args:
            message (str):
                The message to log.

            *args:
                Additional arguments to log.
        """

    def warn(self, message: str, *args) -> None:
        """Logs a warning message.

        Args:
            message (str):
                The message to log.

            *args:
                Additional arguments to log.
        """

    def error(self, message: str, *args) -> None:
        """Logs an error message.

        Args:
            message (str):
                The message to log.

            *args:
                Additional arguments to log.
        """

    def trace(self, message: str, *args) -> None:
        """Logs a trace message.

        Args:
            message (str):
                The message to log.

            *args:
                Additional arguments to log.
        """

### potato.pyi ###
class Provider:
    """Provider enumeration for LLM services.

    Specifies which LLM provider to use for prompts, agents, and workflows.

    Examples:
        >>> provider = Provider.OpenAI
        >>> agent = Agent(provider=provider)
    """

    OpenAI: "Provider"
    """OpenAI provider"""

    Gemini: "Provider"
    """Google Gemini provider"""

    Vertex: "Provider"
    """Google Vertex AI provider"""

    Google: "Provider"
    """Google provider (alias for Gemini)"""

    Anthropic: "Provider"
    """Anthropic provider"""

    Undefined: "Provider"
    """Undefined provider"""

class Role:
    """Message role in conversation.

    Indicates the role of a message sender in a conversation.

    Examples:
        >>> role = Role.User
        >>> role.as_str()
        'user'
    """

    User: "Role"
    """User role"""

    Assistant: "Role"
    """Assistant role"""

    Developer: "Role"
    """Developer/system role"""

    Tool: "Role"
    """Tool role"""

    Model: "Role"
    """Model role"""

    System: "Role"
    """System role"""

    def as_str(self) -> str:
        """Return string representation of role."""

class ResponseType:
    """Type of structured response.

    Indicates the expected response format for structured outputs.

    Examples:
        >>> response_type = ResponseType.Score
        >>> response_type = ResponseType.Pydantic
    """

    Score: "ResponseType"
    """Score response type"""

    Pydantic: "ResponseType"
    """Pydantic BaseModel response type"""

    Null: "ResponseType"
    """No structured response type"""

class TaskStatus:
    """Status of a task in a workflow.

    Indicates the current state of task execution.

    Examples:
        >>> status = TaskStatus.Pending
        >>> status = TaskStatus.Completed
    """

    Pending: "TaskStatus"
    """Task is pending execution"""

    Running: "TaskStatus"
    """Task is currently running"""

    Completed: "TaskStatus"
    """Task has completed successfully"""

    Failed: "TaskStatus"
    """Task has failed"""

T = TypeVar("T", "OpenAIChatSettings", "GeminiSettings", "AnthropicSettings")

class ModelSettings(Generic[T]):
    """Configuration settings for LLM models.

    Unified interface for provider-specific model settings.

    Examples:
        >>> from potato_head.openai import OpenAIChatSettings
        >>> settings = OpenAIChatSettings(temperature=0.7, max_tokens=1000)
        >>> model_settings = ModelSettings(settings)
        >>>
        >>> # Or extract from existing settings
        >>> openai_settings = model_settings.settings
    """

    @overload
    def __init__(self, settings: "OpenAIChatSettings") -> None:
        """Initialize with OpenAI settings.

        Args:
            settings: OpenAI chat completion settings
        """

    @overload
    def __init__(self, settings: "GeminiSettings") -> None:
        """Initialize with Gemini settings.

        Args:
            settings: Gemini/Google AI settings
        """

    @overload
    def __init__(self, settings: "AnthropicSettings") -> None:
        """Initialize with Anthropic settings.

        Args:
            settings: Anthropic Claude settings
        """

    @property
    def settings(self) -> T:
        """Provider-specific settings object."""

    def model_dump_json(self) -> str:
        """Serialize settings to JSON string."""

    def model_dump(self) -> Dict[str, Any]:
        """Serialize settings to dictionary."""

    def settings_type(self) -> Any:
        """Return the settings type."""

    def __str__(self) -> str:
        """String representation."""

class Score:
    """A class representing a score with a score value and a reason. This is typically used
    as a response type for tasks/prompts that require scoring or evaluation of results.

    Example:
    ```python
        Prompt(
            model="openai:gpt-4o",
            messages="What is the score of this response?",
            system_instructions="system_prompt",
            output_type=Score,
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

PromptMessage: TypeAlias = Union[
    str,
    "ChatMessage",
    "MessageParam",
    "GeminiContent",
    List[Union[str, "ChatMessage", "MessageParam", "GeminiContent"]],
]

OutputType = TypeVar("OutputType")

class Prompt(Generic[OutputType]):
    """Prompt for interacting with an LLM API.

    The Prompt class handles message parsing, provider-specific formatting, and
    structured output configuration for LLM interactions.
    """

    def __init__(
        self,
        messages: PromptMessage,
        model: str,
        provider: Provider | str,
        system_instructions: Optional[PromptMessage] = None,
        model_settings: Optional[ModelSettings | OpenAIChatSettings | GeminiSettings | AnthropicSettings] = None,
        output_type: Optional[Type[OutputType]] = None,
    ) -> None:
        """Initialize a Prompt object.

        Main parsing logic:
        1. Extract model settings if provided, otherwise use provider default settings
        2. Messages and system instructions are parsed into provider-specific formats
           (OpenAIChatMessage, AnthropicMessage, or GeminiContent)
        3. String messages are automatically converted to appropriate message types based on provider
        4. Lists of messages are parsed with each item checked and converted accordingly
        5. After parsing, a complete provider request structure is built

        Args:
            message (PromptMessage):
                The user message(s) to use in the prompt
            model (str):
                The model identifier to use (e.g., "gpt-4o", "claude-3-5-sonnet-20241022")
            provider (Provider | str):
                The provider to use for the prompt (e.g., "openai", "anthropic", "google")
            system_instruction (Optional[PromptMessage]):
                Optional system instruction(s). Can be:
            model_settings (Optional[ModelSettings | OpenAIChatSettings | GeminiSettings | AnthropicSettings]):
                Optional model-specific settings (temperature, max_tokens, etc.)
                If None, provider default settings will be used
            output_type (Optional[OutputT]):
                Optional structured output type.The provided format will be parsed into a JSON schema for structured outputs.
                This is typically a pydantic BaseModel.

        Raises:
            TypeError: If message types are invalid or incompatible with the provider
        """

    @property
    def model(self) -> str:
        """The model identifier to use for the prompt (e.g., "gpt-4o")."""

    @property
    def provider(self) -> Provider:
        """The provider to use for the prompt (e.g., Provider.OpenAI)."""

    @property
    def model_identifier(self) -> str:
        """Concatenation of provider and model for identifying the model.

        This is commonly used with frameworks like pydantic_ai to identify
        which model to use for an agent.

        Returns:
            str: Format is "{provider}:{model}" (e.g., "openai:gpt-4o")

        Example:
            ```python
            prompt = Prompt(
                model="gpt-4o",
                messages="My prompt variable is ${variable}",
                system_instructions="You are a helpful assistant",
                provider="openai",
            )

            # Use with pydantic_ai
            agent = Agent(
                prompt.model_identifier,  # "openai:gpt-4o"
                system_prompt=prompt.system_instructions[0].content,
            )
            ```
        """

    @property
    def model_settings(self) -> ModelSettings:
        """The model settings used for the prompt.

        Returns the provider-specific settings (OpenAIChatSettings, GeminiSettings,
        or AnthropicSettings) wrapped in a ModelSettings union type.
        """

    @property
    def all_messages(self) -> List["ChatMessage" | "MessageParam" | "GeminiContent"]:
        """All messages in the prompt, including system instructions, user messages, tools, etc.
        This is helpful for accessing the complete set of messages in the prompt.
        """

    @property
    def messages(self) -> List["ChatMessage" | "MessageParam" | "GeminiContent"]:
        """The user message(s) in the prompt.

        Returns a list of provider-specific message objects that were parsed
        from the input during initialization.
        """

    @property
    def message(self) -> "ChatMessage" | "MessageParam" | "GeminiContent":
        """The last user message in the prompt.

        Returns a list of provider-specific message objects that were parsed
        from the input during initialization.
        """

    @property
    def openai_messages(self) -> List[ChatMessage]:
        """The user messages as OpenAI ChatMessage objects.
        Returns the user messages converted to OpenAI ChatMessage format.
        Raises:
            TypeError: If the provider is not OpenAI
        """

    @property
    def openai_message(self) -> ChatMessage:
        """The last user message as an OpenAI ChatMessage object.
        Returns the last user message converted to OpenAI ChatMessage format.
        Raises:
            TypeError: If the provider is not OpenAI
        """

    @property
    def anthropic_messages(self) -> List[MessageParam]:
        """The user messages as Anthropic MessageParam objects.
        Returns the user messages converted to Anthropic MessageParam format.
        Raises:
            TypeError: If the provider is not Anthropic
        """

    @property
    def anthropic_message(self) -> MessageParam:
        """The last user message as an Anthropic MessageParam object.
        Returns the last user message converted to Anthropic MessageParam format.
        Raises:
            TypeError: If the provider is not Anthropic
        """

    @property
    def gemini_messages(self) -> List[GeminiContent]:
        """The user messages as Google GeminiContent objects.
        Returns the user messages converted to Google GeminiContent format.
        Raises:
            TypeError: If the provider is not Google/Gemini
        """

    @property
    def gemini_message(self) -> GeminiContent:
        """The last user message as a Google GeminiContent object.
        Returns the last user message converted to Google GeminiContent format.
        Raises:
            TypeError: If the provider is not Google/Gemini
        """

    @property
    def system_instructions(
        self,
    ) -> List["ChatMessage" | "GeminiContent" | "MessageParam"]:
        """The system instruction message(s) in the prompt.

        Returns a list of provider-specific message objects for system instructions.
        Returns an empty list if no system instructions were provided.
        """

    @property
    def parameters(self) -> List[str]:
        """Extracted named parameters from the prompt messages.

        Returns a list of all variable placeholders found in the prompt using
        the ${variable_name} syntax. These can be bound to values using the
        bind() or bind_mut() methods.

        Example:
            ```python
            prompt = Prompt(
                messages="Hello ${name}, your score is ${score}",
                model="gpt-4o",
                provider="openai",
            )
            print(prompt.parameters)  # ["name", "score"]
            ```
        """

    def save_prompt(self, path: Optional[Path] = None) -> Path:
        """Save the prompt to a JSON file.

        Args:
            path (Optional[Path]):
                The path to save the prompt to. If None, saves to the current
                working directory with default filename "prompt.json".

        Returns:
            Path: The path where the prompt was saved.

        Example:
            ```python
            prompt = Prompt(messages="Hello!", model="gpt-4o", provider="openai")
            saved_path = prompt.save_prompt(Path("my_prompt.json"))
            ```
        """

    @staticmethod
    def from_path(path: Path) -> "Prompt":
        """Load a prompt from a JSON file.

        Args:
            path (Path):
                The path to the prompt JSON file.

        Returns:
            Prompt: The loaded prompt object.

        Raises:
            IOError: If the file cannot be read
            ValueError: If the JSON is invalid or cannot be parsed into a Prompt

        Example:
            ```python
            prompt = Prompt.from_path(Path("my_prompt.json"))
            ```
        """

    @staticmethod
    def model_validate_json(json_string: str) -> "Prompt":
        """Validate and parse a Prompt from a JSON string.

        Args:
            json_string (str):
                A JSON string representation of a Prompt object.

        Returns:
            Prompt:
                The parsed Prompt object.

        Raises:
            ValueError: If the JSON is invalid or cannot be parsed into a Prompt

        Example:
            ```python
            json_str = '{"model": "gpt-4o", "provider": "openai", ...}'
            prompt = Prompt.model_validate_json(json_str)
            ```
        """

    def model_dump(self) -> Dict[str, Any]:
        """Returns the Prompt request object as a dictionary.
        For instance, if Provider is OpenAI, this will return the OpenAIChatRequest as a dict
        that can be passed to the OpenAI SDK.
        """

    def model_dump_json(self) -> str:
        """Serialize the Prompt to a JSON string.

        Returns:
            str: JSON string representation of the Prompt.

        Example:
            ```python
            prompt = Prompt(messages="Hello!", model="gpt-4o", provider="openai")
            json_str = prompt.model_dump_json()
            ```
        """

    def bind(
        self,
        name: Optional[str] = None,
        value: Optional[str | int | float | bool | list] = None,
        **kwargs: Any,
    ) -> "Prompt":
        """Bind variables in the prompt (immutable operation).

        Creates a new Prompt object with variables bound to values. This iterates
        over all user messages and replaces ${variable_name} placeholders with
        the provided values.

        Args:
            name (Optional[str]):
                The name of a single variable to bind (without ${} syntax)
            value (Optional[str | int | float | bool | list]):
                The value to bind the variable to. Must be JSON serializable.
            **kwargs:
                Additional variables to bind. Keys are variable names,
                values are the values to bind.

        Returns:
            Prompt: A new Prompt object with variables bound.

        Raises:
            TypeError: If no binding arguments are provided or if values are not
                JSON serializable.

        Example:
            ```python
            prompt = Prompt(
                messages="Hello ${name}, you scored ${score}/100",
                model="gpt-4o",
                provider="openai",
            )

            # Single variable binding
            bound = prompt.bind("name", "Alice")

            # Multiple variable binding
            bound = prompt.bind(name="Alice", score=95)

            # Original prompt is unchanged
            print(prompt.parameters)  # ["name", "score"]
            print(bound.parameters)   # []
            ```
        """

    def bind_mut(
        self,
        name: Optional[str] = None,
        value: Optional[str | int | float | bool | list] = None,
        **kwargs: Any,
    ) -> None:
        """Bind variables in the prompt (mutable operation).

        Modifies the current Prompt object by binding variables to values. This
        iterates over all user messages and replaces ${variable_name} placeholders
        with the provided values.

        Args:
            name (Optional[str]):
                The name of a single variable to bind (without ${} syntax)
            value (Optional[str | int | float | bool | list]):
                The value to bind the variable to. Must be JSON serializable.
            **kwargs:
                Additional variables to bind. Keys are variable names,
                values are the values to bind.

        Raises:
            TypeError: If no binding arguments are provided or if values are not
                JSON serializable.

        Example:
            ```python
            prompt = Prompt(
                messages="Hello ${name}, you scored ${score}/100",
                model="gpt-4o",
                provider="openai",
            )

            # Mutate in place
            prompt.bind_mut(name="Bob", score=87)

            # Prompt is now modified
            print(prompt.parameters)  # []
            ```
        """

    @property
    def response_json_schema(self) -> Optional[str]:
        """The JSON schema for structured output responses if provided.

        Returns the raw JSON schema string that was generated from the response_format
        parameter during initialization. Returns None if no response format was specified.
        """

    @property
    def response_json_schema_pretty(self) -> Optional[str]:
        """The pretty-printed JSON schema for structured output responses if provided."""

    def __str__(self) -> str:
        """Return a string representation of the Prompt."""

class EventDetails:
    @property
    def prompt(self) -> Optional[Prompt]:
        """The prompt used for the task."""

    @property
    def response(self) -> Optional[Any]:
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
    """A class representing an event that occurs during the execution of a task in a workflow."""

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

class WorkflowTask:
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
    def result(self) -> Optional[Any]:
        """The result of the task if it has been executed, otherwise None."""

    def __str__(self) -> str: ...

class WorkflowResult:
    @property
    def tasks(self) -> Dict[str, WorkflowTask]:
        """The tasks in the workflow result."""

    @property
    def events(self) -> List[TaskEvent]:
        """The events that occurred during the workflow execution. This is a list of dictionaries
        where each dictionary contains information about the event such as the task ID, status, and timestamp.
        """

    @property
    def result(self) -> Optional[Any]:
        """The result from the last task of the workflow if it has been executed, otherwise None."""

class TokenLogProbs:
    @property
    def token(self) -> str:
        """The token for which the log probabilities are calculated."""

    @property
    def logprob(self) -> float:
        """The log probability of the token."""

class ResponseLogProbs:
    @property
    def tokens(self) -> List[TokenLogProbs]:
        """The log probabilities of the tokens in the response.
        This is primarily used for debugging and analysis purposes.
        """

    def __str__(self) -> str:
        """String representation of the log probabilities."""

_ResponseType: TypeAlias = Union[
    "OpenAIChatResponse",
    "GenerateContentResponse",
    "AnthropicMessageResponse",
]

OutT = TypeVar(
    "OutT",
    default=str,
)
RespT = TypeVar("RespT", default=_ResponseType)

class AgentResponse(Generic[OutT, RespT]):
    """Agent response generic over OutputDataT.

    The structured_output property returns OutputDataT type.

    Examples:
        >>> agent = Agent(provider=Provider.OpenAI)
        >>> response: AgentResponse[WeatherData] = agent.execute_prompt(prompt, output_type=WeatherData)
        >>> weather: WeatherData = response.structured_output
    """

    @property
    def id(self) -> str:
        """The ID of the agent response."""

    @property
    def response(self) -> RespT:
        """The response of the agent."""

    @property
    def token_usage(self) -> Any:
        """Returns the token usage of the agent response if supported"""

    @property
    def log_probs(self) -> ResponseLogProbs:
        """Returns the log probabilities of the agent response if supported."""

    @property
    def structured_output(self) -> OutT:
        """Returns the structured output of the agent response.

        The type is determined by the Agent's OutputType generic parameter
        or the output_type argument passed to execute_task/execute_prompt.
        """

    def response_text(self) -> str:
        """The response text from the agent if available, otherwise an empty string."""

class Task:
    def __init__(
        self,
        agent_id: str,
        prompt: Prompt[OutputType],
        id: Optional[str] = None,
        dependencies: List[str] = [],
        max_retries: int = 3,
    ) -> None:
        """Create a Task object.

        Args:
            agent_id (str):
                The ID of the agent that will execute the task.
            prompt (Prompt[OutputType]):
                The prompt to use for the task.
            id (Optional[str]):
                The ID of the task. If None, a random uuid7 will be generated.
            dependencies (List[str]):
                The dependencies of the task.
            max_retries (int):
                The maximum number of retries for the task if it fails. Defaults to 3.
        """

    def add_dependency(self, task_id: str) -> None:
        """Add a dependency to the task."""

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
    """TaskList is a collection of Task objects used in a Workflow."""

    @property
    def items(self) -> Dict[str, Task]:
        """Dictionary of tasks in the TaskList where keys are task IDs and values are Task objects."""

class Agent:
    """Create an Agent object.

    Generic over OutputType which determines the structured output type.
    By default, OutputType is str if no output_type is specified.

    Examples:
        >>> # Default agent (OutputType = str)
        >>> agent = Agent(provider=Provider.OpenAI)
        >>> response = agent.execute_prompt(prompt)
        >>> text: str = response.structured_output

        >>> # Typed agent with Pydantic model
        >>> class WeatherData(BaseModel):
        ...     temperature: float
        ...     condition: str
        >>>
        >>> agent = Agent(provider=Provider.OpenAI)
        >>> response = agent.execute_prompt(prompt, output_type=WeatherData)
        >>> weather: WeatherData = response.structured_output
    """

    def __init__(
        self,
        provider: Provider | str,
        system_instruction: Optional[PromptMessage] = None,
    ) -> None:
        """Create an Agent object.

        Args:
            provider (Provider | str):
                The provider to use for the agent.
            system_instruction (Optional[PromptMessage]):
                The system message to use for the agent.
        """

    @property
    def system_instruction(self) -> List[Any]:
        """The system message to use for the agent."""

    def execute_task(
        self,
        task: Task,
        output_type: type[OutT] | None = None,
    ) -> AgentResponse[OutT, _ResponseType]:
        """Execute a task.

        Args:
            task (Task):
                The task to execute.
            output_type (Optional[OutT]):
                The output type to use for the task.

        Returns:
            AgentResponse[OutT, _ResponseType]:
                The response from the agent. For type-safe response access,
                annotate the return value with the specific response type.
        """

    def execute_prompt(
        self,
        prompt: Prompt,
        output_type: type[OutT] | None = None,
    ) -> AgentResponse[OutT, _ResponseType]:
        """Execute a prompt.

        Args:
            prompt (Prompt):
                The prompt to execute.
            output_type (Optional[OutT]):
                The output type to use for the task.

        Returns:
            AgentResponse[OutT, _ResponseType]:
                The response from the agent. For type-safe response access,
                annotate the return value with the specific response type.
        """

    @property
    def id(self) -> str:
        """The ID of the agent."""

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
        rehydrating the task output types when loading a workflow from JSON,
        as python objects are not serializable.

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

    def add_agents(self, agents: List[Agent]) -> None:
        """Add multiple agents to the workflow."""

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
    ) -> "WorkflowResult":
        """Run the workflow. This will execute all tasks in the workflow and return when all tasks are complete.

        Args:
            global_context (Optional[Dict[str, Any]]):
                A dictionary of global context to bind to the workflow.
                All tasks in the workflow will have this context bound to them.
        """

    def execute_task(
        self,
        task_id: str,
        global_context: Optional[Any] = None,
    ) -> Any:
        """Execute a single task in the workflow by its ID.

        Args:
            task_id (str):
                The ID of the task to execute.
            global_context (Optional[Any]):
                Any serializable global context to bind to the task before execution.
                This is typically a dictionary or Pydantic BaseModel.
        Returns:
            Any:
        """

    def model_dump_json(self) -> str:
        """Dump the workflow to a JSON string.

        Returns:
            str:
                The JSON string.
        """

    @staticmethod
    def model_validate_json(
        json_string: str,
        output_types: Optional[Dict[str, Any]] = None,
    ) -> "Workflow":
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

class Embedder:
    """Class for creating embeddings."""

    def __init__(  # type: ignore
        self,
        provider: Provider | str,
        config: Optional[OpenAIEmbeddingConfig | GeminiEmbeddingConfig] = None,
    ) -> None:
        """Create an Embedder object.

        Args:
            provider (Provider | str):
                The provider to use for the embedder. This can be a Provider enum or a string
                representing the provider.
            config (Optional[OpenAIEmbeddingConfig | GeminiEmbeddingConfig]):
                The configuration to use for the embedder. This can be a Pydantic BaseModel class
                representing the configuration for the provider. If no config is provided,
                defaults to OpenAI provider configuration.
        """

    def embed(
        self,
        input: str | List[str] | PredictRequest,
    ) -> OpenAIEmbeddingResponse | GeminiEmbeddingResponse | PredictResponse:
        """Create embeddings for input.

        Args:
            input: The input to embed. Type depends on provider:
                - OpenAI/Gemini: str | List[str]
                - Vertex: PredictRequest

        Returns:
            Provider-specific response type.
            OpenAIEmbeddingResponse for OpenAI,
            GeminiEmbeddingResponse for Gemini,
            PredictResponse for Vertex.

        Examples:
            ```python
            ## OpenAI
            embedder = Embedder(Provider.OpenAI)
            response = embedder.embed(input="Test input")

            ## Gemini
            embedder = Embedder(Provider.Gemini, config=GeminiEmbeddingConfig(model="gemini-embedding-001"))
            response = embedder.embed(input="Test input")

            ## Vertex
            from potato_head.google import PredictRequest
            embedder = Embedder(Provider.Vertex)
            response = embedder.embed(input=PredictRequest(text="Test input"))
            ```
        """

###### __potatohead__.openai module ######

# ============================================================================
# Settings Types
# ============================================================================

class AudioParam:
    """Audio output configuration for OpenAI chat completions.

    This class provides configuration for audio output in chat completions,
    including format and voice selection for text-to-speech capabilities.

    Examples:
        >>> audio = AudioParam(format="mp3", voice="alloy")
        >>> audio.format
        'mp3'
        >>> audio.voice
        'alloy'
    """

    def __init__(
        self,
        format: str,
        voice: str,
    ) -> None:
        """Initialize audio output parameters.

        Args:
            format (str):
                Audio output format (e.g., "mp3", "opus", "aac", "flac", "wav", "pcm")
            voice (str):
                Voice to use for text-to-speech (e.g., "alloy", "echo", "fable",
                "onyx", "nova", "shimmer")
        """

    @property
    def format(self) -> str:
        """The audio output format."""

    @property
    def voice(self) -> str:
        """The voice to use for text-to-speech."""

    def model_dump(self) -> Dict[str, Any]:
        """Convert audio parameters to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation of audio parameters
        """

class PredictionContentPart:
    """Content part for predicted outputs in OpenAI requests.

    This class represents a single content part within a predicted output,
    used to improve response times when large parts of the response are known.

    Examples:
        >>> part = PredictionContentPart(type="text", text="Hello, world!")
        >>> part.type
        'text'
        >>> part.text
        'Hello, world!'
    """

    def __init__(
        self,
        type: str,
        text: str,
    ) -> None:
        """Initialize prediction content part.

        Args:
            type (str):
                Type of content (typically "text")
            text (str):
                The predicted text content
        """

    @property
    def type(self) -> str:
        """The content type."""

    @property
    def text(self) -> str:
        """The predicted text content."""

    def model_dump(self) -> Dict[str, Any]:
        """Convert content part to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation of content part
        """

class Content:
    """Content for predicted outputs, supporting text or structured parts.

    This class represents the content of a predicted output, which can be
    either a simple text string or an array of structured content parts.

    Examples:
        >>> # Text content
        >>> content = Content(text="Predicted response")
        >>>
        >>> # Structured content
        >>> parts = [PredictionContentPart(type="text", text="Part 1")]
        >>> content = Content(parts=parts)
    """

    def __init__(
        self,
        text: Optional[str] = None,
        parts: Optional[List[PredictionContentPart]] = None,
    ) -> None:
        """Initialize content for predictions.

        Args:
            text (Optional[str]):
                Simple text content (mutually exclusive with parts)
            parts (Optional[List[PredictionContentPart]]):
                Structured content parts (mutually exclusive with text)

        Raises:
            TypeError: If both text and parts are provided or neither is provided
        """

class Prediction:
    """Configuration for predicted outputs in OpenAI requests.

    This class provides configuration for predicted outputs, which can greatly
    improve response times when large parts of the model response are known ahead
    of time.

    Examples:
        >>> content = Content(text="Expected response")
        >>> prediction = Prediction(type="content", content=content)
        >>> prediction.type
        'content'
    """

    def __init__(
        self,
        type: str,
        content: Content,
    ) -> None:
        """Initialize prediction configuration.

        Args:
            type (str):
                Type of prediction (typically "content")
            content (Content):
                The predicted content
        """

    @property
    def type(self) -> str:
        """The prediction type."""

    @property
    def content(self) -> Content:
        """The predicted content."""

class StreamOptions:
    """Options for streaming chat completion responses.

    This class provides configuration for streaming behavior, including
    usage information and obfuscation settings.

    Examples:
        >>> options = StreamOptions(include_usage=True)
        >>> options.include_usage
        True
    """

    def __init__(
        self,
        include_obfuscation: Optional[bool] = None,
        include_usage: Optional[bool] = None,
    ) -> None:
        """Initialize stream options.

        Args:
            include_obfuscation (Optional[bool]):
                Whether to include obfuscation in the stream
            include_usage (Optional[bool]):
                Whether to include usage information in the stream
        """

    @property
    def include_obfuscation(self) -> Optional[bool]:
        """Whether obfuscation is included."""

    @property
    def include_usage(self) -> Optional[bool]:
        """Whether usage information is included."""

class ToolChoiceMode:
    """Mode for tool choice behavior in chat completions.

    This enum defines how the model should handle tool calls during generation.

    Examples:
        >>> mode = ToolChoiceMode.Auto
        >>> mode.value
        'auto'
    """

    NA = "ToolChoiceMode"
    """Model will not call any tools"""

    Auto = "ToolChoiceMode"
    """Model can choose to call tools or generate a message"""

    Required = "ToolChoiceMode"
    """Model must call one or more tools"""

class FunctionChoice:
    """Specification for a specific function to call.

    This class identifies a specific function by name for tool calling.

    Examples:
        >>> function = FunctionChoice(name="get_weather")
        >>> function.name
        'get_weather'
    """

    def __init__(self, name: str) -> None:
        """Initialize function choice.

        Args:
            name (str):
                Name of the function to call
        """

    @property
    def name(self) -> str:
        """The function name."""

class FunctionToolChoice:
    """Tool choice configuration for a specific function.

    This class specifies that the model should call a specific function tool.

    Examples:
        >>> function = FunctionChoice(name="get_weather")
        >>> tool_choice = FunctionToolChoice(function=function)
        >>> tool_choice.type
        'function'
    """

    def __init__(self, function: FunctionChoice) -> None:
        """Initialize function tool choice.

        Args:
            function (FunctionChoice):
                The function to call
        """

    @property
    def type(self) -> str:
        """The tool type (always 'function')."""

    @property
    def function(self) -> FunctionChoice:
        """The function specification."""

class CustomChoice:
    """Specification for a custom tool to call.

    This class identifies a custom tool by name for tool calling.

    Examples:
        >>> custom = CustomChoice(name="custom_tool")
        >>> custom.name
        'custom_tool'
    """

    def __init__(self, name: str) -> None:
        """Initialize custom choice.

        Args:
            name (str):
                Name of the custom tool to call
        """

    @property
    def name(self) -> str:
        """The custom tool name."""

class CustomToolChoice:
    """Tool choice configuration for a custom tool.

    This class specifies that the model should call a specific custom tool.

    Examples:
        >>> custom = CustomChoice(name="custom_tool")
        >>> tool_choice = CustomToolChoice(custom=custom)
        >>> tool_choice.type
        'custom'
    """

    def __init__(self, custom: CustomChoice) -> None:
        """Initialize custom tool choice.

        Args:
            custom (CustomChoice):
                The custom tool to call
        """

    @property
    def type(self) -> str:
        """The tool type (always 'custom')."""

    @property
    def custom(self) -> CustomChoice:
        """The custom tool specification."""

class ToolDefinition:
    """Definition of a tool for allowed tools configuration.

    This class defines a tool that can be included in an allowed tools list.

    Examples:
        >>> tool = ToolDefinition(function_name="get_weather")
        >>> tool.type
        'function'
    """

    def __init__(self, function_name: str) -> None:
        """Initialize tool definition.

        Args:
            function_name (str):
                Name of the function this tool wraps
        """

    @property
    def type(self) -> str:
        """The tool type (always 'function')."""

    @property
    def function(self) -> FunctionChoice:
        """The function specification."""

class AllowedToolsMode:
    """Mode for allowed tools constraint behavior.

    This enum defines how the model should behave when constrained to
    specific tools.

    Examples:
        >>> mode = AllowedToolsMode.Auto
        >>> mode.value
        'auto'
    """

    Auto = "AllowedToolsMode"
    """Model can pick from allowed tools or generate a message"""

    Required = "AllowedToolsMode"
    """Model must call one or more of the allowed tools"""

class InnerAllowedTools:
    """Inner configuration for allowed tools.

    This class contains the actual list of allowed tools and the mode.

    Examples:
        >>> tools = [ToolDefinition("get_weather")]
        >>> inner = InnerAllowedTools(mode=AllowedToolsMode.Auto, tools=tools)
    """

    @property
    def mode(self) -> AllowedToolsMode:
        """The mode for allowed tools."""

    @property
    def tools(self) -> List[ToolDefinition]:
        """The list of allowed tools."""

class AllowedTools:
    """Configuration for constraining model to specific tools.

    This class specifies a list of tools the model is allowed to use,
    along with the behavior mode.

    Examples:
        >>> tools = [ToolDefinition("get_weather")]
        >>> allowed = AllowedTools(mode=AllowedToolsMode.Auto, tools=tools)
        >>>
        >>> # Or from function names
        >>> allowed = AllowedTools.from_function_names(
        ...     mode=AllowedToolsMode.Required,
        ...     function_names=["get_weather", "get_time"]
        ... )
    """

    def __init__(
        self,
        mode: AllowedToolsMode,
        tools: List[ToolDefinition],
    ) -> None:
        """Initialize allowed tools configuration.

        Args:
            mode (AllowedToolsMode):
                The mode for tool usage behavior
            tools (List[ToolDefinition]):
                List of allowed tools
        """

    @staticmethod
    def from_function_names(
        mode: AllowedToolsMode,
        function_names: List[str],
    ) -> "AllowedTools":
        """Create AllowedTools from function names.

        Args:
            mode (AllowedToolsMode):
                The mode for tool usage behavior
            function_names (List[str]):
                List of function names to allow

        Returns:
            AllowedTools: Configured allowed tools instance
        """

    @property
    def type(self) -> str:
        """The configuration type (always 'allowed_tools')."""

    @property
    def allowed_tools(self) -> InnerAllowedTools:
        """The inner allowed tools configuration."""

    def __str__(self) -> str:
        """String representation of allowed tools.

        Returns:
            str: String representation
        """

class OpenAIToolChoice:
    """Tool choice configuration for chat completions.

    This class configures how the model should handle tool calling, supporting
    multiple modes including simple mode selection, specific tool choice, and
    allowed tools constraints.

    Examples:
        >>> # Simple mode
        >>> choice = ToolChoice.from_mode(ToolChoiceMode.Auto)
        >>>
        >>> # Specific function
        >>> choice = ToolChoice.from_function("get_weather")
        >>>
        >>> # Custom tool
        >>> choice = ToolChoice.from_custom("custom_tool")
        >>>
        >>> # Allowed tools
        >>> allowed = AllowedTools.from_function_names(
        ...     AllowedToolsMode.Auto,
        ...     ["get_weather"]
        ... )
        >>> choice = ToolChoice.from_allowed_tools(allowed)
    """

    @staticmethod
    def from_mode(mode: ToolChoiceMode) -> "OpenAIToolChoice":
        """Create tool choice from mode.

        Args:
            mode (ToolChoiceMode):
                The tool choice mode

        Returns:
            ToolChoice: Tool choice configured with mode
        """

    @staticmethod
    def from_function(function_name: str) -> "OpenAIToolChoice":
        """Create tool choice for specific function.

        Args:
            function_name (str):
                Name of the function to call

        Returns:
            ToolChoice: Tool choice configured for function
        """

    @staticmethod
    def from_custom(custom_name: str) -> "OpenAIToolChoice":
        """Create tool choice for custom tool.

        Args:
            custom_name (str):
                Name of the custom tool to call

        Returns:
            ToolChoice: Tool choice configured for custom tool
        """

    @staticmethod
    def from_allowed_tools(allowed_tools: AllowedTools) -> "OpenAIToolChoice":
        """Create tool choice from allowed tools.

        Args:
            allowed_tools (AllowedTools):
                Allowed tools configuration

        Returns:
            ToolChoice: Tool choice configured with allowed tools
        """

    def __str__(self) -> str:
        """String representation of tool choice.

        Returns:
            str: String representation
        """

class FunctionDefinition:
    """Definition of a function tool for OpenAI chat completions.

    This class defines a function that can be called by the model, including
    its name, description, parameters schema, and strict mode setting.

    Examples:
        >>> # Simple function
        >>> func = FunctionDefinition(
        ...     name="get_weather",
        ...     description="Get weather for a location"
        ... )
        >>>
        >>> # With parameters
        >>> params = {
        ...     "type": "object",
        ...     "properties": {
        ...         "location": {"type": "string"}
        ...     },
        ...     "required": ["location"]
        ... }
        >>> func = FunctionDefinition(
        ...     name="get_weather",
        ...     description="Get weather",
        ...     parameters=params,
        ...     strict=True
        ... )
    """

    def __init__(
        self,
        name: str,
        description: Optional[str] = None,
        parameters: Optional[Any] = None,
        strict: Optional[bool] = None,
    ) -> None:
        """Initialize function definition.

        Args:
            name (str):
                Name of the function
            description (Optional[str]):
                Description of what the function does
            parameters (Optional[Any]):
                JSON schema for function parameters
            strict (Optional[bool]):
                Whether to use strict schema validation
        """

    @property
    def name(self) -> str:
        """The function name."""

    @property
    def description(self) -> Optional[str]:
        """The function description."""

    @property
    def strict(self) -> Optional[bool]:
        """Whether strict schema validation is enabled."""

class FunctionTool:
    """Function tool for OpenAI chat completions.

    This class wraps a function definition to create a callable tool for
    the model.

    Examples:
        >>> func = FunctionDefinition(name="get_weather")
        >>> tool = FunctionTool(function=func, type="function")
        >>> tool.type
        'function'
    """

    def __init__(
        self,
        function: FunctionDefinition,
        type: str,
    ) -> None:
        """Initialize function tool.

        Args:
            function (FunctionDefinition):
                The function definition
            type (str):
                Tool type (typically "function")
        """

    @property
    def function(self) -> FunctionDefinition:
        """The function definition."""

    @property
    def type(self) -> str:
        """The tool type."""

class TextFormat:
    """Text format for custom tool outputs.

    This class defines unconstrained free-form text output format for
    custom tools.

    Examples:
        >>> format = TextFormat(type="text")
        >>> format.type
        'text'
    """

    def __init__(self, type: str) -> None:
        """Initialize text format.

        Args:
            type (str):
                Format type (typically "text")
        """

    @property
    def type(self) -> str:
        """The format type."""

class Grammar:
    """Grammar definition for structured custom tool outputs.

    This class defines a grammar that constrains custom tool outputs to
    follow specific syntax rules.

    Examples:
        >>> grammar = Grammar(
        ...     definition="number: /[0-9]+/",
        ...     syntax="lark"
        ... )
        >>> grammar.syntax
        'lark'
    """

    def __init__(
        self,
        definition: str,
        syntax: str,
    ) -> None:
        """Initialize grammar definition.

        Args:
            definition (str):
                The grammar definition
            syntax (str):
                Grammar syntax type ("lark" or "regex")
        """

    @property
    def definition(self) -> str:
        """The grammar definition."""

    @property
    def syntax(self) -> str:
        """The grammar syntax type."""

class GrammarFormat:
    """Grammar-based format for custom tool outputs.

    This class wraps a grammar definition to create a structured output
    format for custom tools.

    Examples:
        >>> grammar = Grammar(definition="...", syntax="lark")
        >>> format = GrammarFormat(grammar=grammar, type="grammar")
    """

    def __init__(
        self,
        grammar: Grammar,
        type: str,
    ) -> None:
        """Initialize grammar format.

        Args:
            grammar (Grammar):
                The grammar definition
            type (str):
                Format type (typically "grammar")
        """

    @property
    def grammar(self) -> Grammar:
        """The grammar definition."""

    @property
    def type(self) -> str:
        """The format type."""

class CustomToolFormat:
    """Format specification for custom tool outputs.

    This class supports either free-form text or grammar-constrained output
    formats for custom tools.

    Examples:
        >>> # Text format
        >>> format = CustomToolFormat(type="text")
        >>>
        >>> # Grammar format
        >>> grammar = Grammar(definition="...", syntax="lark")
        >>> format = CustomToolFormat(grammar=grammar)
    """

    def __init__(
        self,
        type: Optional[str] = None,
        grammar: Optional[Grammar] = None,
    ) -> None:
        """Initialize custom tool format.

        Args:
            type (Optional[str]):
                Format type for text output
            grammar (Optional[Grammar]):
                Grammar definition for structured output
        """

class CustomDefinition:
    """Definition of a custom tool for OpenAI chat completions.

    This class defines a custom tool with optional format constraints.

    Examples:
        >>> # Simple custom tool
        >>> custom = CustomDefinition(
        ...     name="analyzer",
        ...     description="Analyze data"
        ... )
        >>>
        >>> # With format constraints
        >>> format = CustomToolFormat(type="text")
        >>> custom = CustomDefinition(
        ...     name="analyzer",
        ...     description="Analyze data",
        ...     format=format
        ... )
    """

    def __init__(
        self,
        name: str,
        description: Optional[str] = None,
        format: Optional[CustomToolFormat] = None,
    ) -> None:
        """Initialize custom tool definition.

        Args:
            name (str):
                Name of the custom tool
            description (Optional[str]):
                Description of what the tool does
            format (Optional[CustomToolFormat]):
                Output format constraints
        """

    @property
    def name(self) -> str:
        """The tool name."""

    @property
    def description(self) -> Optional[str]:
        """The tool description."""

    @property
    def format(self) -> Optional[CustomToolFormat]:
        """The output format constraints."""

class CustomTool:
    """Custom tool for OpenAI chat completions.

    This class wraps a custom tool definition to create a callable tool
    for the model.

    Examples:
        >>> custom = CustomDefinition(name="analyzer")
        >>> tool = CustomTool(custom=custom, type="custom")
        >>> tool.type
        'custom'
    """

    def __init__(
        self,
        custom: CustomDefinition,
        type: str,
    ) -> None:
        """Initialize custom tool.

        Args:
            custom (CustomDefinition):
                The custom tool definition
            type (str):
                Tool type (typically "custom")
        """

    @property
    def custom(self) -> CustomDefinition:
        """The custom tool definition."""

    @property
    def type(self) -> str:
        """The tool type."""

class OpenAITool:
    """Tool for OpenAI chat completions.

    This class represents either a function tool or custom tool that can
    be called by the model.

    Examples:
        >>> # Function tool
        >>> func = FunctionDefinition(name="get_weather")
        >>> func_tool = FunctionTool(function=func, type="function")
        >>> tool = Tool(function=func_tool)
        >>>
        >>> # Custom tool
        >>> custom = CustomDefinition(name="analyzer")
        >>> custom_tool = CustomTool(custom=custom, type="custom")
        >>> tool = Tool(custom=custom_tool)
    """

    def __init__(
        self,
        function: Optional[FunctionTool] = None,
        custom: Optional[CustomTool] = None,
    ) -> None:
        """Initialize tool.

        Args:
            function (Optional[FunctionTool]):
                Function tool definition
            custom (Optional[CustomTool]):
                Custom tool definition

        Raises:
            TypeError: If both or neither tool types are provided
        """

class OpenAIChatSettings:
    """Settings for OpenAI chat completion requests.

    This class provides comprehensive configuration options for OpenAI chat
    completions, including sampling parameters, tool usage, audio output,
    caching, and more.

    Examples:
        >>> # Basic settings
        >>> settings = OpenAIChatSettings(
        ...     max_completion_tokens=1000,
        ...     temperature=0.7,
        ...     top_p=0.9
        ... )
        >>>
        >>> # With tools
        >>> func = FunctionDefinition(name="get_weather")
        >>> tool = Tool(function=FunctionTool(function=func, type="function"))
        >>> settings = OpenAIChatSettings(
        ...     tools=[tool],
        ...     tool_choice=ToolChoice.from_mode(ToolChoiceMode.Auto)
        ... )
        >>>
        >>> # With audio output
        >>> audio = AudioParam(format="mp3", voice="alloy")
        >>> settings = OpenAIChatSettings(
        ...     audio=audio,
        ...     modalities=["text", "audio"]
        ... )
    """

    def __init__(
        self,
        max_completion_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        frequency_penalty: Optional[float] = None,
        timeout: Optional[float] = None,
        parallel_tool_calls: Optional[bool] = None,
        seed: Optional[int] = None,
        logit_bias: Optional[Dict[str, int]] = None,
        stop_sequences: Optional[List[str]] = None,
        logprobs: Optional[bool] = None,
        audio: Optional[AudioParam] = None,
        metadata: Optional[Dict[str, str]] = None,
        modalities: Optional[List[str]] = None,
        n: Optional[int] = None,
        prediction: Optional[Prediction] = None,
        presence_penalty: Optional[float] = None,
        prompt_cache_key: Optional[str] = None,
        reasoning_effort: Optional[str] = None,
        safety_identifier: Optional[str] = None,
        service_tier: Optional[str] = None,
        store: Optional[bool] = None,
        stream: Optional[bool] = None,
        stream_options: Optional[StreamOptions] = None,
        tool_choice: Optional[OpenAIToolChoice] = None,
        tools: Optional[List[OpenAITool]] = None,
        top_logprobs: Optional[int] = None,
        verbosity: Optional[str] = None,
        extra_body: Optional[Any] = None,
    ) -> None:
        """Initialize OpenAI chat settings.

        Args:
            max_completion_tokens (Optional[int]):
                Maximum tokens for completion (including reasoning tokens)
            temperature (Optional[float]):
                Sampling temperature (0.0 to 2.0)
            top_p (Optional[float]):
                Nucleus sampling parameter (0.0 to 1.0)
            top_k (Optional[int]):
                Top-k sampling parameter
            frequency_penalty (Optional[float]):
                Frequency penalty (-2.0 to 2.0)
            timeout (Optional[float]):
                Request timeout in seconds
            parallel_tool_calls (Optional[bool]):
                Enable parallel function calling
            seed (Optional[int]):
                Random seed for deterministic sampling
            logit_bias (Optional[Dict[str, int]]):
                Token bias map (-100 to 100)
            stop_sequences (Optional[List[str]]):
                Stop sequences (max 4)
            logprobs (Optional[bool]):
                Return log probabilities
            audio (Optional[AudioParam]):
                Audio output configuration
            metadata (Optional[Dict[str, str]]):
                Request metadata (max 16 key-value pairs)
            modalities (Optional[List[str]]):
                Output modalities (e.g., ["text", "audio"])
            n (Optional[int]):
                Number of completions to generate
            prediction (Optional[Prediction]):
                Predicted output configuration
            presence_penalty (Optional[float]):
                Presence penalty (-2.0 to 2.0)
            prompt_cache_key (Optional[str]):
                Cache key for prompt caching
            reasoning_effort (Optional[str]):
                Reasoning effort level (e.g., "low", "medium", "high")
            safety_identifier (Optional[str]):
                User identifier for safety checks
            service_tier (Optional[str]):
                Service tier ("auto", "default", "flex", "priority")
            store (Optional[bool]):
                Store completion for later retrieval
            stream (Optional[bool]):
                Stream response with SSE
            stream_options (Optional[StreamOptions]):
                Streaming configuration
            tool_choice (Optional[ToolChoice]):
                Tool choice configuration
            tools (Optional[List[Tool]]):
                Available tools
            top_logprobs (Optional[int]):
                Number of top log probs to return (0-20)
            verbosity (Optional[str]):
                Response verbosity ("low", "medium", "high")
            extra_body (Optional[Any]):
                Additional request parameters
        """

    @property
    def max_completion_tokens(self) -> Optional[int]:
        """Maximum completion tokens."""

    @property
    def temperature(self) -> Optional[float]:
        """Sampling temperature."""

    @property
    def top_p(self) -> Optional[float]:
        """Nucleus sampling parameter."""

    @property
    def top_k(self) -> Optional[int]:
        """Top-k sampling parameter."""

    @property
    def frequency_penalty(self) -> Optional[float]:
        """Frequency penalty."""

    @property
    def timeout(self) -> Optional[float]:
        """Request timeout."""

    @property
    def parallel_tool_calls(self) -> Optional[bool]:
        """Whether parallel tool calls are enabled."""

    @property
    def seed(self) -> Optional[int]:
        """Random seed."""

    @property
    def logit_bias(self) -> Optional[Dict[str, int]]:
        """Token bias map."""

    @property
    def stop_sequences(self) -> Optional[List[str]]:
        """Stop sequences."""

    @property
    def logprobs(self) -> Optional[bool]:
        """Whether to return log probabilities."""

    @property
    def audio(self) -> Optional[AudioParam]:
        """Audio output configuration."""

    @property
    def metadata(self) -> Optional[Dict[str, str]]:
        """Request metadata."""

    @property
    def modalities(self) -> Optional[List[str]]:
        """Output modalities."""

    @property
    def n(self) -> Optional[int]:
        """Number of completions."""

    @property
    def prediction(self) -> Optional[Prediction]:
        """Predicted output configuration."""

    @property
    def presence_penalty(self) -> Optional[float]:
        """Presence penalty."""

    @property
    def prompt_cache_key(self) -> Optional[str]:
        """Prompt cache key."""

    @property
    def reasoning_effort(self) -> Optional[str]:
        """Reasoning effort level."""

    @property
    def safety_identifier(self) -> Optional[str]:
        """Safety identifier."""

    @property
    def service_tier(self) -> Optional[str]:
        """Service tier."""

    @property
    def store(self) -> Optional[bool]:
        """Whether to store completion."""

    @property
    def stream(self) -> Optional[bool]:
        """Whether to stream response."""

    @property
    def stream_options(self) -> Optional[StreamOptions]:
        """Stream options."""

    @property
    def tool_choice(self) -> Optional[OpenAIToolChoice]:
        """Tool choice configuration."""

    @property
    def tools(self) -> Optional[List[OpenAITool]]:
        """Available tools."""

    @property
    def top_logprobs(self) -> Optional[int]:
        """Number of top log probabilities."""

    @property
    def verbosity(self) -> Optional[str]:
        """Response verbosity."""

    @property
    def extra_body(self) -> Optional[Dict[str, Any]]:
        """Additional request parameters."""

    def model_dump(self) -> Dict[str, Any]:
        """Convert settings to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation of settings
        """

    def settings_type(self) -> str:
        """Get the settings type identifier.

        Returns:
            str: Settings type ("OpenAIChat")
        """

    def __str__(self) -> str:
        """String representation of settings.

        Returns:
            str: String representation
        """

# ============================================================================
# Request Types
# ============================================================================

class File:
    """File reference for OpenAI chat completion messages.

    This class represents a file that can be included in a message, either
    by providing file data directly or referencing a file by ID.

    Examples:
        >>> # File by ID
        >>> file = File(file_id="file-abc123", filename="document.pdf")
        >>>
        >>> # File with data
        >>> file = File(
        ...     file_data="base64_encoded_data",
        ...     filename="document.pdf"
        ... )
    """

    def __init__(
        self,
        file_data: Optional[str] = None,
        file_id: Optional[str] = None,
        filename: Optional[str] = None,
    ) -> None:
        """Initialize file reference.

        Args:
            file_data (Optional[str]):
                Base64 encoded file data
            file_id (Optional[str]):
                OpenAI file ID
            filename (Optional[str]):
                File name
        """

    @property
    def file_data(self) -> Optional[str]:
        """The base64 encoded file data."""

    @property
    def file_id(self) -> Optional[str]:
        """The OpenAI file ID."""

    @property
    def filename(self) -> Optional[str]:
        """The file name."""

class FileContentPart:
    """File content part for OpenAI chat messages.

    This class represents a file as part of a message's content.

    Examples:
        >>> file_part = FileContentPart(
        ...     file_id="file-abc123",
        ...     filename="document.pdf"
        ... )
        >>> file_part.type
        'file'
    """

    def __init__(
        self,
        file_data: Optional[str] = None,
        file_id: Optional[str] = None,
        filename: Optional[str] = None,
    ) -> None:
        """Initialize file content part.

        Args:
            file_data (Optional[str]):
                Base64 encoded file data
            file_id (Optional[str]):
                OpenAI file ID
            filename (Optional[str]):
                File name
        """

    @property
    def file(self) -> File:
        """The file reference."""

    @property
    def type(self) -> str:
        """The content part type (always 'file')."""

class InputAudioData:
    """Audio data for input in OpenAI chat messages.

    This class represents audio input data with format specification.

    Examples:
        >>> audio_data = InputAudioData(
        ...     data="base64_encoded_audio",
        ...     format="wav"
        ... )
        >>> audio_data.format
        'wav'
    """

    def __init__(
        self,
        data: str,
        format: str,
    ) -> None:
        """Initialize input audio data.

        Args:
            data (str):
                Base64 encoded audio data
            format (str):
                Audio format (e.g., "wav", "mp3")
        """

    @property
    def data(self) -> str:
        """The base64 encoded audio data."""

    @property
    def format(self) -> str:
        """The audio format."""

class InputAudioContentPart:
    """Audio content part for OpenAI chat messages.

    This class represents audio input as part of a message's content.

    Examples:
        >>> audio_part = InputAudioContentPart(
        ...     data="base64_encoded_audio",
        ...     format="wav"
        ... )
        >>> audio_part.type
        'input_audio'
    """

    def __init__(
        self,
        data: str,
        format: str,
    ) -> None:
        """Initialize audio content part.

        Args:
            data (str):
                Base64 encoded audio data
            format (str):
                Audio format (e.g., "wav", "mp3")
        """

    @property
    def input_audio(self) -> InputAudioData:
        """The audio data."""

    @property
    def type(self) -> str:
        """The content part type (always 'input_audio')."""

class ImageUrl:
    """Image URL reference for OpenAI chat messages.

    This class represents an image by URL with optional detail level.

    Examples:
        >>> # Standard detail
        >>> image = ImageUrl(url="https://example.com/image.jpg")
        >>>
        >>> # High detail
        >>> image = ImageUrl(
        ...     url="https://example.com/image.jpg",
        ...     detail="high"
        ... )
    """

    def __init__(
        self,
        url: str,
        detail: Optional[str] = None,
    ) -> None:
        """Initialize image URL.

        Args:
            url (str):
                Image URL (can be HTTP URL or data URL)
            detail (Optional[str]):
                Detail level ("low", "high", or "auto")
        """

    @property
    def url(self) -> str:
        """The image URL."""

    @property
    def detail(self) -> Optional[str]:
        """The detail level."""

class ImageContentPart:
    """Image content part for OpenAI chat messages.

    This class represents an image as part of a message's content.

    Examples:
        >>> image_part = ImageContentPart(
        ...     url="https://example.com/image.jpg",
        ...     detail="high"
        ... )
        >>> image_part.type
        'image_url'
    """

    def __init__(
        self,
        url: str,
        detail: Optional[str] = None,
    ) -> None:
        """Initialize image content part.

        Args:
            url (str):
                Image URL (can be HTTP URL or data URL)
            detail (Optional[str]):
                Detail level ("low", "high", or "auto")
        """

    @property
    def image_url(self) -> ImageUrl:
        """The image URL reference."""

    @property
    def type(self) -> str:
        """The content part type (always 'image_url')."""

class TextContentPart:
    """Text content part for OpenAI chat messages.

    This class represents text as part of a message's content.

    Examples:
        >>> text_part = TextContentPart(text="Hello, world!")
        >>> text_part.text
        'Hello, world!'
        >>> text_part.type
        'text'
    """

    def __init__(self, text: str) -> None:
        """Initialize text content part.

        Args:
            text (str):
                Text content
        """

    @property
    def text(self) -> str:
        """The text content."""

    @property
    def type(self) -> str:
        """The content part type (always 'text')."""

class ChatMessage:
    """Message for OpenAI chat completions.

    This class represents a single message in a chat completion conversation,
    supporting multiple content types including text, images, audio, and files.

    Examples:
        >>> # Simple text message
        >>> msg = ChatMessage(role="user", content="Hello!")
        >>>
        >>> # Message with image
        >>> image = ImageContentPart(url="https://example.com/image.jpg")
        >>> msg = ChatMessage(role="user", content=[image])
        >>>
        >>> # Mixed content message
        >>> msg = ChatMessage(
        ...     role="user",
        ...     content=["Describe this image:", image]
        ... )
        >>>
        >>> # System message with name
        >>> msg = ChatMessage(
        ...     role="system",
        ...     content="You are a helpful assistant.",
        ...     name="assistant_v1"
        ... )
    """

    def __init__(
        self,
        role: str,
        content: Union[
            str,
            List[
                Union[
                    str,
                    TextContentPart,
                    ImageContentPart,
                    InputAudioContentPart,
                    FileContentPart,
                ]
            ],
        ],
        name: Optional[str] = None,
    ) -> None:
        """Initialize chat message.

        Args:
            role (str):
                Message role ("system", "user", "assistant", "tool", "developer")
            content (Union[str, List[...]]):
                Message content - can be:
                - String: Simple text message
                - List: Mixed content with strings and content parts
                - ContentPart: Single structured content part
            name (Optional[str]):
                Optional name for the message

        Raises:
            TypeError: If content format is invalid
        """

    @property
    def text(self) -> str:
        """Get the text content of the first part, if available. Returns
        an empty string if the first part is not text.
        This is meant for convenience when working with simple text messages.
        """

    @property
    def role(self) -> str:
        """The message role."""

    @property
    def content(
        self,
    ) -> List[Union[TextContentPart, ImageContentPart, InputAudioContentPart, FileContentPart]]:
        """The message content parts."""

    @property
    def name(self) -> Optional[str]:
        """The message name."""

    def bind(
        self,
        name: Optional[str] = None,
        value: Optional[str | int | float | bool | list] = None,
    ) -> "ChatMessage":
        """Bind variables to the message content.
        Args:
            name (Optional[str]):
                The variable name to bind.
            value (Optional[Union[str, int, float, bool, list]]):
                The variable value to bind.
        Returns:
            ChatMessage: A new ChatMessage instance with bound variables.
        """

    def bind_mut(
        self,
        name: Optional[str] = None,
        value: Optional[str | int | float | bool | list] = None,
    ) -> None:
        """Bind variables to the message content in place.
        Args:
            name (Optional[str]):
                The variable name to bind.
            value (Optional[Union[str, int, float, bool, list]]):
                The variable value to bind.
        Returns:
            None
        """

    def model_dump(self) -> dict:
        """Dump the message to a dictionary."""

# ============================================================================
# Response Types
# ============================================================================

class Function:
    """Function call information from OpenAI tool calls.

    This class represents a function call made by the model, including
    the function name and JSON-formatted arguments.

    Examples:
        >>> func = Function(
        ...     name="get_weather",
        ...     arguments='{"location": "San Francisco"}'
        ... )
        >>> func.name
        'get_weather'
    """

    @property
    def arguments(self) -> str:
        """The JSON-formatted function arguments."""

    @property
    def name(self) -> str:
        """The function name."""

class ToolCall:
    """Tool call information from OpenAI responses.

    This class represents a single tool call made by the model during
    generation.

    Examples:
        >>> # Accessing tool call from response
        >>> choice = response.choices[0]
        >>> if choice.message.tool_calls:
        ...     tool_call = choice.message.tool_calls[0]
        ...     print(tool_call.function.name)
        ...     print(tool_call.function.arguments)
    """

    @property
    def id(self) -> str:
        """The tool call ID."""

    @property
    def type(self) -> str:
        """The tool call type."""

    @property
    def function(self) -> Function:
        """The function call information."""

class UrlCitation:
    """URL citation from OpenAI web search.

    This class represents a citation to a web source used by the model
    when web search is enabled.

    Examples:
        >>> # Accessing citations from response
        >>> choice = response.choices[0]
        >>> for annotation in choice.message.annotations:
        ...     for citation in annotation.url_citations:
        ...         print(f"{citation.title}: {citation.url}")
    """

    @property
    def end_index(self) -> int:
        """The end index in the message content."""

    @property
    def start_index(self) -> int:
        """The start index in the message content."""

    @property
    def title(self) -> str:
        """The page title."""

    @property
    def url(self) -> str:
        """The URL."""

class Annotations:
    """Annotations attached to OpenAI message content.

    This class contains metadata and citations for message content,
    such as URL citations from web search.

    Examples:
        >>> # Checking for citations
        >>> choice = response.choices[0]
        >>> for annotation in choice.message.annotations:
        ...     print(f"Type: {annotation.type}")
        ...     for citation in annotation.url_citations:
        ...         print(f"  {citation.title}")
    """

    @property
    def type(self) -> str:
        """The annotation type."""

    @property
    def url_citations(self) -> List[UrlCitation]:
        """URL citations."""

class Audio:
    """Audio output from OpenAI chat completions.

    This class contains audio data generated by the model when audio
    output is requested.

    Examples:
        >>> # Accessing audio from response
        >>> choice = response.choices[0]
        >>> if choice.message.audio:
        ...     audio = choice.message.audio
        ...     print(f"Audio ID: {audio.id}")
        ...     print(f"Transcript: {audio.transcript}")
        ...     # audio.data contains base64 encoded audio
    """

    @property
    def data(self) -> str:
        """Base64 encoded audio data."""

    @property
    def expires_at(self) -> int:
        """Unix timestamp when audio expires."""

    @property
    def id(self) -> str:
        """Audio ID."""

    @property
    def transcript(self) -> str:
        """Audio transcript."""

class ChatCompletionMessage:
    """Message from OpenAI chat completion response.

    This class represents the model's response message, including text
    content, tool calls, audio, and annotations.

    Examples:
        >>> # Accessing message from response
        >>> choice = response.choices[0]
        >>> message = choice.message
        >>> print(f"Role: {message.role}")
        >>> print(f"Content: {message.content}")
        >>>
        >>> # Checking for tool calls
        >>> if message.tool_calls:
        ...     for call in message.tool_calls:
        ...         print(f"Function: {call.function.name}")
    """

    @property
    def content(self) -> Optional[str]:
        """The message content."""

    @property
    def refusal(self) -> Optional[str]:
        """Refusal reason if model refused request."""

    @property
    def role(self) -> str:
        """The message role."""

    @property
    def annotations(self) -> List[Annotations]:
        """Message annotations."""

    @property
    def tool_calls(self) -> List[ToolCall]:
        """Tool calls made by the model."""

    @property
    def audio(self) -> Optional[Audio]:
        """Audio output if requested."""

class TopLogProbs:
    """Top log probability information for a token.

    This class represents one of the top alternative tokens considered
    by the model, with its log probability.

    Examples:
        >>> # Accessing top log probs
        >>> choice = response.choices[0]
        >>> if choice.logprobs and choice.logprobs.content:
        ...     for log_content in choice.logprobs.content:
        ...         if log_content.top_logprobs:
        ...             for top in log_content.top_logprobs:
        ...                 print(f"{top.token}: {top.logprob}")
    """

    @property
    def bytes(self) -> Optional[List[int]]:
        """UTF-8 bytes of the token."""

    @property
    def logprob(self) -> float:
        """Log probability of the token."""

    @property
    def token(self) -> str:
        """The token."""

class LogContent:
    """Log probability content for a single token.

    This class contains detailed probability information for a token
    generated by the model.

    Examples:
        >>> # Analyzing token probabilities
        >>> choice = response.choices[0]
        >>> if choice.logprobs and choice.logprobs.content:
        ...     for log_content in choice.logprobs.content:
        ...         print(f"Token: {log_content.token}")
        ...         print(f"Log prob: {log_content.logprob}")
    """

    @property
    def bytes(self) -> Optional[List[int]]:
        """UTF-8 bytes of the token."""

    @property
    def logprob(self) -> float:
        """Log probability of the token."""

    @property
    def token(self) -> str:
        """The token."""

    @property
    def top_logprobs(self) -> Optional[List[TopLogProbs]]:
        """Top alternative tokens."""

class LogProbs:
    """Log probability information for OpenAI responses.

    This class contains log probability data for both generated content
    and refusals.

    Examples:
        >>> # Checking log probabilities
        >>> choice = response.choices[0]
        >>> if choice.logprobs:
        ...     if choice.logprobs.content:
        ...         print(f"Content tokens: {len(choice.logprobs.content)}")
        ...     if choice.logprobs.refusal:
        ...         print("Refusal log probs available")
    """

    @property
    def content(self) -> Optional[List[LogContent]]:
        """Log probabilities for content tokens."""

    @property
    def refusal(self) -> Optional[List[LogContent]]:
        """Log probabilities for refusal tokens."""

class Choice:
    """Choice from OpenAI chat completion response.

    This class represents one possible completion from the model, including
    the message, finish reason, and optional log probabilities.

    Examples:
        >>> # Accessing choice from response
        >>> choice = response.choices[0]
        >>> print(f"Message: {choice.message.content}")
        >>> print(f"Finish reason: {choice.finish_reason}")
        >>>
        >>> # Multiple choices (when n > 1)
        >>> for i, choice in enumerate(response.choices):
        ...     print(f"Choice {i}: {choice.message.content}")
    """

    @property
    def message(self) -> ChatCompletionMessage:
        """The completion message."""

    @property
    def finish_reason(self) -> str:
        """Reason for completion finishing."""

    @property
    def logprobs(self) -> Optional[LogProbs]:
        """Log probability information."""

class CompletionTokenDetails:
    """Detailed token usage for completion output.

    This class provides granular information about tokens used in the
    completion, including reasoning tokens and audio tokens.

    Examples:
        >>> # Accessing token details
        >>> usage = response.usage
        >>> details = usage.completion_tokens_details
        >>> print(f"Reasoning tokens: {details.reasoning_tokens}")
        >>> print(f"Audio tokens: {details.audio_tokens}")
    """

    @property
    def accepted_prediction_tokens(self) -> int:
        """Number of accepted prediction tokens."""

    @property
    def audio_tokens(self) -> int:
        """Number of audio tokens."""

    @property
    def reasoning_tokens(self) -> int:
        """Number of reasoning tokens."""

    @property
    def rejected_prediction_tokens(self) -> int:
        """Number of rejected prediction tokens."""

class PromptTokenDetails:
    """Detailed token usage for input prompt.

    This class provides information about tokens used in the prompt,
    including cached tokens and audio tokens.

    Examples:
        >>> # Accessing prompt token details
        >>> usage = response.usage
        >>> details = usage.prompt_tokens_details
        >>> print(f"Cached tokens: {details.cached_tokens}")
        >>> print(f"Audio tokens: {details.audio_tokens}")
    """

    @property
    def audio_tokens(self) -> int:
        """Number of audio tokens."""

    @property
    def cached_tokens(self) -> int:
        """Number of cached tokens."""

class Usage:
    """Token usage statistics for OpenAI chat completions.

    This class provides comprehensive token usage information, including
    detailed breakdowns for both prompt and completion tokens.

    Examples:
        >>> # Accessing usage information
        >>> usage = response.usage
        >>> print(f"Total tokens: {usage.total_tokens}")
        >>> print(f"Prompt tokens: {usage.prompt_tokens}")
        >>> print(f"Completion tokens: {usage.completion_tokens}")
        >>>
        >>> # Detailed breakdown
        >>> print(f"Cached tokens: {usage.prompt_tokens_details.cached_tokens}")
        >>> print(f"Reasoning tokens: {usage.completion_tokens_details.reasoning_tokens}")
    """

    @property
    def completion_tokens(self) -> int:
        """Total completion tokens."""

    @property
    def prompt_tokens(self) -> int:
        """Total prompt tokens."""

    @property
    def total_tokens(self) -> int:
        """Total tokens (prompt + completion)."""

    @property
    def completion_tokens_details(self) -> CompletionTokenDetails:
        """Detailed completion token breakdown."""

    @property
    def prompt_tokens_details(self) -> PromptTokenDetails:
        """Detailed prompt token breakdown."""

    @property
    def finish_reason(self) -> Optional[str]:
        """Finish reason if applicable."""

class OpenAIChatResponse:
    """Response from OpenAI chat completion API.

    This class represents a complete response from the chat completion API,
    including all choices, usage statistics, and metadata.

    Examples:
        >>> # Basic usage
        >>> response = OpenAIChatResponse(...)
        >>> print(response.choices[0].message.content)
        >>>
        >>> # Accessing metadata
        >>> print(f"Model: {response.model}")
        >>> print(f"ID: {response.id}")
        >>> print(f"Created: {response.created}")
        >>>
        >>> # Usage statistics
        >>> print(f"Total tokens: {response.usage.total_tokens}")
    """

    @property
    def id(self) -> str:
        """Unique completion ID."""

    @property
    def object(self) -> str:
        """Object type (always 'chat.completion')."""

    @property
    def created(self) -> int:
        """Unix timestamp of creation."""

    @property
    def model(self) -> str:
        """Model used for completion."""

    @property
    def choices(self) -> List[Choice]:
        """List of completion choices."""

    @property
    def usage(self) -> Usage:
        """Token usage statistics."""

    @property
    def service_tier(self) -> Optional[str]:
        """Service tier used."""

    @property
    def system_fingerprint(self) -> Optional[str]:
        """System fingerprint for backend configuration."""

    def __str__(self) -> str:
        """String representation of response."""

# ============================================================================
# Embedding Types
# ============================================================================

class OpenAIEmbeddingConfig:
    """Configuration for OpenAI embedding requests.

    This class provides settings for embedding generation, including
    model selection, dimensions, and encoding format.

    Examples:
        >>> # Standard configuration
        >>> config = OpenAIEmbeddingConfig(
        ...     model="text-embedding-3-small"
        ... )
        >>>
        >>> # Custom dimensions
        >>> config = OpenAIEmbeddingConfig(
        ...     model="text-embedding-3-large",
        ...     dimensions=512
        ... )
    """

    def __init__(
        self,
        model: str,
        dimensions: Optional[int] = None,
        encoding_format: Optional[str] = None,
        user: Optional[str] = None,
    ) -> None:
        """Initialize embedding configuration.

        Args:
            model (str):
                Model ID for embeddings
            dimensions (Optional[int]):
                Number of dimensions for output embeddings
            encoding_format (Optional[str]):
                Format for embeddings ("float" or "base64")
            user (Optional[str]):
                User identifier for tracking
        """

    @property
    def model(self) -> str:
        """The embedding model ID."""

    @property
    def dimensions(self) -> Optional[int]:
        """Number of embedding dimensions."""

    @property
    def encoding_format(self) -> Optional[str]:
        """Encoding format for embeddings."""

    @property
    def user(self) -> Optional[str]:
        """User identifier."""

class EmbeddingObject:
    """Single embedding from OpenAI embedding response.

    This class represents one embedding vector from the response.

    Examples:
        >>> # Accessing embeddings
        >>> for embedding in response.data:
        ...     print(f"Index: {embedding.index}")
        ...     print(f"Dimensions: {len(embedding.embedding)}")
    """

    @property
    def embedding(self) -> List[float]:
        """The embedding vector."""

    @property
    def index(self) -> int:
        """Index in the input list."""

    @property
    def object(self) -> str:
        """Object type (always 'embedding')."""

class UsageObject:
    """Token usage for embedding request.

    This class provides token usage statistics for embedding requests.

    Examples:
        >>> usage = response.usage
        >>> print(f"Prompt tokens: {usage.prompt_tokens}")
        >>> print(f"Total tokens: {usage.total_tokens}")
    """

    @property
    def prompt_tokens(self) -> int:
        """Tokens in input prompts."""

    @property
    def total_tokens(self) -> int:
        """Total tokens processed."""

class OpenAIEmbeddingResponse:
    """Response from OpenAI embedding API.

    This class represents a complete response from the embedding API,
    including all generated embeddings and usage statistics.

    Examples:
        >>> # Accessing embeddings
        >>> response = OpenAIEmbeddingResponse(...)
        >>> for embedding in response.data:
        ...     vector = embedding.embedding
        ...     # Use embedding vector
        >>>
        >>> # Usage information
        >>> print(f"Tokens used: {response.usage.total_tokens}")
    """

    @property
    def data(self) -> List[EmbeddingObject]:
        """List of embedding objects."""

    @property
    def model(self) -> str:
        """Model used for embeddings."""

    @property
    def object(self) -> str:
        """Object type (always 'list')."""

    @property
    def usage(self) -> UsageObject:
        """Token usage statistics."""

    def __str__(self) -> str:
        """String representation of response."""

###### __potatohead__.google module ######'

class SchemaType:
    """Schema type definitions for Google/Gemini API.

    Defines the available data types that can be used in schema definitions
    for structured outputs and function parameters.

    Examples:
        >>> schema_type = SchemaType.String
        >>> schema_type.value
        'STRING'
    """

    TypeUnspecified = "SchemaType"
    """Unspecified type"""

    String = "SchemaType"
    """String data type"""

    Number = "SchemaType"
    """Numeric data type (floating point)"""

    Integer = "SchemaType"
    """Integer data type"""

    Boolean = "SchemaType"
    """Boolean data type"""

    Array = "SchemaType"
    """Array/list data type"""

    Object = "SchemaType"
    """Object/dictionary data type"""

    Null = "SchemaType"
    """Null data type"""

class HarmCategory:
    """Harm categories for safety filtering in Google/Gemini API.

    Defines categories of potentially harmful content that can be detected
    and filtered by the model's safety systems.

    Examples:
        >>> category = HarmCategory.HarmCategoryHateSpeech
        >>> category.value
        'HARM_CATEGORY_HATE_SPEECH'
    """

    HarmCategoryUnspecified = "HarmCategory"
    """Unspecified harm category"""

    HarmCategoryDerogatory = "HarmCategory"
    """Derogatory content"""

    HarmCategoryToxicity = "HarmCategory"
    """Toxic content"""

    HarmCategoryViolence = "HarmCategory"
    """Violent content"""

    HarmCategorySexual = "HarmCategory"
    """Sexual content"""

    HarmCategoryMedical = "HarmCategory"
    """Medical misinformation"""

    HarmCategoryDangerous = "HarmCategory"
    """Dangerous content"""

    HarmCategoryHarassment = "HarmCategory"
    """Harassment content"""

    HarmCategoryHateSpeech = "HarmCategory"
    """Hate speech content"""

    HarmCategorySexuallyExplicit = "HarmCategory"
    """Sexually explicit content"""

    HarmCategoryDangerousContent = "HarmCategory"
    """Dangerous content (alternative)"""

class HarmBlockThreshold:
    """Thresholds for blocking harmful content.

    Defines sensitivity levels for blocking content based on harm probability.

    Examples:
        >>> threshold = HarmBlockThreshold.BlockMediumAndAbove
        >>> threshold.value
        'BLOCK_MEDIUM_AND_ABOVE'
    """

    HarmBlockThresholdUnspecified = "HarmBlockThreshold"
    """Unspecified threshold"""

    BlockLowAndAbove = "HarmBlockThreshold"
    """Block content with low or higher harm probability"""

    BlockMediumAndAbove = "HarmBlockThreshold"
    """Block content with medium or higher harm probability"""

    BlockOnlyHigh = "HarmBlockThreshold"
    """Block only high harm probability content"""

    BlockNone = "HarmBlockThreshold"
    """Do not block any content"""

    Off = "HarmBlockThreshold"
    """Turn off safety filtering entirely"""

class HarmBlockMethod:
    """Method for blocking harmful content.

    Specifies whether blocking decisions use probability or severity scores.

    Examples:
        >>> method = HarmBlockMethod.Probability
        >>> method.value
        'PROBABILITY'
    """

    HarmBlockMethodUnspecified = "HarmBlockMethod"
    """Unspecified blocking method"""

    Severity = "HarmBlockMethod"
    """Use severity scores for blocking decisions"""

    Probability = "HarmBlockMethod"
    """Use probability scores for blocking decisions"""

class Modality:
    """Content modality types supported by the model.

    Defines the types of content (text, image, audio, etc.) that can be
    included in requests and responses.

    Examples:
        >>> modality = Modality.Text
        >>> modality.value
        'TEXT'
    """

    ModalityUnspecified = "Modality"
    """Unspecified modality"""

    Text = "Modality"
    """Text content"""

    Image = "Modality"
    """Image content"""

    Audio = "Modality"
    """Audio content"""

    Video = "Modality"
    """Video content"""

    Document = "Modality"
    """Document content"""

class MediaResolution:
    """Media resolution levels for input processing.

    Controls the token resolution at which media content is sampled,
    affecting quality and token usage.

    Examples:
        >>> resolution = MediaResolution.MediaResolutionHigh
        >>> resolution.value
        'MEDIA_RESOLUTION_HIGH'
    """

    MediaResolutionUnspecified = "MediaResolution"
    """Unspecified resolution"""

    MediaResolutionLow = "MediaResolution"
    """Low resolution (64 tokens)"""

    MediaResolutionMedium = "MediaResolution"
    """Medium resolution (256 tokens)"""

    MediaResolutionHigh = "MediaResolution"
    """High resolution with zoomed reframing (256 tokens)"""

class ModelRoutingPreference:
    """Preference for automatic model routing.

    Controls how models are selected when using automatic routing,
    balancing quality, cost, and performance.

    Examples:
        >>> preference = ModelRoutingPreference.Balanced
        >>> preference.value
        'BALANCED'
    """

    Unknown = "ModelRoutingPreference"
    """Unknown preference"""

    PrioritizeQuality = "ModelRoutingPreference"
    """Prioritize response quality"""

    Balanced = "ModelRoutingPreference"
    """Balance quality and cost"""

    PrioritizeCost = "ModelRoutingPreference"
    """Prioritize lower cost"""

class ThinkingLevel:
    """Level of model thinking/reasoning to apply.

    Controls the depth of reasoning the model performs before generating
    its final response.

    Examples:
        >>> level = ThinkingLevel.High
        >>> level.value
        'HIGH'
    """

    ThinkingLevelUnspecified = "ThinkingLevel"
    """Unspecified thinking level"""

    Low = "ThinkingLevel"
    """Low level of thinking"""

    High = "ThinkingLevel"
    """High level of thinking"""

class Mode:
    """Function calling mode for tool usage.

    Controls how the model handles function/tool calls during generation.

    Examples:
        >>> mode = Mode.Auto
        >>> mode.value
        'AUTO'
    """

    ModeUnspecified = "Mode"
    """Unspecified mode"""

    Validated = "Mode"
    """Model may call functions or respond naturally, validated"""

    Any = "Mode"
    """Model must call a function"""

    Auto = "Mode"
    """Model decides whether to call functions or respond naturally"""

    None_Mode = "Mode"
    """Model will not call any functions"""

class Behavior:
    """Function execution behavior.

    Specifies whether function calls are blocking or non-blocking.

    Examples:
        >>> behavior = Behavior.Blocking
        >>> behavior.value
        'BLOCKING'
    """

    Unspecified = "Behavior"
    """Unspecified behavior"""

    Blocking = "Behavior"
    """Function execution blocks until complete"""

    NonBlocking = "Behavior"
    """Function execution does not block"""

class Language:
    """Programming language for executable code.

    Specifies the language used when the model generates executable code.

    Examples:
        >>> lang = Language.Python
        >>> lang.value
        'PYTHON'
    """

    LanguageUnspecified = "Language"
    """Unspecified language"""

    Python = "Language"
    """Python programming language"""

class Outcome:
    """Code execution outcome status.

    Indicates the result of executing generated code.

    Examples:
        >>> outcome = Outcome.OutcomeOk
        >>> outcome.value
        'OUTCOME_OK'
    """

    OutcomeUnspecified = "Outcome"
    """Unspecified outcome"""

    OutcomeOk = "Outcome"
    """Execution completed successfully"""

    OutcomeFailed = "Outcome"
    """Execution failed"""

    OutcomeDeadlineExceeded = "Outcome"
    """Execution exceeded time limit"""

class ApiSpecType:
    """API specification type for external retrieval.

    Defines the type of external API used for grounding/retrieval.

    Examples:
        >>> spec = ApiSpecType.ElasticSearch
        >>> spec.value
        'ELASTIC_SEARCH'
    """

    ApiSpecUnspecified = "ApiSpecType"
    """Unspecified API spec"""

    SimpleSearch = "ApiSpecType"
    """Simple search API"""

    ElasticSearch = "ApiSpecType"
    """Elasticsearch API"""

class AuthType:
    """Authentication type for external APIs.

    Specifies the authentication method used to access external APIs.

    Examples:
        >>> auth = AuthType.ApiKeyAuth
        >>> auth.value
        'API_KEY_AUTH'
    """

    AuthTypeUnspecified = "AuthType"
    """Unspecified auth type"""

    NoAuth = "AuthType"
    """No authentication"""

    ApiKeyAuth = "AuthType"
    """API key authentication"""

    HttpBasicAuth = "AuthType"
    """HTTP basic authentication"""

    GoogleServiceAccountAuth = "AuthType"
    """Google service account authentication"""

    Oauth = "AuthType"
    """OAuth authentication"""

    OidcAuth = "AuthType"
    """OIDC authentication"""

class HttpElementLocation:
    """Location of HTTP authentication element.

    Specifies where authentication information appears in HTTP requests.

    Examples:
        >>> location = HttpElementLocation.HttpInHeader
        >>> location.value
        'HTTP_IN_HEADER'
    """

    HttpInUnspecified = "HttpElementLocation"
    """Unspecified location"""

    HttpInQuery = "HttpElementLocation"
    """In query parameters"""

    HttpInHeader = "HttpElementLocation"
    """In HTTP headers"""

    HttpInPath = "HttpElementLocation"
    """In URL path"""

    HttpInBody = "HttpElementLocation"
    """In request body"""

    HttpInCookie = "HttpElementLocation"
    """In cookies"""

class PhishBlockThreshold:
    """Phishing/malicious URL blocking threshold.

    Controls the confidence level required to block potentially malicious URLs.

    Examples:
        >>> threshold = PhishBlockThreshold.BlockMediumAndAbove
        >>> threshold.value
        'BLOCK_MEDIUM_AND_ABOVE'
    """

    PhishBlockThresholdUnspecified = "PhishBlockThreshold"
    """Unspecified threshold"""

    BlockLowAndAbove = "PhishBlockThreshold"
    """Block low confidence and above"""

    BlockMediumAndAbove = "PhishBlockThreshold"
    """Block medium confidence and above"""

    BlockHighAndAbove = "PhishBlockThreshold"
    """Block high confidence and above"""

    BlockHigherAndAbove = "PhishBlockThreshold"
    """Block higher confidence and above"""

    BlockVeryHighAndAbove = "PhishBlockThreshold"
    """Block very high confidence and above"""

    BlockOnlyExtremelyHigh = "PhishBlockThreshold"
    """Block only extremely high confidence"""

class DynamicRetrievalMode:
    """Mode for dynamic retrieval behavior.

    Controls when the model triggers retrieval operations.

    Examples:
        >>> mode = DynamicRetrievalMode.ModeDynamic
        >>> mode.value
        'MODE_DYNAMIC'
    """

    ModeUnspecified = "DynamicRetrievalMode"
    """Unspecified mode (always trigger)"""

    ModeDynamic = "DynamicRetrievalMode"
    """Trigger retrieval only when necessary"""

class ComputerUseEnvironment:
    """Environment for computer use capabilities.

    Specifies the environment in which the model operates when using
    computer control features.

    Examples:
        >>> env = ComputerUseEnvironment.EnvironmentBrowser
        >>> env.value
        'ENVIRONMENT_BROWSER'
    """

    EnvironmentUnspecified = "ComputerUseEnvironment"
    """Unspecified environment"""

    EnvironmentBrowser = "ComputerUseEnvironment"
    """Web browser environment"""

class TrafficType:
    """Type of API traffic for billing purposes.

    Indicates whether the request uses pay-as-you-go or provisioned quota.

    Examples:
        >>> traffic = TrafficType.OnDemand
        >>> traffic.value
        'ON_DEMAND'
    """

    TrafficTypeUnspecified = "TrafficType"
    """Unspecified traffic type"""

    OnDemand = "TrafficType"
    """Pay-as-you-go quota"""

    ProvisionedThroughput = "TrafficType"
    """Provisioned throughput quota"""

class BlockedReason:
    """Reason why content was blocked.

    Indicates why a prompt or response was blocked by content filters.

    Examples:
        >>> reason = BlockedReason.Safety
        >>> reason.value
        'SAFETY'
    """

    BlockedReasonUnspecified = "BlockedReason"
    """Unspecified reason"""

    Safety = "BlockedReason"
    """Blocked for safety reasons"""

    Other = "BlockedReason"
    """Blocked for other reasons"""

    Blocklist = "BlockedReason"
    """Blocked due to blocklist match"""

    ModelArmor = "BlockedReason"
    """Blocked by Model Armor"""

    ProhibitedContent = "BlockedReason"
    """Contains prohibited content"""

    ImageSafety = "BlockedReason"
    """Blocked for image safety"""

    Jailbreak = "BlockedReason"
    """Blocked as jailbreak attempt"""

class UrlRetrievalStatus:
    """Status of URL retrieval operation.

    Indicates whether a URL was successfully retrieved by the tool.

    Examples:
        >>> status = UrlRetrievalStatus.UrlRetrievalStatusSuccess
        >>> status.value
        'URL_RETRIEVAL_STATUS_SUCCESS'
    """

    UrlRetrievalStatusUnspecified = "UrlRetrievalStatus"
    """Unspecified status"""

    UrlRetrievalStatusSuccess = "UrlRetrievalStatus"
    """URL retrieved successfully"""

    UrlRetrievalStatusError = "UrlRetrievalStatus"
    """URL retrieval failed"""

class HarmProbability:
    """Probability level of harmful content.

    Indicates the likelihood that content contains harmful material.

    Examples:
        >>> prob = HarmProbability.Medium
        >>> prob.value
        'MEDIUM'
    """

    HarmProbabilityUnspecified = "HarmProbability"
    """Unspecified probability"""

    Negligible = "HarmProbability"
    """Negligible harm probability"""

    Low = "HarmProbability"
    """Low harm probability"""

    Medium = "HarmProbability"
    """Medium harm probability"""

    High = "HarmProbability"
    """High harm probability"""

class HarmSeverity:
    """Severity level of harmful content.

    Indicates the severity of potentially harmful content.

    Examples:
        >>> severity = HarmSeverity.HarmSeverityMedium
        >>> severity.value
        'HARM_SEVERITY_MEDIUM'
    """

    HarmSeverityUnspecified = "HarmSeverity"
    """Unspecified severity"""

    HarmSeverityNegligible = "HarmSeverity"
    """Negligible severity"""

    HarmSeverityLow = "HarmSeverity"
    """Low severity"""

    HarmSeverityMedium = "HarmSeverity"
    """Medium severity"""

    HarmSeverityHigh = "HarmSeverity"
    """High severity"""

class FinishReason:
    """Reason why generation stopped.

    Indicates why the model stopped generating tokens.

    Examples:
        >>> reason = FinishReason.Stop
        >>> reason.value
        'STOP'
    """

    FinishReasonUnspecified = "FinishReason"
    """Unspecified reason"""

    Stop = "FinishReason"
    """Natural stopping point or stop sequence reached"""

    MaxTokens = "FinishReason"
    """Maximum token limit reached"""

    Safety = "FinishReason"
    """Stopped due to safety concerns"""

    Recitation = "FinishReason"
    """Stopped due to potential recitation"""

    Other = "FinishReason"
    """Stopped for other reasons"""

    Blocklist = "FinishReason"
    """Stopped due to blocklist match"""

    ProhibitedContent = "FinishReason"
    """Stopped due to prohibited content"""

    Spii = "FinishReason"
    """Stopped due to sensitive personally identifiable information"""

    MalformedFunctionCall = "FinishReason"
    """Stopped due to malformed function call"""

    ModelArmor = "FinishReason"
    """Stopped by Model Armor"""

    ImageSafety = "FinishReason"
    """Generated image violates safety policies"""

    ImageProhibitedContent = "FinishReason"
    """Generated image contains prohibited content"""

    ImageRecitation = "FinishReason"
    """Generated image may be recitation"""

    ImageOther = "FinishReason"
    """Image generation stopped for other reasons"""

    UnexpectedToolCall = "FinishReason"
    """Unexpected tool call generated"""

    NoImage = "FinishReason"
    """Expected image but none generated"""

class EmbeddingTaskType:
    """Task type for embedding generation.

    Specifies the intended use case for embeddings, which may affect
    how they are computed.

    Examples:
        >>> task = EmbeddingTaskType.RetrievalDocument
        >>> task.value
        'RETRIEVAL_DOCUMENT'
    """

    TaskTypeUnspecified = "EmbeddingTaskType"
    """Unspecified task type"""

    RetrievalQuery = "EmbeddingTaskType"
    """Query for retrieval tasks"""

    RetrievalDocument = "EmbeddingTaskType"
    """Document for retrieval tasks"""

    SemanticSimilarity = "EmbeddingTaskType"
    """Semantic similarity comparison"""

    Classification = "EmbeddingTaskType"
    """Classification tasks"""

    Clustering = "EmbeddingTaskType"
    """Clustering tasks"""

class Schema:
    """JSON Schema definition for structured outputs and parameters.

    Defines the structure, types, and constraints for JSON data used in
    function parameters and structured outputs. Based on OpenAPI 3.0 schema.

    Examples:
        >>> # Simple string schema
        >>> schema = Schema(
        ...     type=SchemaType.String,
        ...     description="User's name",
        ...     min_length="1",
        ...     max_length="100"
        ... )

        >>> # Object schema with properties
        >>> schema = Schema(
        ...     type=SchemaType.Object,
        ...     properties={
        ...         "name": Schema(type=SchemaType.String),
        ...         "age": Schema(type=SchemaType.Integer, minimum=0.0)
        ...     },
        ...     required=["name"]
        ... )
    """

    def __init__(
        self,
        type: Optional[SchemaType] = None,
        format: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        nullable: Optional[bool] = None,
        enum_: Optional[List[str]] = None,
        max_items: Optional[str] = None,
        min_items: Optional[str] = None,
        properties: Optional[Dict[str, "Schema"]] = None,
        required: Optional[List[str]] = None,
        min_properties: Optional[str] = None,
        max_properties: Optional[str] = None,
        min_length: Optional[str] = None,
        max_length: Optional[str] = None,
        pattern: Optional[str] = None,
        example: Optional[Any] = None,
        any_of: Optional[List["Schema"]] = None,
        property_ordering: Optional[List[str]] = None,
        default: Optional[Any] = None,
        items: Optional["Schema"] = None,
        minimum: Optional[float] = None,
        maximum: Optional[float] = None,
    ) -> None:
        """Initialize a schema definition.

        Args:
            type (Optional[SchemaType]):
                The data type (string, number, object, etc.)
            format (Optional[str]):
                Format hint for the type (e.g., "date-time")
            title (Optional[str]):
                Human-readable title
            description (Optional[str]):
                Description of the schema
            nullable (Optional[bool]):
                Whether null values are allowed
            enum_ (Optional[List[str]]):
                List of allowed values
            max_items (Optional[str]):
                Maximum array length (for arrays)
            min_items (Optional[str]):
                Minimum array length (for arrays)
            properties (Optional[Dict[str, "Schema"]]):
                Object properties (for objects)
            required (Optional[List[str]]):
                Required property names (for objects)
            min_properties (Optional[str]):
                Minimum number of properties (for objects)
            max_properties (Optional[str]):
                Maximum number of properties (for objects)
            min_length (Optional[str]):
                Minimum string length (for strings)
            max_length (Optional[str]):
                Maximum string length (for strings)
            pattern (Optional[str]):
                Regular expression pattern (for strings)
            example (Optional[Any]):
                Example value
            any_of (Optional[List["Schema"]]):
                List of alternative schemas
            property_ordering (Optional[List[str]]):
                Order of properties
            default (Optional[Any]):
                Default value
            items (Optional["Schema"]):
                Schema for array items (for arrays)
            minimum (Optional[float]):
                Minimum numeric value (for numbers)
            maximum (Optional[float]):
                Maximum numeric value (for numbers)
        """

class SafetySetting:
    """Safety filtering configuration for harmful content.

    Controls how the model handles potentially harmful content in specific
    harm categories. Each setting applies to one harm category.

    Examples:
        >>> # Block hate speech with medium threshold
        >>> setting = SafetySetting(
        ...     category=HarmCategory.HarmCategoryHateSpeech,
        ...     threshold=HarmBlockThreshold.BlockMediumAndAbove
        ... )

        >>> # Disable blocking for harassment
        >>> setting = SafetySetting(
        ...     category=HarmCategory.HarmCategoryHarassment,
        ...     threshold=HarmBlockThreshold.BlockNone
        ... )
    """

    def __init__(
        self,
        category: HarmCategory,
        threshold: HarmBlockThreshold,
    ) -> None:
        """Initialize a safety setting.

        Args:
            category (HarmCategory):
                The harm category to configure
            threshold (HarmBlockThreshold):
                The blocking threshold to apply
        """

    @property
    def category(self) -> HarmCategory:
        """The harm category."""

    @property
    def threshold(self) -> HarmBlockThreshold:
        """The blocking threshold."""

class GeminiThinkingConfig:
    """Configuration for model thinking/reasoning features.

    Controls the model's internal reasoning process, including whether to
    include thoughts in the response and the computational budget.

    Examples:
        >>> # Enable high-level thinking with thoughts included
        >>> config = ThinkingConfig(
        ...     include_thoughts=True,
        ...     thinking_level=ThinkingLevel.High
        ... )

        >>> # Limit thinking budget
        >>> config = ThinkingConfig(
        ...     include_thoughts=False,
        ...     thinking_budget=1000
        ... )
    """

    def __init__(
        self,
        include_thoughts: Optional[bool] = None,
        thinking_budget: Optional[int] = None,
        thinking_level: Optional[ThinkingLevel] = None,
    ) -> None:
        """Initialize thinking configuration.

        Args:
            include_thoughts (Optional[bool]):
                Whether to include reasoning steps in response
            thinking_budget (Optional[int]):
                Token budget for thinking process
            thinking_level (Optional[ThinkingLevel]):
                Depth of reasoning to apply
        """

    @property
    def include_thoughts(self) -> Optional[bool]:
        """Whether to include thoughts in response."""

    @property
    def thinking_budget(self) -> Optional[int]:
        """Token budget for thinking."""

    @property
    def thinking_level(self) -> Optional[ThinkingLevel]:
        """Level of thinking/reasoning."""

class ImageConfig:
    """Configuration for image generation features.

    Controls aspect ratio and size for generated images.

    Examples:
        >>> # Generate widescreen 4K image
        >>> config = ImageConfig(
        ...     aspect_ratio="16:9",
        ...     image_size="4K"
        ... )

        >>> # Generate square 1K image
        >>> config = ImageConfig(
        ...     aspect_ratio="1:1",
        ...     image_size="1K"
        ... )
    """

    def __init__(
        self,
        aspect_ratio: Optional[str] = None,
        image_size: Optional[str] = None,
    ) -> None:
        """Initialize image configuration.

        Args:
            aspect_ratio (Optional[str]):
                Desired aspect ratio (e.g., "16:9", "1:1")
            image_size (Optional[str]):
                Image size ("1K", "2K", "4K")
        """

    @property
    def aspect_ratio(self) -> Optional[str]:
        """The image aspect ratio."""

    @property
    def image_size(self) -> Optional[str]:
        """The image size."""

class AutoRoutingMode:
    """Configuration for automatic model routing.

    Controls model selection based on routing preferences when using
    automatic routing features.

    Examples:
        >>> # Prioritize quality over cost
        >>> mode = AutoRoutingMode(
        ...     model_routing_preference=ModelRoutingPreference.PrioritizeQuality
        ... )

        >>> # Balance quality and cost
        >>> mode = AutoRoutingMode(
        ...     model_routing_preference=ModelRoutingPreference.Balanced
        ... )
    """

    def __init__(
        self,
        model_routing_preference: Optional[ModelRoutingPreference] = None,
    ) -> None:
        """Initialize automatic routing configuration.

        Args:
            model_routing_preference (Optional[ModelRoutingPreference]):
                Preference for model selection
        """

    @property
    def model_routing_preference(self) -> Optional[ModelRoutingPreference]:
        """The routing preference."""

class ManualRoutingMode:
    """Configuration for manual model routing.

    Explicitly specifies which model to use instead of automatic selection.

    Examples:
        >>> mode = ManualRoutingMode(model_name="gemini-2.0-flash-exp")
    """

    def __init__(
        self,
        model_name: str,
    ) -> None:
        """Initialize manual routing configuration.

        Args:
            model_name (str):
                Name of the model to use
        """

    @property
    def model_name(self) -> str:
        """The model name."""

class RoutingConfigMode:
    """Union type for routing configuration modes.

    Represents either automatic or manual routing configuration.

    Examples:
        >>> # Automatic routing
        >>> mode = RoutingConfigMode(
        ...     auto_mode=AutoRoutingMode(
        ...         model_routing_preference=ModelRoutingPreference.Balanced
        ...     )
        ... )

        >>> # Manual routing
        >>> mode = RoutingConfigMode(
        ...     manual_mode=ManualRoutingMode(model_name="gemini-2.0-flash-exp")
        ... )
    """

    def __init__(
        self,
        auto_mode: Optional[AutoRoutingMode] = None,
        manual_mode: Optional[ManualRoutingMode] = None,
    ) -> None:
        """Initialize routing mode.

        Exactly one of auto_mode or manual_mode must be provided.

        Args:
            auto_mode (Optional[AutoRoutingMode]):
                Automatic routing configuration
            manual_mode (Optional[ManualRoutingMode]):
                Manual routing configuration

        Raises:
            TypeError: If both or neither modes are provided
        """

class RoutingConfig:
    """Model routing configuration wrapper.

    Wraps the routing mode configuration.

    Examples:
        >>> config = RoutingConfig(
        ...     routing_config=RoutingConfigMode(
        ...         auto_mode=AutoRoutingMode(
        ...             model_routing_preference=ModelRoutingPreference.Balanced
        ...         )
        ...     )
        ... )
    """

    def __init__(
        self,
        routing_config: RoutingConfigMode,
    ) -> None:
        """Initialize routing configuration.

        Args:
            routing_config (RoutingConfigMode):
                The routing mode configuration
        """

    @property
    def routing_config(self) -> RoutingConfigMode:
        """The routing configuration mode."""

class PrebuiltVoiceConfig:
    """Configuration for prebuilt voice selection.

    Selects a prebuilt voice for text-to-speech generation.

    Examples:
        >>> config = PrebuiltVoiceConfig(voice_name="Puck")
    """

    def __init__(
        self,
        voice_name: str,
    ) -> None:
        """Initialize prebuilt voice configuration.

        Args:
            voice_name (str):
                Name of the prebuilt voice
        """

    @property
    def voice_name(self) -> str:
        """The voice name."""

class VoiceConfig:
    """Voice configuration for speech generation.

    Configures the voice to use for text-to-speech.

    Examples:
        >>> config = VoiceConfig(
        ...     prebuilt_voice_config=PrebuiltVoiceConfig(voice_name="Puck")
        ... )
    """

    def __init__(
        self,
        prebuilt_voice_config: PrebuiltVoiceConfig,
    ) -> None:
        """Initialize voice configuration.

        Args:
            prebuilt_voice_config (PrebuiltVoiceConfig):
                Prebuilt voice to use
        """

    @property
    def prebuilt_voice_config(self) -> PrebuiltVoiceConfig:
        """The prebuilt voice configuration."""

class SpeakerVoiceConfig:
    """Voice configuration for a specific speaker.

    Maps a speaker identifier to a voice configuration for multi-speaker
    text-to-speech.

    Examples:
        >>> config = SpeakerVoiceConfig(
        ...     speaker="Alice",
        ...     voice_config=VoiceConfig(
        ...         prebuilt_voice_config=PrebuiltVoiceConfig(voice_name="Puck")
        ...     )
        ... )
    """

    def __init__(
        self,
        speaker: str,
        voice_config: VoiceConfig,
    ) -> None:
        """Initialize speaker voice configuration.

        Args:
            speaker (str):
                Speaker identifier/name
            voice_config (VoiceConfig):
                Voice configuration for this speaker
        """

    @property
    def speaker(self) -> str:
        """The speaker identifier."""

    @property
    def voice_config(self) -> VoiceConfig:
        """The voice configuration."""

class MultiSpeakerVoiceConfig:
    """Configuration for multi-speaker text-to-speech.

    Configures voices for multiple speakers in a conversation or dialogue.

    Examples:
        >>> config = MultiSpeakerVoiceConfig(
        ...     speaker_voice_configs=[
        ...         SpeakerVoiceConfig(
        ...             speaker="Alice",
        ...             voice_config=VoiceConfig(
        ...                 prebuilt_voice_config=PrebuiltVoiceConfig(voice_name="Puck")
        ...             )
        ...         ),
        ...         SpeakerVoiceConfig(
        ...             speaker="Bob",
        ...             voice_config=VoiceConfig(
        ...                 prebuilt_voice_config=PrebuiltVoiceConfig(voice_name="Charon")
        ...             )
        ...         )
        ...     ]
        ... )
    """

    def __init__(
        self,
        speaker_voice_configs: List[SpeakerVoiceConfig],
    ) -> None:
        """Initialize multi-speaker configuration.

        Args:
            speaker_voice_configs (List[SpeakerVoiceConfig]):
                List of speaker voice configurations
        """

    @property
    def speaker_voice_configs(self) -> List[SpeakerVoiceConfig]:
        """The speaker voice configurations."""

class SpeechConfig:
    """Configuration for speech synthesis.

    Controls text-to-speech generation including voice selection and language.

    Examples:
        >>> # Single speaker
        >>> config = SpeechConfig(
        ...     voice_config=VoiceConfig(
        ...         prebuilt_voice_config=PrebuiltVoiceConfig(voice_name="Puck")
        ...     ),
        ...     language_code="en-US"
        ... )

        >>> # Multiple speakers
        >>> config = SpeechConfig(
        ...     multi_speaker_voice_config=MultiSpeakerVoiceConfig(...),
        ...     language_code="en-US"
        ... )
    """

    def __init__(
        self,
        voice_config: Optional[VoiceConfig] = None,
        multi_speaker_voice_config: Optional[MultiSpeakerVoiceConfig] = None,
        language_code: Optional[str] = None,
    ) -> None:
        """Initialize speech configuration.

        Args:
            voice_config (Optional[VoiceConfig]):
                Single voice configuration
            multi_speaker_voice_config (Optional[MultiSpeakerVoiceConfig]):
                Multi-speaker configuration
            language_code (Optional[str]):
                ISO 639-1 language code
        """

    @property
    def voice_config(self) -> Optional[VoiceConfig]:
        """The voice configuration."""

    @property
    def multi_speaker_voice_config(self) -> Optional[MultiSpeakerVoiceConfig]:
        """The multi-speaker configuration."""

    @property
    def language_code(self) -> Optional[str]:
        """The language code."""

class GenerationConfig:
    """Configuration for content generation behavior.

    Controls all aspects of how the model generates responses including
    sampling parameters, output format, modalities, and more.

    Examples:
        >>> # Basic text generation
        >>> config = GenerationConfig(
        ...     temperature=0.7,
        ...     max_output_tokens=1024,
        ...     top_p=0.95
        ... )

        >>> # Structured JSON output
        >>> config = GenerationConfig(
        ...     response_mime_type="application/json",
        ...     response_json_schema={"type": "object", ...},
        ...     temperature=0.3
        ... )

        >>> # Multi-modal with thinking
        >>> config = GenerationConfig(
        ...     response_modalities=[Modality.Text, Modality.Image],
        ...     thinking_config=ThinkingConfig(
        ...         include_thoughts=True,
        ...         thinking_level=ThinkingLevel.High
        ...     ),
        ...     temperature=0.5
        ... )
    """

    def __init__(
        self,
        stop_sequences: Optional[List[str]] = None,
        response_mime_type: Optional[str] = None,
        response_json_schema: Optional[Any] = None,
        response_modalities: Optional[List[Modality]] = None,
        thinking_config: Optional[GeminiThinkingConfig] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        candidate_count: Optional[int] = None,
        max_output_tokens: Optional[int] = None,
        response_logprobs: Optional[bool] = None,
        logprobs: Optional[int] = None,
        presence_penalty: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        seed: Optional[int] = None,
        audio_timestamp: Optional[bool] = None,
        media_resolution: Optional[MediaResolution] = None,
        speech_config: Optional[SpeechConfig] = None,
        enable_affective_dialog: Optional[bool] = None,
        enable_enhanced_civic_answers: Optional[bool] = None,
        image_config: Optional[ImageConfig] = None,
    ) -> None:
        """Initialize generation configuration.

        Args:
            stop_sequences (Optional[List[str]]):
                Sequences that stop generation
            response_mime_type (Optional[str]):
                MIME type for response (e.g., "application/json")
            response_json_schema (Optional[Any]):
                JSON schema for structured output
            response_modalities (Optional[List[Modality]]):
                Output modalities to include
            thinking_config (Optional[GeminiThinkingConfig]):
                Configuration for thinking/reasoning
            temperature (Optional[float]):
                Sampling temperature (0.0-2.0)
            top_p (Optional[float]):
                Nucleus sampling threshold
            top_k (Optional[int]):
                Top-k sampling threshold
            candidate_count (Optional[int]):
                Number of candidates to generate
            max_output_tokens (Optional[int]):
                Maximum tokens to generate
            response_logprobs (Optional[bool]):
                Whether to return log probabilities
            logprobs (Optional[int]):
                Number of top log probabilities to return
            presence_penalty (Optional[float]):
                Penalty for token presence (-2.0 to 2.0)
            frequency_penalty (Optional[float]):
                Penalty for token frequency (-2.0 to 2.0)
            seed (Optional[int]):
                Random seed for deterministic generation
            audio_timestamp (Optional[bool]):
                Whether to include audio timestamps
            media_resolution (Optional[MediaResolution]):
                Resolution for media processing
            speech_config (Optional[SpeechConfig]):
                Configuration for speech synthesis
            enable_affective_dialog (Optional[bool]):
                Enable emotion detection/adaptation
            enable_enhanced_civic_answers (Optional[bool]):
                Enable enhanced civic answers
            image_config (Optional[ImageConfig]):
                Configuration for image generation
        """

    @property
    def stop_sequences(self) -> Optional[List[str]]:
        """Stop sequences that halt generation."""

    @property
    def response_mime_type(self) -> Optional[str]:
        """The response MIME type."""

    @property
    def response_json_schema(self) -> Optional[Any]:
        """JSON schema for structured output."""

    @property
    def response_modalities(self) -> Optional[List[Modality]]:
        """Output modalities."""

    @property
    def thinking_config(self) -> Optional[GeminiThinkingConfig]:
        """Thinking configuration."""

    @property
    def temperature(self) -> Optional[float]:
        """Sampling temperature."""

    @property
    def top_p(self) -> Optional[float]:
        """Nucleus sampling threshold."""

    @property
    def top_k(self) -> Optional[int]:
        """Top-k sampling threshold."""

    @property
    def candidate_count(self) -> Optional[int]:
        """Number of candidates to generate."""

    @property
    def max_output_tokens(self) -> Optional[int]:
        """Maximum output tokens."""

    @property
    def response_logprobs(self) -> Optional[bool]:
        """Whether to return log probabilities."""

    @property
    def logprobs(self) -> Optional[int]:
        """Number of top log probabilities."""

    @property
    def presence_penalty(self) -> Optional[float]:
        """Presence penalty."""

    @property
    def frequency_penalty(self) -> Optional[float]:
        """Frequency penalty."""

    @property
    def seed(self) -> Optional[int]:
        """Random seed."""

    @property
    def audio_timestamp(self) -> Optional[bool]:
        """Whether to include audio timestamps."""

    @property
    def media_resolution(self) -> Optional[MediaResolution]:
        """Media resolution."""

    @property
    def speech_config(self) -> Optional[SpeechConfig]:
        """Speech configuration."""

    @property
    def enable_affective_dialog(self) -> Optional[bool]:
        """Whether affective dialog is enabled."""

    @property
    def image_config(self) -> Optional[ImageConfig]:
        """Image configuration."""

class ModelArmorConfig:
    """Configuration for Model Armor security filtering.

    Model Armor provides safety and security filtering for prompts and
    responses using customized templates.

    Examples:
        >>> config = ModelArmorConfig(
        ...     prompt_template_name="projects/my-project/locations/us/templates/strict",
        ...     response_template_name="projects/my-project/locations/us/templates/moderate"
        ... )
    """

    def __init__(
        self,
        prompt_template_name: Optional[str] = None,
        response_template_name: Optional[str] = None,
    ) -> None:
        """Initialize Model Armor configuration.

        Args:
            prompt_template_name (Optional[str]):
                Template for prompt screening
            response_template_name (Optional[str]):
                Template for response screening
        """

    @property
    def prompt_template_name(self) -> Optional[str]:
        """The prompt template name."""

    @property
    def response_template_name(self) -> Optional[str]:
        """The response template name."""

class FunctionCallingConfig:
    """Configuration for function calling behavior.

    Controls how the model handles function calls, including whether
    functions are required and which functions are allowed.

    Examples:
        >>> # Auto mode - model decides
        >>> config = FunctionCallingConfig(mode=Mode.Auto)

        >>> # Require specific functions
        >>> config = FunctionCallingConfig(
        ...     mode=Mode.Any,
        ...     allowed_function_names=["get_weather", "search_web"]
        ... )

        >>> # Disable function calling
        >>> config = FunctionCallingConfig(mode=Mode.None_Mode)
    """

    def __init__(
        self,
        mode: Optional[Mode] = None,
        allowed_function_names: Optional[List[str]] = None,
    ) -> None:
        """Initialize function calling configuration.

        Args:
            mode (Optional[Mode]):
                Function calling mode
            allowed_function_names (Optional[List[str]]):
                List of allowed function names (for ANY mode)
        """

    @property
    def mode(self) -> Optional[Mode]:
        """The function calling mode."""

    @property
    def allowed_function_names(self) -> Optional[List[str]]:
        """Allowed function names."""

class LatLng:
    """Geographic coordinates.

    Represents a latitude/longitude pair for location-based features.

    Examples:
        >>> # New York City coordinates
        >>> coords = LatLng(latitude=40.7128, longitude=-74.0060)
    """

    def __init__(
        self,
        latitude: float,
        longitude: float,
    ) -> None:
        """Initialize coordinates.

        Args:
            latitude (float):
                Latitude in degrees
            longitude (float):
                Longitude in degrees
        """

    @property
    def latitude(self) -> float:
        """The latitude."""

    @property
    def longitude(self) -> float:
        """The longitude."""

class RetrievalConfig:
    """Configuration for retrieval operations.

    Provides location and language context for retrieval tools.

    Examples:
        >>> config = RetrievalConfig(
        ...     lat_lng=LatLng(latitude=37.7749, longitude=-122.4194),
        ...     language_code="en-US"
        ... )
    """

    def __init__(
        self,
        lat_lng: LatLng,
        language_code: str,
    ) -> None:
        """Initialize retrieval configuration.

        Args:
            lat_lng (LatLng):
                Geographic coordinates
            language_code (str):
                Language code
        """

    @property
    def lat_lng(self) -> LatLng:
        """The geographic coordinates."""

    @property
    def language_code(self) -> str:
        """The language code."""

class ToolConfig:
    """Configuration for tool usage.

    Controls function calling and retrieval behavior across all tools.

    Examples:
        >>> config = ToolConfig(
        ...     function_calling_config=FunctionCallingConfig(mode=Mode.Auto),
        ...     retrieval_config=RetrievalConfig(
        ...         lat_lng=LatLng(latitude=37.7749, longitude=-122.4194),
        ...         language_code="en-US"
        ...     )
        ... )
    """

    def __init__(
        self,
        function_calling_config: Optional[FunctionCallingConfig] = None,
        retrieval_config: Optional[RetrievalConfig] = None,
    ) -> None:
        """Initialize tool configuration.

        Args:
            function_calling_config (Optional[FunctionCallingConfig]):
                Function calling configuration
            retrieval_config (Optional[RetrievalConfig]):
                Retrieval configuration
        """

    @property
    def function_calling_config(self) -> Optional[FunctionCallingConfig]:
        """The function calling configuration."""

    @property
    def retrieval_config(self) -> Optional[RetrievalConfig]:
        """The retrieval configuration."""

class GeminiSettings:
    """Settings for Gemini/Google API requests.

    Comprehensive configuration for all aspects of model behavior including
    generation, safety, tools, and more.

    Examples:
        >>> settings = GeminiSettings(
        ...     generation_config=GenerationConfig(
        ...         temperature=0.7,
        ...         max_output_tokens=1024
        ...     ),
        ...     safety_settings=[
        ...         SafetySetting(
        ...             category=HarmCategory.HarmCategoryHateSpeech,
        ...             threshold=HarmBlockThreshold.BlockMediumAndAbove
        ...         )
        ...     ],
        ...     tool_config=ToolConfig(
        ...         function_calling_config=FunctionCallingConfig(mode=Mode.Auto)
        ...     )
        ... )
    """

    def __init__(
        self,
        labels: Optional[Dict[str, str]] = None,
        tool_config: Optional[ToolConfig] = None,
        generation_config: Optional[GenerationConfig] = None,
        safety_settings: Optional[List[SafetySetting]] = None,
        model_armor_config: Optional[ModelArmorConfig] = None,
        extra_body: Optional[Any] = None,
        cached_content: Optional[str] = None,
        tools: Optional[List[GeminiTool]] = None,
    ) -> None:
        """Initialize Gemini settings.

        Args:
            labels (Optional[Dict[str, str]]):
                Metadata labels
            tool_config (Optional[ToolConfig]):
                Tool configuration
            generation_config (Optional[GenerationConfig]):
                Generation configuration
            safety_settings (Optional[List[SafetySetting]]):
                Safety filter settings
            model_armor_config (Optional[ModelArmorConfig]):
                Model Armor configuration
            extra_body (Optional[Any]):
                Additional request parameters
            cached_content (Optional[str]):
                Cached content resource name
            tools (Optional[List["Tool"]]):
                Tools available to the model
        """

    @property
    def labels(self) -> Optional[Dict[str, str]]:
        """Metadata labels."""

    @property
    def tool_config(self) -> Optional[ToolConfig]:
        """Tool configuration."""

    @property
    def generation_config(self) -> Optional[GenerationConfig]:
        """Generation configuration."""

    @property
    def safety_settings(self) -> Optional[List[SafetySetting]]:
        """Safety settings."""

    @property
    def model_armor_config(self) -> Optional[ModelArmorConfig]:
        """Model Armor configuration."""

    @property
    def extra_body(self) -> Optional[Dict[str, Any]]:
        """Additional request parameters."""

    @property
    def cached_content(self) -> Optional[str]:
        """Cached content resource name."""

    @property
    def tools(self) -> Optional[List[GeminiTool]]:
        """Available tools."""

    def __str__(self) -> str:
        """String representation."""

    def model_dump(self) -> Dict[str, Any]:
        """Convert settings to dictionary."""

    def settings_type(self) -> str:
        """Get settings type identifier."""

class FileData:
    """URI-based media data reference.

    References media stored in Google Cloud Storage or other URIs.

    Examples:
        >>> file_data = FileData(
        ...     mime_type="image/png",
        ...     file_uri="gs://my-bucket/image.png",
        ...     display_name="Example Image"
        ... )
    """

    def __init__(
        self,
        mime_type: str,
        file_uri: str,
        display_name: Optional[str] = None,
    ) -> None:
        """Initialize file data reference.

        Args:
            mime_type (str):
                IANA MIME type
            file_uri (str):
                URI to the file (e.g., gs:// URL)
            display_name (Optional[str]):
                Optional display name
        """

    @property
    def mime_type(self) -> str:
        """The MIME type."""

    @property
    def file_uri(self) -> str:
        """The file URI."""

    @property
    def display_name(self) -> Optional[str]:
        """The display name."""

class Blob:
    """Inline binary data.

    Contains raw binary data encoded in base64.

    Examples:
        >>> import base64
        >>> image_data = base64.b64encode(image_bytes).decode('utf-8')
        >>> blob = Blob(
        ...     mime_type="image/png",
        ...     data=image_data,
        ...     display_name="Example Image"
        ... )
    """

    def __init__(
        self,
        mime_type: str,
        data: str,
        display_name: Optional[str] = None,
    ) -> None:
        """Initialize binary data blob.

        Args:
            mime_type (str):
                IANA MIME type
            data (str):
                Base64-encoded binary data
            display_name (Optional[str]):
                Optional display name
        """

    @property
    def mime_type(self) -> str:
        """The MIME type."""

    @property
    def data(self) -> str:
        """The base64-encoded data."""

    @property
    def display_name(self) -> Optional[str]:
        """The display name."""

class PartialArgs:
    """Partial function call arguments for streaming.

    Represents incrementally streamed function call arguments.

    Examples:
        >>> args = PartialArgs(
        ...     json_path="$.location",
        ...     string_value="New York",
        ...     will_continue=True
        ... )
    """

    def __init__(
        self,
        json_path: str,
        will_continue: Optional[bool] = None,
        null_value: Optional[bool] = None,
        number_value: Optional[float] = None,
        string_value: Optional[str] = None,
        bool_value: Optional[bool] = None,
    ) -> None:
        """Initialize partial arguments.

        Args:
            json_path (str):
                JSON Path (RFC 9535) to the argument
            will_continue (Optional[bool]):
                Whether more parts follow for this path
            null_value (Optional[bool]):
                Null value
            number_value (Optional[float]):
                Numeric value
            string_value (Optional[str]):
                String value
            bool_value (Optional[bool]):
                Boolean value
        """

    @property
    def json_path(self) -> str:
        """The JSON path."""

    @property
    def will_continue(self) -> Optional[bool]:
        """Whether more parts follow."""

    @property
    def null_value(self) -> Optional[bool]:
        """Null value indicator."""

    @property
    def number_value(self) -> Optional[float]:
        """Numeric value."""

    @property
    def string_value(self) -> Optional[str]:
        """String value."""

    @property
    def bool_value(self) -> Optional[bool]:
        """Boolean value."""

class FunctionCall:
    """Function call request from the model.

    Represents a function that the model wants to call, including
    the function name and arguments.

    Examples:
        >>> call = FunctionCall(
        ...     name="get_weather",
        ...     args={"location": "San Francisco", "units": "celsius"},
        ...     id="call_123"
        ... )
    """

    def __init__(
        self,
        name: str,
        id: Optional[str] = None,
        args: Optional[Dict[str, Any]] = None,
        will_continue: Optional[bool] = None,
        partial_args: Optional[List[PartialArgs]] = None,
    ) -> None:
        """Initialize function call.

        Args:
            name: Function name to call
            id (Optional[str]):
                Unique call identifier
            args (Optional[Dict[str, Any]]):
                Function arguments as dictionary
            will_continue (Optional[bool]):
                Whether this is the final part of the call
            partial_args (Optional[List[PartialArgs]]):
                Incrementally streamed arguments
        """

    @property
    def name(self) -> str:
        """The function name."""

    @property
    def id(self) -> Optional[str]:
        """The call identifier."""

    @property
    def args(self) -> Optional[Dict[str, Any]]:
        """The function arguments."""

    @property
    def will_continue(self) -> Optional[bool]:
        """Whether more parts follow."""

    @property
    def partial_args(self) -> Optional[List[PartialArgs]]:
        """Partial arguments."""

class FunctionResponse:
    """Function execution result.

    Contains the result of executing a function call.
    """

    @property
    def name(self) -> str:
        """The function name."""

    @property
    def response(self) -> Dict[str, Any]:
        """The function response."""

class ExecutableCode:
    """Executable code generated by the model.

    Contains code that can be executed to perform computations.
    """

    @property
    def language(self) -> Language:
        """The programming language."""

    @property
    def code(self) -> str:
        """The code."""

class CodeExecutionResult:
    """Result of code execution.

    Contains the outcome and output from executing code.

    Examples:
        >>> result = CodeExecutionResult(
        ...     outcome=Outcome.OutcomeOk,
        ...     output="4\\n"
        ... )

        >>> # Error result
        >>> result = CodeExecutionResult(
        ...     outcome=Outcome.OutcomeFailed,
        ...     output="NameError: name 'x' is not defined"
        ... )
    """

    @property
    def outcome(self) -> Outcome:
        """The execution outcome."""

    @property
    def output(self) -> Optional[str]:
        """The output."""

class VideoMetadata:
    """Metadata for video content.

    Specifies time ranges and frame rates for video processing.
    """

    @property
    def start_offset(self) -> Optional[str]:
        """The start offset."""

    @property
    def end_offset(self) -> Optional[str]:
        """The end offset."""

class PartMetadata:
    """Custom metadata for content parts.

    Allows arbitrary structured metadata to be attached to parts.

    Examples:
        >>> metadata = PartMetadata(
        ...     struct_={"custom_field": "value", "priority": 1}
        ... )
    """

    def __init__(
        self,
        struct_: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize part metadata.

        Args:
            struct_: Arbitrary metadata dictionary
        """

class Part:
    """A part of a multi-part message.

    Represents a single piece of content which can be text, media, function
    calls, or other data types.

    Examples:
        >>> # Text part
        >>> part = Part(data="Hello, world!")

        >>> # Image part
        >>> part = Part(
        ...     data=Blob(
        ...         mime_type="image/png",
        ...         data=base64_encoded_data
        ...     )
        ... )

        >>> # Function call part
        >>> part = Part(
        ...     data=FunctionCall(
        ...         name="get_weather",
        ...         args={"location": "NYC"}
        ...     )
        ... )

        >>> # Part with metadata
        >>> part = Part(
        ...     data="Analyze this carefully",
        ...     thought=True,
        ...     media_resolution=MediaResolution.MediaResolutionHigh
        ... )
    """

    def __init__(
        self,
        data: Union[
            str,
            Blob,
            FileData,
            FunctionCall,
            FunctionResponse,
            ExecutableCode,
            CodeExecutionResult,
        ],
        thought: Optional[bool] = None,
        thought_signature: Optional[str] = None,
        part_metadata: Optional[PartMetadata] = None,
        media_resolution: Optional[MediaResolution] = None,
        video_metadata: Optional[VideoMetadata] = None,
    ) -> None:
        """Initialize a content part.

        Args:
            data (Union[str, Blob, FileData, FunctionCall, FunctionResponse, ExecutableCode, CodeExecutionResult]):
                The content data (text, blob, function call, etc.)
            thought (Optional[bool]):
                Whether this is part of the model's reasoning
            thought_signature (Optional[str]):
                Signature for reusing thoughts
            part_metadata (Optional[PartMetadata]):
                Custom metadata
            media_resolution (Optional[MediaResolution]):
                Media resolution level
            video_metadata (Optional[VideoMetadata]):
                Video-specific metadata
        """

    @property
    def thought(self) -> Optional[bool]:
        """Whether this is a thought/reasoning part."""

    @property
    def thought_signature(self) -> Optional[str]:
        """The thought signature."""

    @property
    def part_metadata(self) -> Optional[PartMetadata]:
        """Custom metadata."""

    @property
    def media_resolution(self) -> Optional[MediaResolution]:
        """Media resolution."""

    @property
    def data(
        self,
    ) -> Union[
        str,
        Blob,
        FileData,
        FunctionCall,
        FunctionResponse,
        ExecutableCode,
        CodeExecutionResult,
    ]:
        """The content data."""

    @property
    def video_metadata(self) -> Optional[VideoMetadata]:
        """Video metadata."""

class GeminiContent:
    """Multi-part message content.

    Represents a complete message from a user or model, consisting of one
    or more parts. This is the fundamental message structure for Gemini API.

    Examples:
        >>> # Simple text message
        >>> content = GeminiContent(
        ...     role="user",
        ...     parts="What's the weather in San Francisco?"
        ... )

        >>> # Multi-part message with image
        >>> content = GeminiContent(
        ...     role="user",
        ...     parts=[
        ...         "What's in this image?",
        ...         Blob(mime_type="image/png", data=image_data)
        ...     ]
        ... )

        >>> # Function call response
        >>> content = GeminiContent(
        ...     role="model",
        ...     parts=[
        ...         FunctionCall(
        ...             name="get_weather",
        ...             args={"location": "San Francisco"}
        ...         )
        ...     ]
        ... )

        >>> # Function result
        >>> content = GeminiContent(
        ...     role="function",
        ...     parts=[
        ...         FunctionResponse(
        ...             name="get_weather",
        ...             response={"output": {"temperature": 72}}
        ...         )
        ...     ]
        ... )
    """

    def __init__(
        self,
        parts: Union[
            str,
            Part,
            List[
                Union[
                    str,
                    Part,
                    Blob,
                    FileData,
                    FunctionCall,
                    FunctionResponse,
                    ExecutableCode,
                    CodeExecutionResult,
                ]
            ],
        ],
        role: Optional[str] = None,
    ) -> None:
        """Initialize message content.

        Args:
            parts (Union[str, Part, List[Union[str, Part, Blob, FileData, FunctionCall, FunctionResponse,
            ExecutableCode, CodeExecutionResult]]]):
                Content from typing import Any, Dict, List, Optional, Union from the message
            role (Optional[str]):
                Role of the message sender (e.g., "user", "model", "function")
        """

    @property
    def text(self) -> str:
        """Get the text content of the first part, if available. Returns
        an empty string if the first part is not text.
        This is meant for convenience when working with simple text messages.
        """

    @property
    def role(self) -> Optional[str]:
        """The role of the message sender."""

    @property
    def parts(self) -> List[Part]:
        """The message parts."""

    def bind(
        self,
        name: Optional[str] = None,
        value: Optional[str | int | float | bool | list] = None,
    ) -> "GeminiContent":
        """Bind variables to the message content.
        Args:
            name (Optional[str]):
                The variable name to bind.
            value (Optional[Union[str, int, float, bool, list]]):
                The variable value to bind.
        Returns:
            GeminiContent:
                New content with variables bound.
        """

    def bind_mut(
        self,
        name: Optional[str] = None,
        value: Optional[str | int | float | bool | list] = None,
    ) -> None:
        """Bind variables to the message content in place.
        Args:
            name (Optional[str]):
                The variable name to bind.
            value (Optional[Union[str, int, float, bool, list]]):
                The variable value to bind.
        Returns:
            None
        """

    def model_dump(self) -> dict:
        """Dump the message to a dictionary."""

class FunctionDeclaration:
    """Function declaration for tool use.

    Defines a function that the model can call, including its name,
    description, parameters, and return type.

    Examples:
        >>> func = FunctionDeclaration(
        ...     name="get_weather",
        ...     description="Get current weather for a location",
        ...     parameters=Schema(
        ...         type=SchemaType.Object,
        ...         properties={
        ...             "location": Schema(type=SchemaType.String),
        ...             "units": Schema(
        ...                 type=SchemaType.String,
        ...                 enum_=["celsius", "fahrenheit"]
        ...             )
        ...         },
        ...         required=["location"]
        ...     )
        ... )
    """

    @property
    def name(self) -> str:
        """The function name."""

    @property
    def description(self) -> str:
        """The function description."""

    @property
    def behavior(self) -> Optional[Behavior]:
        """Execution behavior (blocking/non-blocking)."""

    @property
    def parameters(self) -> Optional[Schema]:
        """Parameter schema."""

    @property
    def parameters_json_schema(self) -> Optional[Any]:
        """Parameters as raw JSON schema."""

    @property
    def response(self) -> Optional[Schema]:
        """Response schema."""

    @property
    def response_json_schema(self) -> Optional[Any]:
        """Response as raw JSON schema."""

class DataStoreSpec:
    """Specification for a Vertex AI Search datastore.

    Defines a datastore to search with optional filtering.

    Examples:
        >>> spec = DataStoreSpec(
        ...     data_store="projects/my-project/locations/us/collections/default/dataStores/my-store",
        ...     filter="category:electronics"
        ... )
    """

    def __init__(
        self,
        data_store: str,
        filter: Optional[str] = None,
    ) -> None:
        """Initialize datastore specification.

        Args:
            data_store (str):
                Full resource name of the datastore
            filter (Optional[str]):
                Optional filter expression
        """

    @property
    def data_store(self) -> str:
        """The datastore resource name."""

    @property
    def filter(self) -> Optional[str]:
        """The filter expression."""

class VertexAISearch:
    """Vertex AI Search retrieval configuration.

    Configures retrieval from Vertex AI Search datastores or engines.

    Examples:
        >>> # Using a datastore
        >>> search = VertexAISearch(
        ...     datastore="projects/my-project/locations/us/collections/default/dataStores/my-store",
        ...     max_results=5
        ... )

        >>> # Using an engine with multiple datastores
        >>> search = VertexAISearch(
        ...     engine="projects/my-project/locations/us/collections/default/engines/my-engine",
        ...     data_store_specs=[
        ...         DataStoreSpec(data_store="store1", filter="category:a"),
        ...         DataStoreSpec(data_store="store2", filter="category:b")
        ...     ]
        ... )
    """

    def __init__(
        self,
        datastore: Optional[str] = None,
        engine: Optional[str] = None,
        max_results: Optional[int] = None,
        filter: Optional[str] = None,
        data_store_specs: Optional[List[DataStoreSpec]] = None,
    ) -> None:
        """Initialize Vertex AI Search configuration.

        Args:
            datastore (Optional[str]):
                Datastore resource name
            engine (Optional[str]):
                Engine resource name
            max_results (Optional[int]):
                Maximum number of results (default 10, max 10)
            filter (Optional[str]):
                Filter expression
            data_store_specs (Optional[List[DataStoreSpec]]):
                Datastore specifications (for engines)
        """

    @property
    def datastore(self) -> Optional[str]:
        """The datastore resource name."""

    @property
    def engine(self) -> Optional[str]:
        """The engine resource name."""

    @property
    def max_results(self) -> Optional[int]:
        """Maximum results to return."""

    @property
    def filter(self) -> Optional[str]:
        """The filter expression."""

    @property
    def data_store_specs(self) -> Optional[List[DataStoreSpec]]:
        """Datastore specifications."""

class RagResource:
    """RAG corpus and file specification.

    Specifies which RAG corpus and optionally which files to use.

    Examples:
        >>> # Use entire corpus
        >>> resource = RagResource(
        ...     rag_corpus="projects/my-project/locations/us/ragCorpora/my-corpus"
        ... )

        >>> # Use specific files from corpus
        >>> resource = RagResource(
        ...     rag_corpus="projects/my-project/locations/us/ragCorpora/my-corpus",
        ...     rag_file_ids=["file1", "file2"]
        ... )
    """

    def __init__(
        self,
        rag_corpus: Optional[str] = None,
        rag_file_ids: Optional[List[str]] = None,
    ) -> None:
        """Initialize RAG resource.

        Args:
            rag_corpus (Optional[str]):
                RAG corpus resource name
            rag_file_ids (Optional[List[str]]):
                List of file IDs within the corpus
        """

    @property
    def rag_corpus(self) -> Optional[str]:
        """The RAG corpus resource name."""

    @property
    def rag_file_ids(self) -> Optional[List[str]]:
        """The file IDs."""

class Filter:
    """Filtering configuration for RAG retrieval.

    Configures metadata and vector-based filtering.

    Examples:
        >>> # Metadata filtering
        >>> filter = Filter(
        ...     metadata_filter="category = 'technical'",
        ...     vector_similarity_threshold=0.7
        ... )
    """

    def __init__(
        self,
        metadata_filter: Optional[str] = None,
        vector_distance_threshold: Optional[float] = None,
        vector_similarity_threshold: Optional[float] = None,
    ) -> None:
        """Initialize filter configuration.

        Args:
            metadata_filter (Optional[str]):
                Metadata filter expression
            vector_distance_threshold (Optional[float]):
                Maximum vector distance
            vector_similarity_threshold (Optional[float]):
                Minimum vector similarity
        """

    @property
    def metadata_filter(self) -> Optional[str]:
        """The metadata filter expression."""

    @property
    def vector_distance_threshold(self) -> Optional[float]:
        """Maximum vector distance threshold."""

    @property
    def vector_similarity_threshold(self) -> Optional[float]:
        """Minimum vector similarity threshold."""

class RankService:
    """Rank service configuration.

    Configures the ranking service for RAG results.

    Examples:
        >>> service = RankService(model_name="semantic-ranker-512@latest")
    """

    def __init__(
        self,
        model_name: Optional[str] = None,
    ) -> None:
        """Initialize rank service.

        Args:
            model_name (Optional[str]):
                Model name for ranking
        """

    @property
    def model_name(self) -> Optional[str]:
        """The ranking model name."""

class LlmRanker:
    """LLM-based ranker configuration.

    Uses an LLM to rank RAG results.

    Examples:
        >>> ranker = LlmRanker(model_name="gemini-1.5-flash")
    """

    def __init__(
        self,
        model_name: Optional[str] = None,
    ) -> None:
        """Initialize LLM ranker.

        Args:
            model_name (Optional[str]):
                Model name for ranking
        """

    @property
    def model_name(self) -> Optional[str]:
        """The ranking model name."""

class RankingConfig:
    """Union type for ranking configuration.

    Represents either rank service or LLM ranker configuration.

    Examples:
        >>> # Use rank service
        >>> config = RankingConfig.RankService(
        ...     RankService(model_name="semantic-ranker-512@latest")
        ... )

        >>> # Use LLM ranker
        >>> config = RankingConfig.LlmRanker(
        ...     LlmRanker(model_name="gemini-1.5-flash")
        ... )
    """

class Ranking:
    """Ranking and reranking configuration.

    Configures how RAG results are ranked.

    Examples:
        >>> # Using rank service
        >>> ranking = Ranking(
        ...     rank_service=RankService(model_name="semantic-ranker-512@latest")
        ... )

        >>> # Using LLM ranker
        >>> ranking = Ranking(
        ...     llm_ranker=LlmRanker(model_name="gemini-1.5-flash")
        ... )
    """

    def __init__(
        self,
        rank_service: Optional[RankService] = None,
        llm_ranker: Optional[LlmRanker] = None,
    ) -> None:
        """Initialize ranking configuration.

        Exactly one of rank_service or llm_ranker must be provided.

        Args:
            rank_service (Optional[RankService]):
                Rank service configuration
            llm_ranker (Optional[LlmRanker]):
                LLM ranker configuration

        Raises:
            TypeError: If both or neither are provided
        """

    @property
    def ranking_config(self) -> RankingConfig:
        """The ranking configuration."""

class RagRetrievalConfig:
    """Configuration for RAG retrieval behavior.

    Controls filtering, ranking, and other retrieval parameters.

    Examples:
        >>> config = RagRetrievalConfig(
        ...     top_k=5,
        ...     filter=Filter(metadata_filter="category='technical'"),
        ...     ranking=Ranking(
        ...         rank_service=RankService(model_name="semantic-ranker-512@latest")
        ...     )
        ... )
    """

    def __init__(
        self,
        top_k: Optional[int] = None,
        filter: Optional[Filter] = None,
        ranking: Optional[Ranking] = None,
    ) -> None:
        """Initialize RAG retrieval configuration.

        Args:
            top_k (Optional[int]):
                Number of top results to retrieve
            filter (Optional[Filter]):
                Filtering configuration
            ranking (Optional[Ranking]):
                Ranking configuration
        """

    @property
    def top_k(self) -> Optional[int]:
        """Number of top results."""

    @property
    def filter(self) -> Optional[Filter]:
        """Filter configuration."""

    @property
    def ranking(self) -> Optional[Ranking]:
        """Ranking configuration."""

class VertexRagStore:
    """Vertex RAG Store retrieval configuration.

    Configures retrieval from Vertex RAG Store.

    Examples:
        >>> store = VertexRagStore(
        ...     rag_resources=[
        ...         RagResource(
        ...             rag_corpus="projects/my-project/locations/us/ragCorpora/my-corpus"
        ...         )
        ...     ],
        ...     rag_retrieval_config=RagRetrievalConfig(top_k=5),
        ...     similarity_top_k=10
        ... )
    """

    @property
    def rag_resources(self) -> Optional[List[RagResource]]:
        """RAG resources to use."""

    @property
    def rag_retrieval_config(self) -> Optional[RagRetrievalConfig]:
        """Retrieval configuration."""

    @property
    def similarity_top_k(self) -> Optional[int]:
        """Number of similar results."""

    @property
    def vector_distance_threshold(self) -> Optional[float]:
        """Vector distance threshold."""

class SimpleSearchParams:
    """Parameters for simple search API.

    This type has no configuration fields.

    Examples:
        >>> params = SimpleSearchParams()
    """

    def __init__(self) -> None:
        """Initialize simple search parameters."""

class ElasticSearchParams:
    """Parameters for Elasticsearch API.

    Configures Elasticsearch index and search template.

    Examples:
        >>> params = ElasticSearchParams(
        ...     index="my-index",
        ...     search_template="my-template",
        ...     num_hits=10
        ... )
    """

    def __init__(
        self,
        index: str,
        search_template: str,
        num_hits: Optional[int] = None,
    ) -> None:
        """Initialize Elasticsearch parameters.

        Args:
            index (str):
                Elasticsearch index name
            search_template (str):
                Search template name
            num_hits (Optional[int]):
                Number of hits to request
        """

    @property
    def index(self) -> str:
        """The Elasticsearch index."""

    @property
    def search_template(self) -> str:
        """The search template."""

    @property
    def num_hits(self) -> Optional[int]:
        """Number of hits."""

class ApiKeyConfig:
    """API key authentication configuration.

    Configures API key authentication for external APIs.

    Examples:
        >>> config = ApiKeyConfig(
        ...     name="X-API-Key",
        ...     api_key_secret="projects/my-project/secrets/api-key",
        ...     http_element_location=HttpElementLocation.HttpInHeader
        ... )
    """

    def __init__(
        self,
        name: Optional[str] = None,
        api_key_secret: Optional[str] = None,
        api_key_string: Optional[str] = None,
        http_element_location: Optional[HttpElementLocation] = None,
    ) -> None:
        """Initialize API key configuration.

        Args:
            name (Optional[str]):
                Name of the API key parameter
            api_key_secret (Optional[str]):
                Secret manager resource name
            api_key_string (Optional[str]):
                Direct API key string
            http_element_location (Optional[HttpElementLocation]):
                Where to place the API key
        """

    @property
    def name(self) -> Optional[str]:
        """The API key parameter name."""

    @property
    def api_key_secret(self) -> Optional[str]:
        """The secret resource name."""

    @property
    def api_key_string(self) -> Optional[str]:
        """The direct API key string."""

    @property
    def http_element_location(self) -> Optional[HttpElementLocation]:
        """Where to place the API key."""

class HttpBasicAuthConfig:
    """HTTP Basic authentication configuration.

    Configures HTTP Basic authentication for external APIs.

    Examples:
        >>> config = HttpBasicAuthConfig(
        ...     credential_secret="projects/my-project/secrets/credentials"
        ... )
    """

    def __init__(
        self,
        credential_secret: str,
    ) -> None:
        """Initialize HTTP Basic auth configuration.

        Args:
            credential_secret (str):
                Secret manager resource name for credentials
        """

    @property
    def credential_secret(self) -> str:
        """The credential secret resource name."""

class GoogleServiceAccountConfig:
    """Google Service Account authentication configuration.

    Configures service account authentication.

    Examples:
        >>> config = GoogleServiceAccountConfig(
        ...     service_account="my-service-account@my-project.iam.gserviceaccount.com"
        ... )
    """

    def __init__(
        self,
        service_account: Optional[str] = None,
    ) -> None:
        """Initialize service account configuration.

        Args:
            service_account (Optional[str]):
                Service account email
        """

    @property
    def service_account(self) -> Optional[str]:
        """The service account email."""

class OauthConfigValue:
    """Union type for OAuth configuration.

    Represents either an access token or service account OAuth configuration.

    Examples:
        >>> # Using access token
        >>> config = OauthConfigValue(access_token="ya29....")

        >>> # Using service account
        >>> config = OauthConfigValue(
        ...     service_account="my-sa@project.iam.gserviceaccount.com"
        ... )
    """

    def __init__(
        self,
        access_token: Optional[str] = None,
        service_account: Optional[str] = None,
    ) -> None:
        """Initialize OAuth configuration value.

        Exactly one of access_token or service_account must be provided.

        Args:
            access_token (Optional[str]):
                OAuth access token
            service_account (Optional[str]):
                Service account email

        Raises:
            TypeError: If both or neither are provided
        """

class OauthConfig:
    """OAuth authentication configuration.

    Configures OAuth authentication for external APIs.

    Examples:
        >>> config = OauthConfig(access_token="ya29....")
    """

    def __init__(
        self,
        access_token: Optional[str] = None,
        service_account: Optional[str] = None,
    ) -> None:
        """Initialize OAuth configuration.

        Args:
            access_token (Optional[str]):
                OAuth access token
            service_account (Optional[str]):
                Service account email

        Raises:
            TypeError: If configuration is invalid
        """

    @property
    def oauth_config(self) -> OauthConfigValue:
        """The OAuth configuration value."""

class OidcConfig:
    """OIDC authentication configuration.

    Configures OIDC authentication for external APIs.

    Examples:
        >>> config = OidcConfig(id_token="eyJhbGc...")
    """

    def __init__(
        self,
        id_token: Optional[str] = None,
        service_account: Optional[str] = None,
    ) -> None:
        """Initialize OIDC configuration.

        Args:
            id_token (Optional[str]):
                OIDC ID token
            service_account (Optional[str]):
                Service account email

        Raises:
            TypeError: If configuration is invalid
        """

    @property
    def oidc_config(self) -> Any:
        """The OIDC configuration value."""

class AuthConfigValue:
    """Union type for authentication configuration.

    Represents one of several authentication methods.

    Examples:
        >>> # API key auth
        >>> config = AuthConfigValue(
        ...     api_key_config=ApiKeyConfig(...)
        ... )

        >>> # OAuth
        >>> config = AuthConfigValue(
        ...     oauth_config=OauthConfig(...)
        ... )
    """

    def __init__(
        self,
        api_key_config: Optional[ApiKeyConfig] = None,
        http_basic_auth_config: Optional[HttpBasicAuthConfig] = None,
        google_service_account_config: Optional[GoogleServiceAccountConfig] = None,
        oauth_config: Optional[OauthConfig] = None,
        oidc_config: Optional[OidcConfig] = None,
    ) -> None:
        """Initialize auth configuration value.

        Exactly one configuration type must be provided.

        Args:
            api_key_config (Optional[ApiKeyConfig]):
                API key authentication
            http_basic_auth_config (Optional[HttpBasicAuthConfig]):
                HTTP Basic authentication
            google_service_account_config (Optional[GoogleServiceAccountConfig]):
                Service account authentication
            oauth_config (Optional[OauthConfig]):
                OAuth authentication
            oidc_config (Optional[OidcConfig]):
                OIDC authentication

        Raises:
            TypeError: If configuration is invalid
        """

class AuthConfig:
    """Authentication configuration wrapper.

    Wraps authentication type and configuration.

    Examples:
        >>> config = AuthConfig(
        ...     auth_type=AuthType.ApiKeyAuth,
        ...     auth_config=AuthConfigValue(
        ...         api_key_config=ApiKeyConfig(...)
        ...     )
        ... )
    """

    @property
    def auth_type(self) -> AuthType:
        """The authentication type."""

    @property
    def auth_config(self) -> AuthConfigValue:
        """The authentication configuration."""

class ExternalApi:
    """External API retrieval configuration.

    Configures retrieval from external APIs.

    Examples:
        >>> api = ExternalApi(
        ...     api_spec=ApiSpecType.ElasticSearch,
        ...     endpoint="https://my-es-cluster.com",
        ...     auth_config=AuthConfig(...),
        ...     elastic_search_params=ElasticSearchParams(...)
        ... )
    """

    def __init__(
        self,
        api_spec: ApiSpecType,
        endpoint: str,
        auth_config: Optional[AuthConfig] = None,
        simple_search_params: Optional[SimpleSearchParams] = None,
        elastic_search_params: Optional[ElasticSearchParams] = None,
    ) -> None:
        """Initialize external API configuration.

        Args:
            api_spec (ApiSpecType):
                API specification type
            endpoint (str):
                API endpoint URL
            auth_config (Optional[AuthConfig]):
                Authentication configuration
            simple_search_params (Optional[SimpleSearchParams]):
                Simple search parameters
            elastic_search_params (Optional[ElasticSearchParams]):
                Elasticsearch parameters
        """

    @property
    def api_spec(self) -> ApiSpecType:
        """The API specification type."""

    @property
    def endpoint(self) -> str:
        """The API endpoint."""

    @property
    def auth_config(self) -> Optional[AuthConfig]:
        """The authentication configuration."""

    @property
    def params(self) -> Optional[Union[SimpleSearchParams, ElasticSearchParams]]:
        """The API parameters."""

class RetrievalSource:
    """Union type for retrieval sources.

    Represents one of several retrieval source types.

    Examples:
        >>> # Vertex AI Search
        >>> source = RetrievalSource(
        ...     vertex_ai_search=VertexAISearch(...)
        ... )

        >>> # RAG Store
        >>> source = RetrievalSource(
        ...     vertex_rag_store=VertexRagStore(...)
        ... )

        >>> # External API
        >>> source = RetrievalSource(
        ...     external_api=ExternalApi(...)
        ... )
    """

    def __init__(
        self,
        vertex_ai_search: Optional[VertexAISearch] = None,
        vertex_rag_store: Optional[VertexRagStore] = None,
        external_api: Optional[ExternalApi] = None,
    ) -> None:
        """Initialize retrieval source.

        Exactly one source type must be provided.

        Args:
            vertex_ai_search (Optional[VertexAISearch]):
                Vertex AI Search configuration
            vertex_rag_store (Optional[VertexRagStore]):
                Vertex RAG Store configuration
            external_api (Optional[ExternalApi]):
                External API configuration

        Raises:
            TypeError: If configuration is invalid
        """

class Retrieval:
    """Retrieval tool configuration.

    Enables the model to retrieve information from external sources.

    Examples:
        >>> retrieval = Retrieval(
        ...     source=RetrievalSource(
        ...         vertex_ai_search=VertexAISearch(
        ...             datastore="projects/my-project/..."
        ...         )
        ...     ),
        ...     disable_attribution=False
        ... )
    """

    def __init__(
        self,
        source: RetrievalSource,
        disable_attribution: Optional[bool] = None,
    ) -> None:
        """Initialize retrieval configuration.

        Args:
            source (RetrievalSource):
                Retrieval source configuration
            disable_attribution (Optional[bool]):
                Whether to disable attribution
        """

    @property
    def disable_attribution(self) -> Optional[bool]:
        """Whether attribution is disabled."""

    @property
    def source(self) -> RetrievalSource:
        """The retrieval source."""

class Interval:
    """Time interval specification.

    Represents a time range with start and end times.

    Examples:
        >>> interval = Interval(
        ...     start_time="2024-01-01T00:00:00Z",
        ...     end_time="2024-12-31T23:59:59Z"
        ... )
    """

    @property
    def start_time(self) -> str:
        """The start time."""

    @property
    def end_time(self) -> str:
        """The end time."""

class GoogleSearch:
    """Google Search tool configuration (Gemini API).

    Configures Google Search with time range filtering.

    Examples:
        >>> search = GoogleSearch(
        ...     time_range_filter=Interval(
        ...         start_time="2024-01-01T00:00:00Z",
        ...         end_time="2024-12-31T23:59:59Z"
        ...     )
        ... )
    """

    @property
    def time_range_filter(self) -> Interval:
        """The time range filter."""

class VertexGoogleSearch:
    """Google Search tool configuration (Vertex API).

    Configures Google Search with domain blocking and phishing filters.

    Examples:
        >>> search = VertexGoogleSearch(
        ...     exclude_domains=["example.com", "spam.com"],
        ...     blocking_confidence=PhishBlockThreshold.BlockMediumAndAbove
        ... )
    """

    def __init__(
        self,
        exclude_domains: Optional[List[str]] = None,
        blocking_confidence: Optional[PhishBlockThreshold] = None,
    ) -> None:
        """Initialize Vertex Google Search configuration.

        Args:
            exclude_domains (Optional[List[str]]):
                Domains to exclude from results
            blocking_confidence (Optional[PhishBlockThreshold]):
                Phishing blocking threshold
        """

    @property
    def exclude_domains(self) -> Optional[List[str]]:
        """Domains to exclude."""

    @property
    def blocking_confidence(self) -> Optional[PhishBlockThreshold]:
        """Phishing blocking threshold."""

class EnterpriseWebSearch:
    """Enterprise web search tool configuration.

    Configures enterprise-grade web search with compliance features.

    Examples:
        >>> search = EnterpriseWebSearch(
        ...     exclude_domains=["example.com"],
        ...     blocking_confidence=PhishBlockThreshold.BlockHighAndAbove
        ... )
    """

    def __init__(
        self,
        exclude_domains: Optional[List[str]] = None,
        blocking_confidence: Optional[PhishBlockThreshold] = None,
    ) -> None:
        """Initialize enterprise web search configuration.

        Args:
            exclude_domains (Optional[List[str]]):
                Domains to exclude from results
            blocking_confidence (Optional[PhishBlockThreshold]):
                Phishing blocking threshold
        """

    @property
    def exclude_domains(self) -> Optional[List[str]]:
        """Domains to exclude."""

    @property
    def blocking_confidence(self) -> Optional[PhishBlockThreshold]:
        """Phishing blocking threshold."""

class ParallelAiSearch:
    """Parallel.ai search tool configuration.

    Configures search using the Parallel.ai engine.

    Examples:
        >>> search = ParallelAiSearch(
        ...     api_key="my-api-key",
        ...     custom_configs={
        ...         "source_policy": {"include_domains": ["google.com"]},
        ...         "maxResults": 10
        ...     }
        ... )
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        custom_configs: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize Parallel.ai search configuration.

        Args:
            api_key (Optional[str]):
                Parallel.ai API key
            custom_configs (Optional[Dict[str, Any]]):
                Custom configuration parameters

        Raises:
            TypeError: If configuration is invalid
        """

    @property
    def api_key(self) -> Optional[str]:
        """The API key."""

    @property
    def custom_configs(self) -> Optional[Dict[str, Any]]:
        """Custom configuration parameters."""

class GoogleSearchNum:
    """Union type for Google Search configurations.

    Represents either Gemini or Vertex Google Search configuration.

    Examples:
        >>> # Gemini search
        >>> search = GoogleSearchNum(
        ...     gemini_search=GoogleSearch(...)
        ... )

        >>> # Vertex search
        >>> search = GoogleSearchNum(
        ...     vertex_search=VertexGoogleSearch(...)
        ... )
    """

    def __init__(
        self,
        gemini_search: Optional[GoogleSearch] = None,
        vertex_search: Optional[VertexGoogleSearch] = None,
    ) -> None:
        """Initialize Google Search configuration.

        Exactly one of gemini_search or vertex_search must be provided.

        Args:
            gemini_search (Optional[GoogleSearch]):
                Gemini API search configuration
            vertex_search (Optional[VertexGoogleSearch]):
                Vertex API search configuration
        """

class DynamicRetrievalConfig:
    """Configuration for dynamic retrieval behavior.

    Controls when and how retrieval is triggered.

    Examples:
        >>> config = DynamicRetrievalConfig(
        ...     mode=DynamicRetrievalMode.ModeDynamic,
        ...     dynamic_threshold=0.5
        ... )
    """

    def __init__(
        self,
        mode: Optional[DynamicRetrievalMode] = None,
        dynamic_threshold: Optional[float] = None,
    ) -> None:
        """Initialize dynamic retrieval configuration.

        Args:
            mode (Optional[DynamicRetrievalMode]):
                Retrieval mode
            dynamic_threshold (Optional[float]):
                Threshold for dynamic retrieval
        """

    @property
    def mode(self) -> Optional[DynamicRetrievalMode]:
        """The retrieval mode."""

    @property
    def dynamic_threshold(self) -> Optional[float]:
        """The dynamic threshold."""

class GoogleSearchRetrieval:
    """Google Search retrieval tool configuration.

    Configures Google Search with dynamic retrieval.

    Examples:
        >>> retrieval = GoogleSearchRetrieval(
        ...     dynamic_retrieval_config=DynamicRetrievalConfig(
        ...         mode=DynamicRetrievalMode.ModeDynamic
        ...     )
        ... )
    """

    def __init__(
        self,
        dynamic_retrieval_config: Optional[DynamicRetrievalConfig] = None,
    ) -> None:
        """Initialize Google Search retrieval configuration.

        Args:
            dynamic_retrieval_config (Optional[DynamicRetrievalConfig]):
                Dynamic retrieval configuration
        """

    @property
    def dynamic_retrieval_config(self) -> Optional[DynamicRetrievalConfig]:
        """The dynamic retrieval configuration."""

class GoogleMaps:
    """Google Maps tool configuration.

    Configures Google Maps integration.

    Examples:
        >>> maps = GoogleMaps(enable_widget=True)
    """

    def __init__(
        self,
        enable_widget: bool = False,
    ) -> None:
        """Initialize Google Maps configuration.

        Args:
            enable_widget (bool):
                Whether to enable widget context token
        """

    @property
    def enable_widget(self) -> bool:
        """Whether widget is enabled."""

class CodeExecution:
    """Code execution tool configuration.

    Enables the model to execute generated code.

    This type has no configuration fields.

    Examples:
        >>> code_exec = CodeExecution()
    """

    def __init__(self) -> None:
        """Initialize code execution tool."""

class ComputerUse:
    """Computer use tool configuration.

    Enables the model to interact with computer interfaces.

    Examples:
        >>> computer_use = ComputerUse(
        ...     environment=ComputerUseEnvironment.EnvironmentBrowser,
        ...     excluded_predefined_functions=["take_screenshot"]
        ... )
    """

    def __init__(
        self,
        environment: ComputerUseEnvironment,
        excluded_predefined_functions: List[str],
    ) -> None:
        """Initialize computer use configuration.

        Args:
            environment (ComputerUseEnvironment):
                Operating environment
            excluded_predefined_functions (List[str]):
                Functions to exclude from auto-inclusion
        """

    @property
    def environment(self) -> ComputerUseEnvironment:
        """The operating environment."""

    @property
    def excluded_predefined_functions(self) -> List[str]:
        """Excluded functions."""

class UrlContext:
    """URL context tool configuration.

    Enables retrieval from user-provided URLs.

    This type has no configuration fields.

    Examples:
        >>> url_context = UrlContext()
    """

    def __init__(self) -> None:
        """Initialize URL context tool."""

class FileSearch:
    """File search tool configuration.

    Enables searching in file stores.

    Examples:
        >>> file_search = FileSearch(
        ...     file_search_store_names=["my-store"],
        ...     metadata_filter="category='docs'",
        ...     top_k=5
        ... )
    """

    def __init__(
        self,
        file_search_store_names: List[str],
        metadata_filter: str,
        top_k: int,
    ) -> None:
        """Initialize file search configuration.

        Args:
            file_search_store_names (List[str]):
                File store names to search
            metadata_filter (str):
                Metadata filter expression
            top_k (int):
                Number of top results
        """

    @property
    def file_search_store_names(self) -> List[str]:
        """File store names."""

    @property
    def metadata_filter(self) -> str:
        """Metadata filter."""

    @property
    def top_k(self) -> int:
        """Number of top results."""

class GeminiTool:
    """Tool definition for model use.

    Defines tools/functions that the model can use during generation.
    Tools enable the model to perform actions or retrieve information.

    Examples:
        >>> # Function tool
        >>> tool = Tool(
        ...     function_declarations=[
        ...         FunctionDeclaration(
        ...             name="get_weather",
        ...             description="Get weather for a location",
        ...             parameters=Schema(...)
        ...         )
        ...     ]
        ... )

        >>> # Google Search tool
        >>> tool = Tool(
        ...     google_search=GoogleSearchNum(
        ...         vertex_search=VertexGoogleSearch()
        ...     )
        ... )

        >>> # Code execution tool
        >>> tool = Tool(code_execution=CodeExecution())

        >>> # Multiple tools
        >>> tool = Tool(
        ...     function_declarations=[...],
        ...     google_search=GoogleSearchNum(...),
        ...     code_execution=CodeExecution()
        ... )
    """

    def __init__(
        self,
        function_declarations: Optional[List[FunctionDeclaration]] = None,
        retrieval: Optional[Retrieval] = None,
        google_search_retrieval: Optional[GoogleSearchRetrieval] = None,
        code_execution: Optional[CodeExecution] = None,
        google_search: Optional[GoogleSearchNum] = None,
        google_maps: Optional[GoogleMaps] = None,
        enterprise_web_search: Optional[EnterpriseWebSearch] = None,
        parallel_ai_search: Optional[ParallelAiSearch] = None,
        computer_use: Optional[ComputerUse] = None,
        url_context: Optional[UrlContext] = None,
        file_search: Optional[FileSearch] = None,
    ) -> None:
        """Initialize tool configuration.

        Args:
            function_declarations (Optional[List[FunctionDeclaration]]):
                Function declarations
            retrieval (Optional[Retrieval]):
                Retrieval tool configuration
            google_search_retrieval (Optional[GoogleSearchRetrieval]):
                Google Search retrieval configuration
            code_execution (Optional[CodeExecution]):
                Code execution tool
            google_search (Optional[GoogleSearchNum]):
                Google Search tool
            google_maps (Optional[GoogleMaps]):
                Google Maps tool
            enterprise_web_search (Optional[EnterpriseWebSearch]):
                Enterprise web search tool
            parallel_ai_search (Optional[ParallelAiSearch]):
                Parallel.ai search tool
            computer_use (Optional[ComputerUse]):
                Computer use tool
            url_context (Optional[UrlContext]):
                URL context tool
            file_search (Optional[FileSearch]):
                File search tool
        """

    @property
    def function_declarations(self) -> Optional[List[FunctionDeclaration]]:
        """Function declarations."""

    @property
    def retrieval(self) -> Optional[Retrieval]:
        """Retrieval configuration."""

    @property
    def google_search_retrieval(self) -> Optional[GoogleSearchRetrieval]:
        """Google Search retrieval configuration."""

    @property
    def code_execution(self) -> Optional[CodeExecution]:
        """Code execution tool."""

    @property
    def google_search(self) -> Optional[GoogleSearchNum]:
        """Google Search tool."""

    @property
    def google_maps(self) -> Optional[GoogleMaps]:
        """Google Maps tool."""

    @property
    def enterprise_web_search(self) -> Optional[EnterpriseWebSearch]:
        """Enterprise web search tool."""

    @property
    def parallel_ai_search(self) -> Optional[ParallelAiSearch]:
        """Parallel.ai search tool."""

    @property
    def computer_use(self) -> Optional[ComputerUse]:
        """Computer use tool."""

    @property
    def url_context(self) -> Optional[UrlContext]:
        """URL context tool."""

    @property
    def file_search(self) -> Optional[FileSearch]:
        """File search tool."""

class ModalityTokenCount:
    """Token count by modality.

    Breaks down token usage by content type (text, image, audio, etc.).

    Examples:
        >>> count = ModalityTokenCount(
        ...     modality=Modality.Text,
        ...     token_count=150
        ... )
    """

    @property
    def modality(self) -> Optional[Modality]:
        """The content modality."""

    @property
    def token_count(self) -> Optional[int]:
        """Token count for this modality."""

class UsageMetadata:
    """Token usage metadata for a request/response.

    Provides detailed breakdown of token usage across different components.

    Examples:
        >>> usage = UsageMetadata(
        ...     prompt_token_count=100,
        ...     candidates_token_count=50,
        ...     total_token_count=150,
        ...     cached_content_token_count=20
        ... )
    """

    @property
    def prompt_token_count(self) -> Optional[int]:
        """Tokens in the prompt."""

    @property
    def candidates_token_count(self) -> Optional[int]:
        """Tokens in generated candidates."""

    @property
    def tool_use_prompt_token_count(self) -> Optional[int]:
        """Tokens from tool use results."""

    @property
    def thoughts_token_count(self) -> Optional[int]:
        """Tokens in thinking/reasoning."""

    @property
    def total_token_count(self) -> Optional[int]:
        """Total token count."""

    @property
    def cached_content_token_count(self) -> Optional[int]:
        """Tokens from cached content."""

    @property
    def prompt_tokens_details(self) -> Optional[List[ModalityTokenCount]]:
        """Prompt tokens by modality."""

    @property
    def cache_tokens_details(self) -> Optional[List[ModalityTokenCount]]:
        """Cache tokens by modality."""

    @property
    def candidates_tokens_details(self) -> Optional[List[ModalityTokenCount]]:
        """Candidate tokens by modality."""

    @property
    def tool_use_prompt_tokens_details(self) -> Optional[List[ModalityTokenCount]]:
        """Tool use tokens by modality."""

    @property
    def traffic_type(self) -> Optional[TrafficType]:
        """Traffic type for billing."""

class PromptFeedback:
    """Feedback about prompt blocking.

    Indicates why a prompt was blocked by content filters.

    Examples:
        >>> feedback = PromptFeedback(
        ...     block_reason=BlockedReason.Safety,
        ...     safety_ratings=[...],
        ...     block_reason_messages="Prompt contains unsafe content"
        ... )
    """

    @property
    def block_reason(self) -> Optional[BlockedReason]:
        """Why the prompt was blocked."""

    @property
    def safety_ratings(self) -> Optional[List["SafetyRating"]]:
        """Safety ratings for the prompt."""

    @property
    def block_reason_message(self) -> Optional[str]:
        """Human-readable block reason."""

class UrlMetadata:
    """Metadata about URL retrieval.

    Information about a URL retrieved by the URL context tool.

    Examples:
        >>> metadata = UrlMetadata(
        ...     retrieved_url="https://example.com",
        ...     url_retrieval_status=UrlRetrievalStatus.UrlRetrievalStatusSuccess
        ... )
    """

    @property
    def retrieved_url(self) -> Optional[str]:
        """The retrieved URL."""

    @property
    def url_retrieval_status(self) -> Optional[UrlRetrievalStatus]:
        """Retrieval status."""

class UrlContextMetadata:
    """Metadata about URL context tool usage.

    Contains information about URLs retrieved by the tool.

    Examples:
        >>> metadata = UrlContextMetadata(
        ...     url_metadata=[
        ...         UrlMetadata(retrieved_url="https://example.com", ...)
        ...     ]
        ... )
    """

    @property
    def url_metadata(self) -> Optional[List[UrlMetadata]]:
        """List of URL metadata."""

class SourceFlaggingUri:
    """URI flagged as potentially problematic.

    Information about a source that was flagged for review.

    Examples:
        >>> uri = SourceFlaggingUri(
        ...     source_id="source123",
        ...     flag_content_uri="https://example.com/flagged"
        ... )
    """

    @property
    def source_id(self) -> str:
        """Source identifier."""

    @property
    def flag_content_uri(self) -> str:
        """URI of flagged content."""

class RetrievalMetadata:
    """Metadata about retrieval operations.

    Contains scores and information about retrieval behavior.

    Examples:
        >>> metadata = RetrievalMetadata(
        ...     google_search_dynamic_retrieval_score=0.85
        ... )
    """

    @property
    def google_search_dynamic_retrieval_score(self) -> Optional[float]:
        """Score for dynamic retrieval likelihood."""

class SearchEntryPoint:
    """Search entry point information.

    Contains embeddable search widgets and SDK data.

    Examples:
        >>> entry_point = SearchEntryPoint(
        ...     rendered_content="<div>...</div>",
        ...     sdk_blob="base64encodeddata"
        ... )
    """

    @property
    def rendered_content(self) -> Optional[str]:
        """Embeddable HTML content."""

    @property
    def sdk_blob(self) -> Optional[str]:
        """Base64 encoded SDK data."""

class Segment:
    """Text segment within content.

    Identifies a portion of generated content by part index and byte range.

    Examples:
        >>> segment = Segment(
        ...     part_index=0,
        ...     start_index=10,
        ...     end_index=50,
        ...     text="example text"
        ... )
    """

    @property
    def part_index(self) -> Optional[int]:
        """Index of the Part object."""

    @property
    def start_index(self) -> Optional[int]:
        """Start byte index."""

    @property
    def end_index(self) -> Optional[int]:
        """End byte index."""

    @property
    def text(self) -> Optional[str]:
        """The segment text."""

class GroundingSupport:
    """Grounding support information.

    Links generated content to source materials with confidence scores.

    Examples:
        >>> support = GroundingSupport(
        ...     grounding_chunk_indices=[0, 1, 2],
        ...     confidence_scores=[0.9, 0.85, 0.8],
        ...     segment=Segment(...)
        ... )
    """

    @property
    def grounding_chunk_indices(self) -> Optional[List[int]]:
        """Indices into grounding chunks."""

    @property
    def confidence_scores(self) -> Optional[List[float]]:
        """Confidence scores for citations."""

    @property
    def segment(self) -> Optional[Segment]:
        """Content segment being supported."""

class Web:
    """Web source information.

    Information about a web source used for grounding.

    Examples:
        >>> web = Web(
        ...     uri="https://example.com/page",
        ...     title="Example Page",
        ...     domain="example.com"
        ... )
    """

    @property
    def uri(self) -> Optional[str]:
        """The source URI."""

    @property
    def title(self) -> Optional[str]:
        """The page title."""

    @property
    def domain(self) -> Optional[str]:
        """The domain name."""

class PageSpan:
    """Page range in a document.

    Specifies a range of pages in a document.

    Examples:
        >>> span = PageSpan(first_page=1, last_page=5)
    """

    @property
    def first_page(self) -> int:
        """First page number."""

    @property
    def last_page(self) -> int:
        """Last page number."""

class RagChunk:
    """RAG chunk information.

    Text chunk from RAG retrieval with optional page information.

    Examples:
        >>> chunk = RagChunk(
        ...     text="Retrieved text content",
        ...     page_span=PageSpan(first_page=1, last_page=2)
        ... )
    """

    @property
    def text(self) -> str:
        """The chunk text."""

    @property
    def page_span(self) -> Optional[PageSpan]:
        """Page range for this chunk."""

class RetrievedContext:
    """Retrieved context information.

    Context retrieved from a knowledge source.

    Examples:
        >>> context = RetrievedContext(
        ...     uri="https://example.com",
        ...     title="Example",
        ...     text="Retrieved content",
        ...     rag_chunk=RagChunk(...)
        ... )
    """

    @property
    def uri(self) -> Optional[str]:
        """Source URI."""

    @property
    def title(self) -> Optional[str]:
        """Source title."""

    @property
    def text(self) -> Optional[str]:
        """Retrieved text."""

    @property
    def rag_chunk(self) -> Optional[RagChunk]:
        """RAG chunk information."""

class Maps:
    """Google Maps source information.

    Information about a Maps location used for grounding.

    Examples:
        >>> maps = Maps(
        ...     uri="https://maps.google.com/...",
        ...     title="Statue of Liberty",
        ...     place_id="ChIJPTacEpBQwokRKwIlDbbNLlE"
        ... )
    """

    @property
    def uri(self) -> Optional[str]:
        """Maps URI."""

    @property
    def title(self) -> Optional[str]:
        """Location title."""

    @property
    def text(self) -> Optional[str]:
        """Location description."""

    @property
    def place_id(self) -> Optional[str]:
        """Google Maps place ID."""

class GroundingChunkType:
    """Union type for grounding chunk sources.

    Represents different types of grounding sources.

    Examples:
        >>> # Web source
        >>> chunk = GroundingChunkType.Web(Web(...))

        >>> # Retrieved context
        >>> chunk = GroundingChunkType.RetrievedContext(RetrievedContext(...))

        >>> # Maps source
        >>> chunk = GroundingChunkType.Maps(Maps(...))
    """

class GroundingChunk:
    """Grounding chunk wrapper.

    Wraps a grounding chunk source.

    Examples:
        >>> chunk = GroundingChunk(
        ...     chunk_type=GroundingChunkType.Web(Web(...))
        ... )
    """

    @property
    def chunk_type(self) -> GroundingChunkType:
        """The chunk type."""

class GroundingMetadata:
    """Grounding metadata for a response.

    Contains all grounding information including sources, supports, and search queries.

    Examples:
        >>> metadata = GroundingMetadata(
        ...     web_search_queries=["query1", "query2"],
        ...     grounding_chunks=[GroundingChunk(...)],
        ...     grounding_supports=[GroundingSupport(...)]
        ... )
    """

    @property
    def web_search_queries(self) -> Optional[List[str]]:
        """Web search queries used."""

    @property
    def grounding_chunks(self) -> Optional[List[GroundingChunk]]:
        """Grounding source chunks."""

    @property
    def grounding_supports(self) -> Optional[List[GroundingSupport]]:
        """Grounding support information."""

    @property
    def search_entry_point(self) -> Optional[SearchEntryPoint]:
        """Search entry point."""

    @property
    def retrieval_metadata(self) -> Optional[RetrievalMetadata]:
        """Retrieval metadata."""

    @property
    def source_flagging_uris(self) -> Optional[List[SourceFlaggingUri]]:
        """Flagged source URIs."""

    @property
    def google_maps_widget_context_token(self) -> Optional[str]:
        """Maps widget context token."""

class SafetyRating:
    """Safety rating for content.

    Provides detailed safety assessment including probability and severity.

    Examples:
        >>> rating = SafetyRating(
        ...     category=HarmCategory.HarmCategoryHateSpeech,
        ...     probability=HarmProbability.Low,
        ...     probability_score=0.2,
        ...     severity=HarmSeverity.HarmSeverityLow,
        ...     severity_score=0.15,
        ...     blocked=False
        ... )
    """

    @property
    def category(self) -> HarmCategory:
        """Harm category."""

    @property
    def probability(self) -> Optional[HarmProbability]:
        """Harm probability level."""

    @property
    def probability_score(self) -> Optional[float]:
        """Numeric probability score."""

    @property
    def severity(self) -> Optional[HarmSeverity]:
        """Harm severity level."""

    @property
    def severity_score(self) -> Optional[float]:
        """Numeric severity score."""

    @property
    def blocked(self) -> Optional[bool]:
        """Whether content was blocked."""

    @property
    def overwritten_threshold(self) -> Optional[HarmBlockThreshold]:
        """Overwritten threshold for image output."""

class LogprobsCandidate:
    """Log probability information for a token.

    Contains token string, ID, and log probability.

    Examples:
        >>> candidate = LogprobsCandidate(
        ...     token="hello",
        ...     token_id=12345,
        ...     log_probability=-0.5
        ... )
    """

    @property
    def token(self) -> Optional[str]:
        """Token string."""

    @property
    def token_id(self) -> Optional[int]:
        """Token ID."""

    @property
    def log_probability(self) -> Optional[float]:
        """Log probability."""

class TopCandidates:
    """Top token candidates at a decoding step.

    List of top candidates sorted by log probability.

    Examples:
        >>> top = TopCandidates(
        ...     candidates=[
        ...         LogprobsCandidate(token="hello", log_probability=-0.5),
        ...         LogprobsCandidate(token="hi", log_probability=-1.2)
        ...     ]
        ... )
    """

    @property
    def candidates(self) -> Optional[List[LogprobsCandidate]]:
        """List of candidates."""

class LogprobsResult:
    """Complete log probability result.

    Contains both top candidates and chosen tokens with probabilities.

    Examples:
        >>> result = LogprobsResult(
        ...     top_candidates=[TopCandidates(...)],
        ...     chosen_candidates=[LogprobsCandidate(...)]
        ... )
    """

    @property
    def top_candidates(self) -> Optional[List[TopCandidates]]:
        """Top candidates per step."""

    @property
    def chosen_candidates(self) -> Optional[List[LogprobsCandidate]]:
        """Actually chosen tokens."""

class GoogleDate:
    """Date representation.

    Simple date with year, month, and day.

    Examples:
        >>> date = GoogleDate(year=2024, month=12, day=25)
    """

    @property
    def year(self) -> Optional[int]:
        """Year."""

    @property
    def month(self) -> Optional[int]:
        """Month (1-12)."""

    @property
    def day(self) -> Optional[int]:
        """Day of month."""

class Citation:
    """Source citation information.

    Citation for a piece of generated content with source details.

    Examples:
        >>> citation = Citation(
        ...     start_index=10,
        ...     end_index=50,
        ...     uri="https://example.com",
        ...     title="Example Source",
        ...     license="CC-BY-4.0",
        ...     publication_date=GoogleDate(year=2024, month=1, day=1)
        ... )
    """

    @property
    def start_index(self) -> Optional[int]:
        """Start index in content."""

    @property
    def end_index(self) -> Optional[int]:
        """End index in content."""

    @property
    def uri(self) -> Optional[str]:
        """Source URI."""

    @property
    def title(self) -> Optional[str]:
        """Source title."""

    @property
    def license(self) -> Optional[str]:
        """Source license."""

    @property
    def publication_date(self) -> Optional[GoogleDate]:
        """Publication date."""

class CitationMetadata:
    """Collection of citations.

    Contains all citations for a piece of content.

    Examples:
        >>> metadata = CitationMetadata(
        ...     citations=[Citation(...), Citation(...)]
        ... )
    """

    @property
    def citations(self) -> Optional[List[Citation]]:
        """List of citations."""

class Candidate:
    """Response candidate from the model.

    A single generated response option with content and metadata.

    Examples:
        >>> candidate = Candidate(
        ...     index=0,
        ...     content=GeminiContent(...),
        ...     finish_reason=FinishReason.Stop,
        ...     safety_ratings=[SafetyRating(...)],
        ...     citation_metadata=CitationMetadata(...)
        ... )
    """

    @property
    def index(self) -> Optional[int]:
        """Candidate index."""

    @property
    def content(self) -> GeminiContent:
        """Generated content."""

    @property
    def avg_logprobs(self) -> Optional[float]:
        """Average log probability."""

    @property
    def logprobs_result(self) -> Optional[LogprobsResult]:
        """Detailed log probabilities."""

    @property
    def finish_reason(self) -> Optional[FinishReason]:
        """Why generation stopped."""

    @property
    def safety_ratings(self) -> Optional[List[SafetyRating]]:
        """Safety ratings."""

    @property
    def citation_metadata(self) -> Optional[CitationMetadata]:
        """Citation metadata."""

    @property
    def grounding_metadata(self) -> Optional[GroundingMetadata]:
        """Grounding metadata."""

    @property
    def url_context_metadata(self) -> Optional[UrlContextMetadata]:
        """URL context metadata."""

    @property
    def finish_message(self) -> Optional[str]:
        """Detailed finish reason message."""

class GenerateContentResponse:
    """Response from content generation.

    Complete response including candidates, usage, and feedback.

    Examples:
        >>> response = GenerateContentResponse(
        ...     candidates=[Candidate(...)],
        ...     usage_metadata=UsageMetadata(...),
        ...     model_version="gemini-1.5-pro-002"
        ... )
    """

    @property
    def candidates(self) -> List[Candidate]:
        """Generated candidates."""

    @property
    def model_version(self) -> Optional[str]:
        """Model version used."""

    @property
    def create_time(self) -> Optional[str]:
        """Request timestamp."""

    @property
    def response_id(self) -> Optional[str]:
        """Response identifier."""

    @property
    def prompt_feedback(self) -> Optional[PromptFeedback]:
        """Prompt feedback (if blocked)."""

    @property
    def usage_metadata(self) -> Optional[UsageMetadata]:
        """Token usage metadata."""

class PredictRequest:
    """Prediction API request.

    Generic prediction request for embedding and other endpoints.

    Examples:
        >>> request = PredictRequest(
        ...     instances=[{"content": {"parts": [{"text": "Hello"}]}}],
        ...     parameters={"outputDimensionality": 768}
        ... )
    """

    def __init__(
        self,
        instances: Any,
        parameters: Optional[Any] = None,
    ) -> None:
        """Initialize prediction request.

        Args:
            instances (Any):
                Input instances
            parameters (Optional[Any]):
                Request parameters
        """

    @property
    def instances(self) -> Any:
        """Input instances."""

    @property
    def parameters(self) -> Any:
        """Request parameters."""

    def __str__(self) -> str:
        """String representation."""

class PredictResponse:
    """Prediction API response.

    Generic prediction response containing predictions and metadata.

    Examples:
        >>> response = PredictResponse(
        ...     predictions=[{"embedding": {"values": [0.1, 0.2, ...]}}],
        ...     deployed_model_id="12345",
        ...     model="embedding-001"
        ... )
    """

    @property
    def predictions(self) -> Any:
        """Predictions."""

    @property
    def metadata(self) -> Any:
        """Response metadata."""

    @property
    def deployed_model_id(self) -> str:
        """Deployed model ID."""

    @property
    def model(self) -> str:
        """Model name."""

    @property
    def model_version_id(self) -> str:
        """Model version ID."""

    @property
    def model_display_name(self) -> str:
        """Model display name."""

    def __str__(self) -> str:
        """String representation."""

class GeminiEmbeddingConfig:
    """Configuration for Gemini embeddings.

    Configures embedding generation including dimensionality and task type.

    Examples:
        >>> config = GeminiEmbeddingConfig(
        ...     model="text-embedding-004",
        ...     output_dimensionality=768,
        ...     task_type=EmbeddingTaskType.RetrievalDocument
        ... )
    """

    def __init__(
        self,
        model: Optional[str] = None,
        output_dimensionality: Optional[int] = None,
        task_type: Optional[EmbeddingTaskType] = None,
    ) -> None:
        """Initialize embedding configuration.

        Args:
            model (Optional[str]):
                Model name
            output_dimensionality (Optional[int]):
                Output embedding dimensionality
            task_type (Optional[EmbeddingTaskType]):
                Task type for embeddings

        Raises:
            TypeError: If neither model nor task_type is provided
        """

    @property
    def model(self) -> Optional[str]:
        """The model name."""

    @property
    def output_dimensionality(self) -> Optional[int]:
        """Output dimensionality."""

    @property
    def task_type(self) -> Optional[EmbeddingTaskType]:
        """Task type."""

    @property
    def is_configured(self) -> bool:
        """Whether config has parameters set."""

class ContentEmbedding:
    """Content embedding result.

    Contains the embedding vector values.

    Examples:
        >>> embedding = ContentEmbedding(
        ...     values=[0.1, 0.2, 0.3, ...]
        ... )
    """

    @property
    def values(self) -> List[float]:
        """Embedding vector values."""

class GeminiEmbeddingResponse:
    """Response from embedding generation.

    Contains the generated embedding.

    Examples:
        >>> response = GeminiEmbeddingResponse(
        ...     embedding=ContentEmbedding(values=[0.1, 0.2, ...])
        ... )
    """

    @property
    def embedding(self) -> ContentEmbedding:
        """The generated embedding."""

###### __potatohead__.anthropic module ######

class CitationCharLocationParam:
    """Citation with character-level location in document.

    Specifies a citation reference using character indices within a document.

    Examples:
        >>> citation = CitationCharLocationParam(
        ...     cited_text="Example text",
        ...     document_index=0,
        ...     document_title="Document Title",
        ...     end_char_index=100,
        ...     start_char_index=50
        ... )
    """

    def __init__(
        self,
        cited_text: str,
        document_index: int,
        document_title: str,
        end_char_index: int,
        start_char_index: int,
    ) -> None:
        """Initialize character location citation.

        Args:
            cited_text (str):
                The text being cited
            document_index (int):
                Index of the document in the input
            document_title (str):
                Title of the document
            end_char_index (int):
                Ending character position
            start_char_index (int):
                Starting character position
        """

    @property
    def cited_text(self) -> str:
        """The cited text."""

    @property
    def document_index(self) -> int:
        """Document index."""

    @property
    def document_title(self) -> str:
        """Document title."""

    @property
    def end_char_index(self) -> int:
        """End character index."""

    @property
    def start_char_index(self) -> int:
        """Start character index."""

    @property
    def type(self) -> str:
        """Citation type (always 'char_location')."""

class CitationPageLocationParam:
    """Citation with page-level location in document.

    Specifies a citation reference using page numbers within a document.

    Examples:
        >>> citation = CitationPageLocationParam(
        ...     cited_text="Example text",
        ...     document_index=0,
        ...     document_title="Document Title",
        ...     end_page_number=10,
        ...     start_page_number=5
        ... )
    """

    def __init__(
        self,
        cited_text: str,
        document_index: int,
        document_title: str,
        end_page_number: int,
        start_page_number: int,
    ) -> None:
        """Initialize page location citation.

        Args:
            cited_text (str):
                The text being cited
            document_index (int):
                Index of the document in the input
            document_title (str):
                Title of the document
            end_page_number (int):
                Ending page number
            start_page_number (int):
                Starting page number
        """

    @property
    def cited_text(self) -> str:
        """The cited text."""

    @property
    def document_index(self) -> int:
        """Document index."""

    @property
    def document_title(self) -> str:
        """Document title."""

    @property
    def end_page_number(self) -> int:
        """End page number."""

    @property
    def start_page_number(self) -> int:
        """Start page number."""

    @property
    def type(self) -> str:
        """Citation type (always 'page_location')."""

class CitationContentBlockLocationParam:
    """Citation with content block location in document.

    Specifies a citation reference using content block indices within a document.

    Examples:
        >>> citation = CitationContentBlockLocationParam(
        ...     cited_text="Example text",
        ...     document_index=0,
        ...     document_title="Document Title",
        ...     end_block_index=5,
        ...     start_block_index=2
        ... )
    """

    def __init__(
        self,
        cited_text: str,
        document_index: int,
        document_title: str,
        end_block_index: int,
        start_block_index: int,
    ) -> None:
        """Initialize content block location citation.

        Args:
            cited_text (str):
                The text being cited
            document_index (int):
                Index of the document in the input
            document_title (str):
                Title of the document
            end_block_index (int):
                Ending content block index
            start_block_index (int):
                Starting content block index
        """

    @property
    def cited_text(self) -> str:
        """The cited text."""

    @property
    def document_index(self) -> int:
        """Document index."""

    @property
    def document_title(self) -> str:
        """Document title."""

    @property
    def end_block_index(self) -> int:
        """End block index."""

    @property
    def start_block_index(self) -> int:
        """Start block index."""

    @property
    def type(self) -> str:
        """Citation type (always 'content_block_location')."""

class CitationWebSearchResultLocationParam:
    """Citation from web search result.

    Specifies a citation reference from a web search result.

    Examples:
        >>> citation = CitationWebSearchResultLocationParam(
        ...     cited_text="Example text",
        ...     encrypted_index="abc123",
        ...     title="Search Result",
        ...     url="https://example.com"
        ... )
    """

    def __init__(
        self,
        cited_text: str,
        encrypted_index: str,
        title: str,
        url: str,
    ) -> None:
        """Initialize web search result citation.

        Args:
            cited_text (str):
                The text being cited
            encrypted_index (str):
                Encrypted search result index
            title (str):
                Title of the search result
            url (str):
                URL of the search result
        """

    @property
    def cited_text(self) -> str:
        """The cited text."""

    @property
    def encrypted_index(self) -> str:
        """Encrypted index."""

    @property
    def title(self) -> str:
        """Result title."""

    @property
    def type(self) -> str:
        """Citation type (always 'web_search_result_location')."""

    @property
    def url(self) -> str:
        """Result URL."""

class CitationSearchResultLocationParam:
    """Citation from search result.

    Specifies a citation reference from a search result with block-level location.

    Examples:
        >>> citation = CitationSearchResultLocationParam(
        ...     cited_text="Example text",
        ...     end_block_index=5,
        ...     search_result_index=0,
        ...     source="https://example.com",
        ...     start_block_index=2,
        ...     title="Search Result"
        ... )
    """

    def __init__(
        self,
        cited_text: str,
        end_block_index: int,
        search_result_index: int,
        source: str,
        start_block_index: int,
        title: str,
    ) -> None:
        """Initialize search result citation.

        Args:
            cited_text (str):
                The text being cited
            end_block_index (int):
                Ending content block index
            search_result_index (int):
                Index of the search result
            source (str):
                Source URL or identifier
            start_block_index (int):
                Starting content block index
            title (str):
                Title of the search result
        """

    @property
    def cited_text(self) -> str:
        """The cited text."""

    @property
    def end_block_index(self) -> int:
        """End block index."""

    @property
    def search_result_index(self) -> int:
        """Search result index."""

    @property
    def source(self) -> str:
        """Result source."""

    @property
    def start_block_index(self) -> int:
        """Start block index."""

    @property
    def title(self) -> str:
        """Result title."""

    @property
    def type(self) -> str:
        """Citation type (always 'search_result_location')."""

class TextBlockParam:
    """Text content block parameter.

    Regular text content with optional cache control and citations.

    Examples:
        >>> # Simple text block
        >>> block = TextBlockParam(text="Hello, world!", cache_control=None, citations=None)
        >>>
        >>> # With cache control
        >>> cache = CacheControl(cache_type="ephemeral", ttl="5m")
        >>> block = TextBlockParam(text="Hello", cache_control=cache, citations=None)
    """

    def __init__(
        self,
        text: str,
        cache_control: Optional["CacheControl"] = None,
        citations: Optional[Any] = None,
    ) -> None:
        """Initialize text block parameter.

        Args:
            text (str):
                Text content
            cache_control (Optional[CacheControl]):
                Cache control settings
            citations (Optional[Any]):
                Citation information
        """

    @property
    def text(self) -> str:
        """The text content."""

    @property
    def cache_control(self) -> Optional["CacheControl"]:
        """Cache control settings."""

    @property
    def type(self) -> str:
        """Content type (always 'text')."""

class Base64ImageSource:
    """Base64-encoded image source.

    Image data encoded in base64 format with media type.

    Examples:
        >>> source = Base64ImageSource(
        ...     media_type="image/jpeg",
        ...     data="base64_encoded_data_here"
        ... )
    """

    def __init__(self, media_type: str, data: str) -> None:
        """Initialize base64 image source.

        Args:
            media_type (str):
                Image media type (e.g., "image/jpeg", "image/png")
            data (str):
                Base64-encoded image data
        """

    @property
    def media_type(self) -> str:
        """Image media type."""

    @property
    def data(self) -> str:
        """Base64-encoded image data."""

    @property
    def type(self) -> str:
        """Source type (always 'base64')."""

class UrlImageSource:
    """URL-based image source.

    Image referenced by URL.

    Examples:
        >>> source = UrlImageSource(url="https://example.com/image.jpg")
    """

    def __init__(self, url: str) -> None:
        """Initialize URL image source.

        Args:
            url (str):
                Image URL
        """

    @property
    def url(self) -> str:
        """Image URL."""

    @property
    def type(self) -> str:
        """Source type (always 'url')."""

class ImageBlockParam:
    """Image content block parameter.

    Image content with source and optional cache control.

    Examples:
        >>> # Base64 image
        >>> source = Base64ImageSource(media_type="image/jpeg", data="...")
        >>> block = ImageBlockParam(source=source, cache_control=None)
        >>>
        >>> # URL image
        >>> source = UrlImageSource(url="https://example.com/image.jpg")
        >>> block = ImageBlockParam(source=source, cache_control=None)
    """

    def __init__(
        self,
        source: Any,
        cache_control: Optional["CacheControl"] = None,
    ) -> None:
        """Initialize image block parameter.

        Args:
            source (Any):
                Image source (Base64ImageSource or UrlImageSource)
            cache_control (Optional[CacheControl]):
                Cache control settings
        """

    @property
    def source(self) -> Any:
        """Image source."""

    @property
    def cache_control(self) -> Optional["CacheControl"]:
        """Cache control settings."""

    @property
    def type(self) -> str:
        """Content type (always 'image')."""

class Base64PDFSource:
    """Base64-encoded PDF source.

    PDF document data encoded in base64 format.

    Examples:
        >>> source = Base64PDFSource(data="base64_encoded_pdf_data")
    """

    def __init__(self, data: str) -> None:
        """Initialize base64 PDF source.

        Args:
            data (str):
                Base64-encoded PDF data
        """

    @property
    def media_type(self) -> str:
        """Media type (always 'application/pdf')."""

    @property
    def data(self) -> str:
        """Base64-encoded PDF data."""

    @property
    def type(self) -> str:
        """Source type (always 'base64')."""

class UrlPDFSource:
    """URL-based PDF source.

    PDF document referenced by URL.

    Examples:
        >>> source = UrlPDFSource(url="https://example.com/document.pdf")
    """

    def __init__(self, url: str) -> None:
        """Initialize URL PDF source.

        Args:
            url (str):
                PDF document URL
        """

    @property
    def url(self) -> str:
        """PDF URL."""

    @property
    def type(self) -> str:
        """Source type (always 'url')."""

class PlainTextSource:
    """Plain text document source.

    Plain text document data.

    Examples:
        >>> source = PlainTextSource(data="Plain text content")
    """

    def __init__(self, data: str) -> None:
        """Initialize plain text source.

        Args:
            data (str):
                Plain text content
        """

    @property
    def media_type(self) -> str:
        """Media type (always 'text/plain')."""

    @property
    def data(self) -> str:
        """Text content."""

    @property
    def type(self) -> str:
        """Source type (always 'text')."""

class CitationsConfigParams:
    """Configuration for citations.

    Controls whether citations are enabled for document content.

    Examples:
        >>> config = CitationsConfigParams()
        >>> config.enabled = True
    """

    @property
    def enabled(self) -> Optional[bool]:
        """Whether citations are enabled."""

class DocumentBlockParam:
    """Document content block parameter.

    Document content with source, optional cache control, title, context, and citations.

    Examples:
        >>> # PDF document
        >>> source = Base64PDFSource(data="...")
        >>> block = DocumentBlockParam(
        ...     source=source,
        ...     title="Document Title",
        ...     context="Additional context",
        ...     citations=CitationsConfigParams()
        ... )
    """

    def __init__(
        self,
        source: Any,
        cache_control: Optional["CacheControl"] = None,
        title: Optional[str] = None,
        context: Optional[str] = None,
        citations: Optional[CitationsConfigParams] = None,
    ) -> None:
        """Initialize document block parameter.

        Args:
            source (Any):
                Document source (Base64PDFSource, UrlPDFSource, or PlainTextSource)
            cache_control (Optional[CacheControl]):
                Cache control settings
            title (Optional[str]):
                Document title
            context (Optional[str]):
                Additional context about the document
            citations (Optional[CitationsConfigParams]):
                Citations configuration
        """

    @property
    def cache_control(self) -> Optional["CacheControl"]:
        """Cache control settings."""

    @property
    def title(self) -> Optional[str]:
        """Document title."""

    @property
    def context(self) -> Optional[str]:
        """Document context."""

    @property
    def type(self) -> str:
        """Content type (always 'document')."""

    @property
    def citations(self) -> Optional[CitationsConfigParams]:
        """Citations configuration."""

class SearchResultBlockParam:
    """Search result content block parameter.

    Search result content with text blocks, source, and title.

    Examples:
        >>> content = [TextBlockParam(text="Result content", cache_control=None, citations=None)]
        >>> block = SearchResultBlockParam(
        ...     content=content,
        ...     source="https://example.com",
        ...     title="Search Result",
        ...     cache_control=None,
        ...     citations=None
        ... )
    """

    def __init__(
        self,
        content: List[TextBlockParam],
        source: str,
        title: str,
        cache_control: Optional["CacheControl"] = None,
        citations: Optional[CitationsConfigParams] = None,
    ) -> None:
        """Initialize search result block parameter.

        Args:
            content (List[TextBlockParam]):
                List of text content blocks
            source (str):
                Source URL or identifier
            title (str):
                Result title
            cache_control (Optional[CacheControl]):
                Cache control settings
            citations (Optional[CitationsConfigParams]):
                Citations configuration
        """

    @property
    def content(self) -> List[TextBlockParam]:
        """Content blocks."""

    @property
    def source(self) -> str:
        """Result source."""

    @property
    def title(self) -> str:
        """Result title."""

    @property
    def type(self) -> str:
        """Content type (always 'search_result')."""

    @property
    def cache_control(self) -> Optional["CacheControl"]:
        """Cache control settings."""

    @property
    def citations(self) -> Optional[CitationsConfigParams]:
        """Citations configuration."""

class ThinkingBlockParam:
    """Thinking content block parameter.

    Claude's internal thinking/reasoning process.

    Examples:
        >>> block = ThinkingBlockParam(
        ...     thinking="Let me think about this...",
        ...     signature="signature_string"
        ... )
    """

    def __init__(
        self,
        thinking: str,
        signature: Optional[str] = None,
    ) -> None:
        """Initialize thinking block parameter.

        Args:
            thinking (str):
                The thinking content
            signature (Optional[str]):
                Cryptographic signature
        """

    @property
    def thinking(self) -> str:
        """Thinking content."""

    @property
    def signature(self) -> Optional[str]:
        """Cryptographic signature."""

    @property
    def type(self) -> str:
        """Content type (always 'thinking')."""

class RedactedThinkingBlockParam:
    """Redacted thinking content block parameter.

    Redacted version of Claude's thinking process.

    Examples:
        >>> block = RedactedThinkingBlockParam(data="[REDACTED]")
    """

    def __init__(self, data: str) -> None:
        """Initialize redacted thinking block parameter.

        Args:
            data (str):
                Redacted thinking data
        """

    @property
    def data(self) -> str:
        """Redacted data."""

    @property
    def type(self) -> str:
        """Content type (always 'redacted_thinking')."""

class ToolUseBlockParam:
    """Tool use content block parameter.

    Represents a tool call made by the model.

    Examples:
        >>> block = ToolUseBlockParam(
        ...     id="tool_call_123",
        ...     name="get_weather",
        ...     input={"location": "San Francisco"},
        ...     cache_control=None
        ... )
    """

    def __init__(
        self,
        id: str,
        name: str,
        input: Any,
        cache_control: Optional["CacheControl"] = None,
    ) -> None:
        """Initialize tool use block parameter.

        Args:
            id (str):
                Tool call ID
            name (str):
                Tool name
            input (Any):
                Tool input parameters
            cache_control (Optional[CacheControl]):
                Cache control settings
        """

    @property
    def id(self) -> str:
        """Tool call ID."""

    @property
    def name(self) -> str:
        """Tool name."""

    @property
    def input(self) -> Any:
        """Tool input parameters."""

    @property
    def cache_control(self) -> Optional["CacheControl"]:
        """Cache control settings."""

    @property
    def type(self) -> str:
        """Content type (always 'tool_use')."""

class ToolResultBlockParam:
    """Tool result content block parameter.

    Contains the result from executing a tool.

    Examples:
        >>> # Success result
        >>> content = [TextBlockParam(text="Result data", cache_control=None, citations=None)]
        >>> block = ToolResultBlockParam(
        ...     tool_use_id="tool_call_123",
        ...     is_error=False,
        ...     cache_control=None,
        ...     content=content
        ... )
        >>>
        >>> # Error result
        >>> block = ToolResultBlockParam(
        ...     tool_use_id="tool_call_123",
        ...     is_error=True,
        ...     cache_control=None,
        ...     content=None
        ... )
    """

    def __init__(
        self,
        tool_use_id: str,
        is_error: Optional[bool] = None,
        cache_control: Optional["CacheControl"] = None,
        content: Optional[List[Any]] = None,
    ) -> None:
        """Initialize tool result block parameter.

        Args:
            tool_use_id (str):
                ID of the tool call this is a result for
            is_error (Optional[bool]):
                Whether this is an error result
            cache_control (Optional[CacheControl]):
                Cache control settings
            content (Optional[List[Any]]):
                Result content blocks
        """

    @property
    def tool_use_id(self) -> str:
        """Tool use ID."""

    @property
    def cache_control(self) -> Optional["CacheControl"]:
        """Cache control settings."""

    @property
    def type(self) -> str:
        """Content type (always 'tool_result')."""

    @property
    def content(self) -> Optional[Any]:
        """Result content."""

class ServerToolUseBlockParam:
    """Server tool use content block parameter.

    Represents a server-side tool call made by the model.

    Examples:
        >>> block = ServerToolUseBlockParam(
        ...     id="server_tool_123",
        ...     name="web_search",
        ...     input={"query": "latest news"},
        ...     cache_control=None
        ... )
    """

    def __init__(
        self,
        id: str,
        name: str,
        input: Any,
        cache_control: Optional["CacheControl"] = None,
    ) -> None:
        """Initialize server tool use block parameter.

        Args:
            id (str):
                Tool call ID
            name (str):
                Tool name
            input (Any):
                Tool input parameters
            cache_control (Optional[CacheControl]):
                Cache control settings
        """

    @property
    def id(self) -> str:
        """Tool call ID."""

    @property
    def name(self) -> str:
        """Tool name."""

    @property
    def input(self) -> Any:
        """Tool input parameters."""

    @property
    def cache_control(self) -> Optional["CacheControl"]:
        """Cache control settings."""

    @property
    def type(self) -> str:
        """Content type (always 'server_tool_use')."""

class WebSearchResultBlockParam:
    """Web search result block parameter.

    Contains a single web search result.

    Examples:
        >>> block = WebSearchResultBlockParam(
        ...     encrypted_content="encrypted_data",
        ...     title="Search Result",
        ...     url="https://example.com",
        ...     page_agent="5 hours ago"
        ... )
    """

    def __init__(
        self,
        encrypted_content: str,
        title: str,
        url: str,
        page_agent: Optional[str] = None,
    ) -> None:
        """Initialize web search result block parameter.

        Args:
            encrypted_content (str):
                Encrypted content data
            title (str):
                Result title
            url (str):
                Result URL
            page_agent (Optional[str]):
                Page age information
        """

    @property
    def encrypted_content(self) -> str:
        """Encrypted content."""

    @property
    def title(self) -> str:
        """Result title."""

    @property
    def url(self) -> str:
        """Result URL."""

    @property
    def page_agent(self) -> Optional[str]:
        """Page age information."""

    @property
    def type(self) -> str:
        """Content type (always 'web_search_result')."""

class WebSearchToolResultBlockParam:
    """Web search tool result block parameter.

    Contains multiple web search results from a tool call.

    Examples:
        >>> results = [WebSearchResultBlockParam(...), WebSearchResultBlockParam(...)]
        >>> block = WebSearchToolResultBlockParam(
        ...     tool_use_id="search_123",
        ...     content=results,
        ...     cache_control=None
        ... )
    """

    def __init__(
        self,
        tool_use_id: str,
        content: List[WebSearchResultBlockParam],
        cache_control: Optional["CacheControl"] = None,
    ) -> None:
        """Initialize web search tool result block parameter.

        Args:
            tool_use_id (str):
                ID of the web search tool call
            content (List[WebSearchResultBlockParam]):
                List of search results
            cache_control (Optional[CacheControl]):
                Cache control settings
        """

    @property
    def tool_use_id(self) -> str:
        """Tool use ID."""

    @property
    def content(self) -> List[WebSearchResultBlockParam]:
        """Search results."""

    @property
    def cache_control(self) -> Optional["CacheControl"]:
        """Cache control settings."""

    @property
    def type(self) -> str:
        """Content type (always 'web_search_tool_result')."""

_ParamType: TypeAlias = (
    TextBlockParam
    | ImageBlockParam
    | DocumentBlockParam
    | SearchResultBlockParam
    | ThinkingBlockParam
    | RedactedThinkingBlockParam
    | ToolUseBlockParam
    | ToolResultBlockParam
    | ServerToolUseBlockParam
    | ServerToolUseBlockParam
    | WebSearchResultBlockParam
)

_ContentType: TypeAlias = str | _ParamType | List[_ParamType]

class MessageParam:
    """Message parameter for chat completion requests.

    Input message with role and content.

    Examples:
        >>> # Simple text message
        >>> msg = MessageParam(content="Hello, Claude!", role="user")
        >>>
        >>> # Message with mixed content
        >>> text_block = TextBlockParam(text="Describe this:", cache_control=None, citations=None)
        >>> image_source = UrlImageSource(url="https://example.com/image.jpg")
        >>> image_block = ImageBlockParam(source=image_source, cache_control=None)
        >>> msg = MessageParam(content=[text_block, image_block], role="user")
    """

    def __init__(self, content: _ContentType, role: str) -> None:
        """Initialize message parameter.

        Args:
            content (_ContentType):
                Message content (string, content block or list of content blocks)
            role (str):
                Message role ("user" or "assistant")
        """

    @property
    def text(self) -> str:
        """Get the text content of the first part, if available. Returns
        an empty string if the first part is not text.
        This is meant for convenience when working with simple text messages.
        """

    @property
    def content(self) -> List[_ParamType]:
        """Message content blocks."""

    @property
    def role(self) -> str:
        """Message role."""

    def bind(
        self,
        name: Optional[str] = None,
        value: Optional[str | int | float | bool | list] = None,
    ) -> "MessageParam":
        """Bind variables to the message content.
        Args:
            name (Optional[str]):
                The variable name to bind.
            value (Optional[Union[str, int, float, bool, list]]):
                The variable value to bind.
        Returns:
            MessageParam: A new MessageParam instance with bound variables.
        """

    def bind_mut(
        self,
        name: Optional[str] = None,
        value: Optional[str | int | float | bool | list] = None,
    ) -> None:
        """Bind variables to the message content in place.
        Args:
            name (Optional[str]):
                The variable name to bind.
            value (Optional[Union[str, int, float, bool, list]]):
                The variable value to bind.
        Returns:
            None
        """

    def model_dump(self) -> dict:
        """Dump the message to a dictionary."""

class Metadata:
    """Request metadata.

    Metadata associated with the API request.

    Examples:
        >>> metadata = Metadata(user_id="user_123")
    """

    def __init__(self, user_id: Optional[str] = None) -> None:
        """Initialize metadata.

        Args:
            user_id (Optional[str]):
                External user identifier
        """

class CacheControl:
    """Cache control configuration.

    Controls prompt caching behavior.

    Examples:
        >>> # 5 minute cache
        >>> cache = CacheControl(cache_type="ephemeral", ttl="5m")
        >>>
        >>> # 1 hour cache
        >>> cache = CacheControl(cache_type="ephemeral", ttl="1h")
    """

    def __init__(self, cache_type: str, ttl: Optional[str] = None) -> None:
        """Initialize cache control.

        Args:
            cache_type (str):
                Cache type (typically "ephemeral")
            ttl (Optional[str]):
                Time-to-live ("5m" or "1h")
        """

class AnthropicTool:
    """Tool definition for Anthropic API.

    Defines a tool that Claude can use.

    Examples:
        >>> schema = {
        ...     "type": "object",
        ...     "properties": {
        ...         "location": {"type": "string"}
        ...     },
        ...     "required": ["location"]
        ... }
        >>> tool = AnthropicTool(
        ...     name="get_weather",
        ...     description="Get weather for a location",
        ...     input_schema=schema,
        ...     cache_control=None
        ... )
    """

    def __init__(
        self,
        name: str,
        description: Optional[str] = None,
        input_schema: Any = None,
        cache_control: Optional[CacheControl] = None,
    ) -> None:
        """Initialize tool definition.

        Args:
            name (str):
                Tool name
            description (Optional[str]):
                Tool description
            input_schema (Any):
                JSON schema for tool input
            cache_control (Optional[CacheControl]):
                Cache control settings
        """

class AnthropicThinkingConfig:
    """Configuration for extended thinking.

    Controls Claude's extended thinking feature.

    Examples:
        >>> # Enable thinking with budget
        >>> config = AnthropicThinkingConfig(type="enabled", budget_tokens=2000)
        >>>
        >>> # Disable thinking
        >>> config = AnthropicThinkingConfig(type="disabled", budget_tokens=None)
    """

    def __init__(
        self,
        type: str,
        budget_tokens: Optional[int] = None,
    ) -> None:
        """Initialize thinking configuration.

        Args:
            type (str):
                Configuration type ("enabled" or "disabled")
            budget_tokens (Optional[int]):
                Token budget for thinking
        """

    @property
    def type(self) -> str:
        """Configuration type."""

    @property
    def budget_tokens(self) -> Optional[int]:
        """Token budget."""

class AnthropicToolChoice:
    """Tool choice configuration.

    Controls how Claude uses tools.

    Examples:
        >>> # Automatic tool choice
        >>> choice = AnthropicToolChoice(
        ...     type="auto",
        ...     disable_parallel_tool_use=False,
        ...     name=None
        ... )
        >>>
        >>> # Specific tool
        >>> choice = AnthropicToolChoice(
        ...     type="tool",
        ...     disable_parallel_tool_use=False,
        ...     name="get_weather"
        ... )
        >>>
        >>> # No tools
        >>> choice = AnthropicToolChoice(
        ...     type="none",
        ...     disable_parallel_tool_use=None,
        ...     name=None
        ... )
    """

    def __init__(
        self,
        type: str,
        disable_parallel_tool_use: Optional[bool] = None,
        name: Optional[str] = None,
    ) -> None:
        """Initialize tool choice configuration.

        Args:
            type (str):
                Choice type ("auto", "any", "tool", "none")
            disable_parallel_tool_use (Optional[bool]):
                Whether to disable parallel tool use
            name (Optional[str]):
                Specific tool name (required if type is "tool")
        """

    @property
    def type(self) -> str:
        """Choice type."""

    @property
    def disable_parallel_tool_use(self) -> Optional[bool]:
        """Disable parallel tool use."""

    @property
    def name(self) -> Optional[str]:
        """Tool name."""

class AnthropicSettings:
    """Settings for Anthropic chat completion requests.

    Comprehensive configuration for chat completion behavior.

    Examples:
        >>> # Basic settings
        >>> settings = AnthropicSettings(
        ...     max_tokens=1024,
        ...     temperature=0.7
        ... )
        >>>
        >>> # Advanced settings with tools
        >>> tool = AnthropicTool(name="get_weather", ...)
        >>> choice = AnthropicToolChoice(type="auto")
        >>> settings = AnthropicSettings(
        ...     max_tokens=2048,
        ...     temperature=0.5,
        ...     tools=[tool],
        ...     tool_choice=choice
        ... )
    """

    def __init__(
        self,
        max_tokens: int = 4096,
        metadata: Optional[Metadata] = None,
        service_tier: Optional[str] = None,
        stop_sequences: Optional[List[str]] = None,
        stream: Optional[bool] = None,
        system: Optional[str] = None,
        temperature: Optional[float] = None,
        thinking: Optional[AnthropicThinkingConfig] = None,
        top_k: Optional[int] = None,
        top_p: Optional[float] = None,
        tools: Optional[List[AnthropicTool]] = None,
        tool_choice: Optional[AnthropicToolChoice] = None,
        extra_body: Optional[Any] = None,
    ) -> None:
        """Initialize Anthropic settings.

        Args:
            max_tokens (int):
                Maximum tokens to generate
            metadata (Optional[Metadata]):
                Request metadata
            service_tier (Optional[str]):
                Service tier ("auto" or "standard_only")
            stop_sequences (Optional[List[str]]):
                Stop sequences
            stream (Optional[bool]):
                Enable streaming
            system (Optional[str]):
                System prompt
            temperature (Optional[float]):
                Sampling temperature (0.0-1.0)
            thinking (Optional[AnthropicThinkingConfig]):
                Thinking configuration
            top_k (Optional[int]):
                Top-k sampling parameter
            top_p (Optional[float]):
                Nucleus sampling parameter
            tools (Optional[List[AnthropicTool]]):
                Available tools
            tool_choice (Optional[AnthropicToolChoice]):
                Tool choice configuration
            extra_body (Optional[Any]):
                Additional request parameters
        """

    @property
    def max_tokens(self) -> int:
        """Maximum tokens."""

    @property
    def metadata(self) -> Optional[Metadata]:
        """Request metadata."""

    @property
    def service_tier(self) -> Optional[str]:
        """Service tier."""

    @property
    def stop_sequences(self) -> Optional[List[str]]:
        """Stop sequences."""

    @property
    def stream(self) -> Optional[bool]:
        """Streaming enabled."""

    @property
    def system(self) -> Optional[str]:
        """System prompt."""

    @property
    def temperature(self) -> Optional[float]:
        """Sampling temperature."""

    @property
    def thinking(self) -> Optional[AnthropicThinkingConfig]:
        """Thinking configuration."""

    @property
    def top_k(self) -> Optional[int]:
        """Top-k parameter."""

    @property
    def top_p(self) -> Optional[float]:
        """Top-p parameter."""

    @property
    def tools(self) -> Optional[List[AnthropicTool]]:
        """Available tools."""

    @property
    def tool_choice(self) -> Optional[AnthropicToolChoice]:
        """Tool choice configuration."""

    @property
    def extra_body(self) -> Optional[Any]:
        """Extra request parameters."""

    def __str__(self) -> str:
        """String representation."""

    def model_dump(self) -> Dict[str, Any]:
        """Convert settings to dictionary."""

class SystemPrompt:
    """System prompt for Anthropic messages.

    System-level instructions for Claude.

    Examples:
        >>> # Simple system prompt
        >>> prompt = SystemPrompt(content="You are a helpful assistant.")
        >>>
        >>> # System prompt with multiple blocks
        >>> blocks = [
        ...     TextBlockParam(text="You are helpful.", cache_control=None, citations=None),
        ...     TextBlockParam(text="Be concise.", cache_control=None, citations=None)
        ... ]
        >>> prompt = SystemPrompt(content=blocks)
    """

    def __init__(self, content: Any) -> None:
        """Initialize system prompt.

        Args:
            content (Any):
                System prompt content (string or list of TextBlockParam)
        """

    @property
    def content(self) -> List[TextBlockParam]:
        """System prompt content blocks."""

# ============================================================================
# Response Types
# ============================================================================

class CitationCharLocation:
    """Character-level citation location in response.

    Citation with character-level location information.

    Examples:
        >>> citation = CitationCharLocation(...)
        >>> print(citation.cited_text)
        >>> print(f"Characters {citation.start_char_index}-{citation.end_char_index}")
    """

    @property
    def cited_text(self) -> str:
        """Cited text."""

    @property
    def document_index(self) -> int:
        """Document index."""

    @property
    def document_title(self) -> str:
        """Document title."""

    @property
    def end_char_index(self) -> int:
        """End character index."""

    @property
    def file_id(self) -> str:
        """File ID."""

    @property
    def start_char_index(self) -> int:
        """Start character index."""

    @property
    def type(self) -> str:
        """Citation type."""

class CitationPageLocation:
    """Page-level citation location in response.

    Citation with page-level location information.

    Examples:
        >>> citation = CitationPageLocation(...)
        >>> print(f"Pages {citation.start_page_number}-{citation.end_page_number}")
    """

    @property
    def cited_text(self) -> str:
        """Cited text."""

    @property
    def document_index(self) -> int:
        """Document index."""

    @property
    def document_title(self) -> str:
        """Document title."""

    @property
    def end_page_number(self) -> int:
        """End page number."""

    @property
    def file_id(self) -> str:
        """File ID."""

    @property
    def start_page_number(self) -> int:
        """Start page number."""

    @property
    def type(self) -> str:
        """Citation type."""

class CitationContentBlockLocation:
    """Content block citation location in response.

    Citation with content block-level location information.

    Examples:
        >>> citation = CitationContentBlockLocation(...)
        >>> print(f"Blocks {citation.start_block_index}-{citation.end_block_index}")
    """

    @property
    def cited_text(self) -> str:
        """Cited text."""

    @property
    def document_index(self) -> int:
        """Document index."""

    @property
    def document_title(self) -> str:
        """Document title."""

    @property
    def end_block_index(self) -> int:
        """End block index."""

    @property
    def file_id(self) -> str:
        """File ID."""

    @property
    def start_block_index(self) -> int:
        """Start block index."""

    @property
    def type(self) -> str:
        """Citation type."""

class CitationsWebSearchResultLocation:
    """Web search result citation location in response.

    Citation from a web search result.

    Examples:
        >>> citation = CitationsWebSearchResultLocation(...)
        >>> print(f"{citation.title}: {citation.url}")
    """

    @property
    def cited_text(self) -> str:
        """Cited text."""

    @property
    def encrypted_index(self) -> str:
        """Encrypted index."""

    @property
    def title(self) -> str:
        """Result title."""

    @property
    def type(self) -> str:
        """Citation type."""

    @property
    def url(self) -> str:
        """Result URL."""

class CitationsSearchResultLocation:
    """Search result citation location in response.

    Citation from a search result with block-level information.

    Examples:
        >>> citation = CitationsSearchResultLocation(...)
        >>> print(f"{citation.title} from {citation.source}")
    """

    @property
    def cited_text(self) -> str:
        """Cited text."""

    @property
    def end_block_index(self) -> int:
        """End block index."""

    @property
    def search_result_index(self) -> int:
        """Search result index."""

    @property
    def source(self) -> str:
        """Result source."""

    @property
    def start_block_index(self) -> int:
        """Start block index."""

    @property
    def title(self) -> str:
        """Result title."""

    @property
    def type(self) -> str:
        """Citation type."""

class TextBlock:
    """Text content block in response.

    Text content with optional citations.

    Examples:
        >>> block = response.content[0]
        >>> print(block.text)
        >>> if block.citations:
        ...     for citation in block.citations:
        ...         print(citation)
    """

    @property
    def text(self) -> str:
        """Text content."""

    @property
    def citations(self) -> Optional[List[Any]]:
        """Citations."""

    @property
    def type(self) -> str:
        """Block type."""

class ThinkingBlock:
    """Thinking content block in response.

    Claude's internal thinking process.

    Examples:
        >>> block = response.content[0]
        >>> print(block.thinking)
        >>> if block.signature:
        ...     print(f"Signature: {block.signature}")
    """

    @property
    def thinking(self) -> str:
        """Thinking content."""

    @property
    def signature(self) -> Optional[str]:
        """Cryptographic signature."""

    @property
    def type(self) -> str:
        """Block type."""

class RedactedThinkingBlock:
    """Redacted thinking content block in response.

    Redacted version of thinking content.

    Examples:
        >>> block = response.content[0]
        >>> print(block.data)
    """

    @property
    def data(self) -> str:
        """Redacted data."""

    @property
    def type(self) -> str:
        """Block type."""

class ToolUseBlock:
    """Tool use content block in response.

    Represents a tool call from Claude.

    Examples:
        >>> block = response.content[0]
        >>> print(f"Tool: {block.name}")
        >>> print(f"ID: {block.id}")
        >>> print(f"Input: {block.input}")
    """

    @property
    def id(self) -> str:
        """Tool call ID."""

    @property
    def name(self) -> str:
        """Tool name."""

    @property
    def type(self) -> str:
        """Block type."""

class ServerToolUseBlock:
    """Server tool use content block in response.

    Represents a server-side tool call from Claude.

    Examples:
        >>> block = response.content[0]
        >>> print(f"Server tool: {block.name}")
    """

    @property
    def id(self) -> str:
        """Tool call ID."""

    @property
    def name(self) -> str:
        """Tool name."""

    @property
    def type(self) -> str:
        """Block type."""

class WebSearchResultBlock:
    """Web search result block in response.

    Single web search result.

    Examples:
        >>> result = block.content[0]
        >>> print(f"{result.title}: {result.url}")
        >>> if result.page_age:
        ...     print(f"Age: {result.page_age}")
    """

    @property
    def encrypted_content(self) -> str:
        """Encrypted content."""

    @property
    def page_age(self) -> Optional[str]:
        """Page age."""

    @property
    def title(self) -> str:
        """Result title."""

    @property
    def type(self) -> str:
        """Block type."""

    @property
    def url(self) -> str:
        """Result URL."""

class WebSearchToolResultError:
    """Web search tool error result.

    Error information from web search tool.

    Examples:
        >>> error = block.content
        >>> print(f"Error: {error.error_code}")
    """

    @property
    def error_code(self) -> str:
        """Error code."""

    @property
    def type(self) -> str:
        """Error type."""

class WebSearchToolResultBlock:
    """Web search tool result block in response.

    Contains web search results or error.

    Examples:
        >>> block = response.content[0]
        >>> print(f"Tool use ID: {block.tool_use_id}")
        >>> if isinstance(block.content, list):
        ...     for result in block.content:
        ...         print(result.title)
    """

    @property
    def content(self) -> Any:
        """Search results or error."""

    @property
    def tool_use_id(self) -> str:
        """Tool use ID."""

    @property
    def type(self) -> str:
        """Block type."""

class StopReason:
    """Reason for generation stopping.

    Indicates why Claude stopped generating.

    Examples:
        >>> reason = response.stop_reason
        >>> if reason == StopReason.EndTurn:
        ...     print("Natural stopping point")
    """

    EndTurn = "StopReason"
    """Natural stopping point reached"""

    MaxTokens = "StopReason"
    """Maximum token limit reached"""

    StopSequence = "StopReason"
    """Stop sequence encountered"""

    ToolUse = "StopReason"
    """Tool was invoked"""

class AnthropicUsage:
    """Token usage statistics.

    Token usage information for the request.

    Examples:
        >>> usage = response.usage
        >>> print(f"Input tokens: {usage.input_tokens}")
        >>> print(f"Output tokens: {usage.output_tokens}")
        >>> print(f"Total: {usage.input_tokens + usage.output_tokens}")
        >>> if usage.cache_read_input_tokens:
        ...     print(f"Cache hits: {usage.cache_read_input_tokens}")
    """

    @property
    def input_tokens(self) -> int:
        """Input tokens used."""

    @property
    def output_tokens(self) -> int:
        """Output tokens generated."""

    @property
    def cache_creation_input_tokens(self) -> Optional[int]:
        """Tokens used to create cache."""

    @property
    def cache_read_input_tokens(self) -> Optional[int]:
        """Tokens read from cache."""

    @property
    def service_tier(self) -> Optional[str]:
        """Service tier used."""

class AnthropicMessageResponse:
    """Response from Anthropic chat completion API.

    Complete response containing generated content and metadata.

    Examples:
        >>> response = AnthropicMessageResponse(...)
        >>> print(response.content[0].text)
        >>> print(f"Stop reason: {response.stop_reason}")
        >>> print(f"Usage: {response.usage.total_tokens} tokens")
    """

    @property
    def id(self) -> str:
        """Response ID."""

    @property
    def model(self) -> str:
        """Model used."""

    @property
    def role(self) -> str:
        """Message role (always 'assistant')."""

    @property
    def stop_reason(self) -> Optional[StopReason]:
        """Reason for stopping."""

    @property
    def stop_sequence(self) -> Optional[str]:
        """Stop sequence matched."""

    @property
    def type(self) -> str:
        """Response type."""

    @property
    def usage(self) -> AnthropicUsage:
        """Token usage statistics."""

    @property
    def content(self) -> List[Any]:
        """Generated content blocks."""

###### __potatohead__.mock module ######

class LLMTestServer:
    """
    Mock server for OpenAI API.
    This class is used to simulate the OpenAI API for testing purposes.
    """

    def __init__(self):
        """Initialize the mock server."""

    def __enter__(self):
        """
        Start the mock server.
        """

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Stop the mock server.
        """

### tracing.pyi ###
class TagRecord:
    """Represents a single tag record associated with an entity."""

    entity_type: str
    entity_id: str
    key: str
    value: str

class Attribute:
    """Represents a key-value attribute associated with a span."""

    key: str
    value: Any

class SpanEvent:
    """Represents an event within a span."""

    timestamp: datetime.datetime
    name: str
    attributes: List[Attribute]
    dropped_attributes_count: int

class SpanLink:
    """Represents a link to another span."""

    trace_id: str
    span_id: str
    trace_state: str
    attributes: List[Attribute]
    dropped_attributes_count: int

class TraceBaggageRecord:
    """Represents a single baggage record associated with a trace."""

    created_at: datetime.datetime
    trace_id: str
    scope: str
    key: str
    value: str

class TraceFilters:
    """A struct for filtering traces, generated from Rust pyclass."""

    service_name: Optional[str]
    has_errors: Optional[bool]
    status_code: Optional[int]
    start_time: Optional[datetime.datetime]
    end_time: Optional[datetime.datetime]
    limit: Optional[int]
    cursor_created_at: Optional[datetime.datetime]
    cursor_trace_id: Optional[str]

    def __init__(
        self,
        service_name: Optional[str] = None,
        has_errors: Optional[bool] = None,
        status_code: Optional[int] = None,
        start_time: Optional[datetime.datetime] = None,
        end_time: Optional[datetime.datetime] = None,
        limit: Optional[int] = None,
        cursor_created_at: Optional[datetime.datetime] = None,
        cursor_trace_id: Optional[str] = None,
    ) -> None:
        """Initialize trace filters.

        Args:
            service_name:
                Service name filter
            has_errors:
                Filter by presence of errors
            status_code:
                Filter by root span status code
            start_time:
                Start time boundary (UTC)
            end_time:
                End time boundary (UTC)
            limit:
                Maximum number of results to return
            cursor_created_at:
                Pagination cursor: created at timestamp
            cursor_trace_id:
                Pagination cursor: trace ID
        """

class TraceMetricBucket:
    """Represents aggregated trace metrics for a specific time bucket."""

    bucket_start: datetime.datetime
    trace_count: int
    avg_duration_ms: float
    p50_duration_ms: Optional[float]
    p95_duration_ms: Optional[float]
    p99_duration_ms: Optional[float]
    error_rate: float

class TraceListItem:
    """Represents a summary item for a trace in a list view."""

    trace_id: str
    service_name: str
    scope: str
    root_operation: Optional[str]
    start_time: datetime.datetime
    end_time: Optional[datetime.datetime]
    duration_ms: Optional[int]
    status_code: int
    status_message: Optional[str]
    span_count: Optional[int]
    has_errors: bool
    error_count: int
    created_at: datetime.datetime

class TraceSpan:
    """Detailed information for a single span within a trace."""

    trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    span_name: str
    span_kind: Optional[str]
    start_time: datetime.datetime
    end_time: Optional[datetime.datetime]
    duration_ms: Optional[int]
    status_code: int
    status_message: Optional[str]
    attributes: List[Attribute]
    events: List[SpanEvent]
    links: List[SpanLink]
    depth: int
    path: List[str]
    root_span_id: str
    span_order: int
    input: Any
    output: Any

def get_function_type(func: Callable[..., Any]) -> "FunctionType":
    """Determine the function type (sync, async, generator, async generator).

    Args:
        func (Callable[..., Any]):
            The function to analyze.
    """

def get_tracing_headers_from_current_span() -> Dict[str, str]:
    """Get tracing headers from the current active span and global propagator.

    Returns:
        Dict[str, str]:
            A dictionary of tracing headers.
    """

class OtelProtocol:
    """Enumeration of protocols for HTTP exporting."""

    HttpBinary: "OtelProtocol"
    HttpJson: "OtelProtocol"

class SpanKind:
    """Enumeration of span kinds."""

    Internal: "SpanKind"
    Server: "SpanKind"
    Client: "SpanKind"
    Producer: "SpanKind"
    Consumer: "SpanKind"

class FunctionType:
    """Enumeration of function types."""

    Sync: "FunctionType"
    Async: "FunctionType"
    SyncGenerator: "FunctionType"
    AsyncGenerator: "FunctionType"

class BatchConfig:
    """Configuration for batch exporting of spans."""

    def __init__(
        self,
        max_queue_size: int = 2048,
        scheduled_delay_ms: int = 5000,
        max_export_batch_size: int = 512,
    ) -> None:
        """Initialize the BatchConfig.

        Args:
            max_queue_size (int):
                The maximum queue size for spans. Defaults to 2048.
            scheduled_delay_ms (int):
                The delay in milliseconds between export attempts. Defaults to 5000.
            max_export_batch_size (int):
                The maximum batch size for exporting spans. Defaults to 512.
        """

def init_tracer(
    service_name: str = "scouter_service",
    scope: str = "scouter.tracer.{version}",
    transport_config: Optional[HttpConfig | KafkaConfig | RabbitMQConfig | RedisConfig | GrpcConfig] = None,
    exporter: Optional[HttpSpanExporter | GrpcSpanExporter | StdoutSpanExporter | TestSpanExporter] = None,
    batch_config: Optional[BatchConfig] = None,
    sample_ratio: Optional[float] = None,
) -> None:
    """
    Initialize the tracer for a service with dual export capability.
    ```
    ╔════════════════════════════════════════════╗
    ║          DUAL EXPORT ARCHITECTURE          ║
    ╠════════════════════════════════════════════╣
    ║                                            ║
    ║  Your Application                          ║
    ║       │                                    ║
    ║       │  init_tracer()                     ║
    ║       │                                    ║
    ║       ├──────────────────┬                 ║
    ║       │                  │                 ║
    ║       ▼                  ▼                 ║
    ║  ┌─────────────┐   ┌──────────────┐        ║
    ║  │  Transport  │   │   Optional   │        ║
    ║  │   to        │   │     OTEL     │        ║
    ║  │  Scouter    │   │  Exporter    │        ║
    ║  │  (Required) │   │              │        ║
    ║  └──────┬──────┘   └──────┬───────┘        ║
    ║         │                 │                ║
    ║         │                 │                ║
    ║    ┌────▼────┐       ┌────▼────┐           ║
    ║    │ Scouter │       │  OTEL   │           ║
    ║    │ Server  │       │Collector│           ║
    ║    └─────────┘       └─────────┘           ║
    ║                                            ║
    ╚════════════════════════════════════════════╝
    ```
    Configuration Overview:
        This function sets up a service tracer with **mandatory** export to Scouter
        and **optional** export to OpenTelemetry-compatible backends.

    ```
    ┌─ REQUIRED: Scouter Export ────────────────────────────────────────────────┐
    │                                                                           │
    │  All spans are ALWAYS exported to Scouter via transport_config:           │
    │    • HttpConfig    → HTTP endpoint (default)                              │
    │    • GrpcConfig    → gRPC endpoint                                        │
    │    • KafkaConfig   → Kafka topic                                          │
    │    • RabbitMQConfig→ RabbitMQ queue                                       │
    │    • RedisConfig   → Redis stream/channel                                 │
    │                                                                           │
    └───────────────────────────────────────────────────────────────────────────┘

    ┌─ OPTIONAL: OTEL Export ───────────────────────────────────────────────────┐
    │                                                                           │
    │  Optionally export spans to external OTEL-compatible systems:             │
    │    • HttpSpanExporter   → OTEL Collector (HTTP)                           │
    │    • GrpcSpanExporter   → OTEL Collector (gRPC)                           │
    │    • StdoutSpanExporter → Console output (debugging)                      │
    │    • TestSpanExporter   → In-memory (testing)                             │
    │                                                                           │
    │  If None: Only Scouter export is active (NoOpExporter)                    │
    │                                                                           │
    └───────────────────────────────────────────────────────────────────────────┘
    ```

    Args:
        service_name (str):
            The **required** name of the service this tracer is associated with.
            This is typically a logical identifier for the application or component.
            Default: "scouter_service"

        scope (str):
            The scope for the tracer. Used to differentiate tracers by version
            or environment.
            Default: "scouter.tracer.{version}"

        transport_config (HttpConfig | GrpcConfig | KafkaConfig | RabbitMQConfig | RedisConfig | None):

            Configuration for sending spans to Scouter. If None, defaults to HttpConfig.

            Supported transports:
                • HttpConfig     : Export to Scouter via HTTP
                • GrpcConfig     : Export to Scouter via gRPC
                • KafkaConfig    : Export to Scouter via Kafka
                • RabbitMQConfig : Export to Scouter via RabbitMQ
                • RedisConfig    : Export to Scouter via Redis

        exporter (HttpSpanExporter | GrpcSpanExporter | StdoutSpanExporter | TestSpanExporter | None):

            Optional secondary exporter for OpenTelemetry-compatible backends.
            If None, spans are ONLY sent to Scouter (NoOpExporter used internally).

            Available exporters:
                • HttpSpanExporter   : Send to OTEL Collector via HTTP
                • GrpcSpanExporter   : Send to OTEL Collector via gRPC
                • StdoutSpanExporter : Write to stdout (debugging)
                • TestSpanExporter   : Collect in-memory (testing)

        batch_config (BatchConfig | None):
            Configuration for batch span export. If provided, spans are queued
            and exported in batches. If None and the exporter supports batching,
            default batch settings apply.

            Batching improves performance for high-throughput applications.

        sample_ratio (float | None):
            Sampling ratio for tracing. A value between 0.0 and 1.0.
            All provided values are clamped between 0.0 and 1.0.
            If None, all spans are sampled (no sampling).

    Examples:
        Basic setup (Scouter only via HTTP):
            >>> init_tracer(service_name="my-service")

        Scouter via Kafka + OTEL Collector:
            >>> init_tracer(
            ...     service_name="my-service",
            ...     transport_config=KafkaConfig(brokers="kafka:9092"),
            ...     exporter=HttpSpanExporter(
            ...         export_config=OtelExportConfig(
            ...             endpoint="http://otel-collector:4318"
            ...         )
            ...     )
            ... )

        Scouter via gRPC + stdout debugging:
            >>> init_tracer(
            ...     service_name="my-service",
            ...     transport_config=GrpcConfig(server_uri="grpc://scouter:50051"),
            ...     exporter=StdoutSpanExporter()
            ... )

    Notes:
        • Spans are ALWAYS exported to Scouter via transport_config
        • OTEL export via exporter is completely optional
        • Both exports happen in parallel without blocking each other
        • Use batch_config to optimize performance for high-volume tracing

    See Also:
        - HttpConfig, GrpcConfig, KafkaConfig, RabbitMQConfig, RedisConfig
        - HttpSpanExporter, GrpcSpanExporter, StdoutSpanExporter, TestSpanExporter
        - BatchConfig
    """

class ActiveSpan:
    """Represents an active tracing span."""

    @property
    def trace_id(self) -> str:
        """Get the trace ID of the current active span.

        Returns:
            str:
                The trace ID.
        """

    @property
    def span_id(self) -> str:
        """Get the span ID of the current active span.

        Returns:
            str:
                The span ID.
        """

    @property
    def context_id(self) -> str:
        """Get the context ID of the active span."""

    def set_attribute(self, key: str, value: SerializedType) -> None:
        """Set an attribute on the active span.

        Args:
            key (str):
                The attribute key.
            value (SerializedType):
                The attribute value.
        """

    def set_tag(self, key: str, value: str) -> None:
        """Set a tag on the active span. Tags are similar to attributes
        except they are often used for indexing and searching spans/traces.
        All tags are also set as attributes on the span. Before export, tags are
        extracted and stored in a separate backend table for efficient querying.

        Args:
            key (str):
                The tag key.
            value (str):
                The tag value.
        """

    def add_event(self, name: str, attributes: Any) -> None:
        """Add an event to the active span.

        Args:
            name (str):
                The name of the event.
            attributes (Any):
                Optional attributes for the event.
                Can be any serializable type or pydantic `BaseModel`.
        """

    def add_queue_item(
        self,
        alias: str,
        item: Union[Features, Metrics, GenAIEvalRecord],
    ) -> None:
        """Helpers to add queue entities into a specified queue associated with the active span.
        This is an convenience method that abstracts away the details of queue management and
        leverages tracing's sampling capabilities to control data ingestion. Thus, correlated queue
        records and spans/traces can be sampled together based on the same sampling decision.

        Args:
            alias (str):
                Alias of the queue to add the item into.
            item (Union[Features, Metrics, GenAIEvalRecord]):
                Item to add into the queue.
                Can be an instance for Features, Metrics, or GenAIEvalRecord.

        Example:
            ```python
            features = Features(
                features=[
                    Feature("feature_1", 1),
                    Feature("feature_2", 2.0),
                    Feature("feature_3", "value"),
                ]
            )
            span.add_queue_item(alias, features)
            ```
        """

    def set_status(self, status: str, description: Optional[str] = None) -> None:
        """Set the status of the active span.

        Args:
            status (str):
                The status code (e.g., "OK", "ERROR").
            description (Optional[str]):
                Optional description for the status.
        """

    def set_input(self, input: Any, max_length: int = 1000) -> None:
        """Set the input for the active span.

        Args:
            input (Any):
                The input to set. Can be any serializable primitive type (str, int, float, bool, list, dict),
                or a pydantic `BaseModel`.
            max_length (int):
                The maximum length for a given string input. Defaults to 1000.
        """

    def set_output(self, output: Any, max_length: int = 1000) -> None:
        """Set the output for the active span.

        Args:
            output (Any):
                The output to set. Can be any serializable primitive type (str, int, float, bool, list, dict),
                or a pydantic `BaseModel`.
            max_length (int):
                The maximum length for a given string output. Defaults to 1000.

        """

    def __enter__(self) -> "ActiveSpan":
        """Enter the span context."""

    def __exit__(
        self,
        exc_type: Optional[type],
        exc_value: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        """Exit the span context."""

    async def __aenter__(self) -> "ActiveSpan":
        """Enter the async span context."""

    async def __aexit__(
        self,
        exc_type: Optional[type],
        exc_value: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        """Exit the async span context."""

class BaseTracer:
    def __init__(self, name: str) -> None:
        """Initialize the BaseTracer with a service name.

        Args:
            name (str):
                The name of the service for tracing.
        """

    def set_scouter_queue(self, queue: "ScouterQueue") -> None:
        """Add a ScouterQueue to the tracer. This allows the tracer to manage
        and export queue entities in conjunction with span data for correlated
        monitoring and observability.

        Args:
            queue (ScouterQueue):
                The ScouterQueue instance to add.
        """

    def start_as_current_span(
        self,
        name: str,
        kind: Optional[SpanKind] = SpanKind.Internal,
        label: Optional[str] = None,
        attributes: Optional[dict[str, str]] = None,
        baggage: Optional[dict[str, str]] = None,
        tags: Optional[dict[str, str]] = None,
        parent_context_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        span_id: Optional[str] = None,
        remote_sampled: Optional[bool] = None,
    ) -> ActiveSpan:
        """Context manager to start a new span as the current span.

        Args:
            name (str):
                The name of the span.
            kind (Optional[SpanKind]):
                The kind of span (e.g., "SERVER", "CLIENT").
            label (Optional[str]):
                An optional label for the span.
            attributes (Optional[dict[str, str]]):
                Optional attributes to set on the span.
            baggage (Optional[dict[str, str]]):
                Optional baggage items to attach to the span.
            tags (Optional[dict[str, str]]):
                Optional tags to set on the span and trace.
            parent_context_id (Optional[str]):
                Optional parent span context ID.
            trace_id (Optional[str]):
                Optional trace ID to associate with the span. This is useful for
                when linking spans across different services or systems.
            span_id (Optional[str]):
                Optional span ID to associate with the span. This will be the parent span ID.
            remote_sampled (Optional[bool]):
                Optional flag indicating if the span was sampled remotely.
        Returns:
            ActiveSpan:
        """

    def _start_decorated_as_current_span(
        self,
        name: Optional[str],
        func: Callable[..., Any],
        func_args: tuple[Any, ...],
        kind: SpanKind = SpanKind.Internal,
        label: Optional[str] = None,
        attributes: List[dict[str, str]] = [],
        baggage: List[dict[str, str]] = [],
        tags: List[dict[str, str]] = [],
        parent_context_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        max_length: int = 1000,
        func_type: FunctionType = FunctionType.Sync,
        func_kwargs: Optional[dict[str, Any]] = None,
    ) -> ActiveSpan:
        """Context manager to start a new span as the current span for decorated functions.

        Args:
            name (Optional[str]):
                The name of the span. If None, defaults to the function name.
            func (Callable[..., Any]):
                The function being decorated.
            func_args (tuple[Any, ...]):
                The positional arguments passed to the function.
            kind (SpanKind):
                The kind of span (e.g., Internal, Server, Client).
            label (Optional[str]):
                An optional label for the span.
            attributes (Optional[dict[str, str]]):
                Optional attributes to set on the span.
            baggage (Optional[dict[str, str]]):
                Optional baggage items to attach to the span.
            tags (Optional[dict[str, str]]):
                Optional tags to set on the span.
            parent_context_id (Optional[str]):
                Optional parent span context ID.
            trace_id (Optional[str]):
                Optional trace ID to associate with the span. This is useful for
                when linking spans across different services or systems.
            max_length (int):
                The maximum length for string inputs/outputs. Defaults to 1000.
            func_type (FunctionType):
                The type of function being decorated (Sync, Async, Generator, AsyncGenerator).
            func_kwargs (Optional[dict[str, Any]]):
                The keyword arguments passed to the function.
        Returns:
            ActiveSpan:
                The active span context manager.
        """

    def current_span(self) -> ActiveSpan:
        """Get the current active span.

        Returns:
            ActiveSpan:
                The current active span.
                Raises an error if no active span exists.
        """

    def shutdown(self) -> None:
        """Shutdown the tracer and flush any remaining spans."""

def get_current_active_span(self) -> ActiveSpan:
    """Get the current active span.

    Returns:
        ActiveSpan:
            The current active span.
            Raises an error if no active span exists.
    """

class StdoutSpanExporter:
    """Exporter that outputs spans to standard output (stdout)."""

    def __init__(
        self,
        batch_export: bool = False,
        sample_ratio: Optional[float] = None,
    ) -> None:
        """Initialize the StdoutSpanExporter.

        Args:
            batch_export (bool):
                Whether to use batch exporting. Defaults to False.
            sample_ratio (Optional[float]):
                The sampling ratio for traces. If None, defaults to always sample.
        """

    @property
    def batch_export(self) -> bool:
        """Get whether batch exporting is enabled."""

    @property
    def sample_ratio(self) -> Optional[float]:
        """Get the sampling ratio."""

def flush_tracer() -> None:
    """Force flush the tracer's exporter."""

class OtelExportConfig:
    """Configuration for exporting spans."""

    def __init__(
        self,
        endpoint: Optional[str],
        protocol: OtelProtocol = OtelProtocol.HttpBinary,
        timeout: Optional[int] = None,
        compression: Optional[CompressionType] = None,
        headers: Optional[dict[str, str]] = None,
    ) -> None:
        """Initialize the ExportConfig.

        Args:
            endpoint (Optional[str]):
                The endpoint for exporting spans. Can be either an HTTP or gRPC endpoint.
            protocol (Protocol):
                The protocol to use for exporting spans. Defaults to HttpBinary.
            timeout (Optional[int]):
                The timeout for requests in seconds.
            compression (Optional[CompressionType]):
                The compression type for requests.
            headers (Optional[dict[str, str]]):
                Optional HTTP headers to include in requests.
        """

    @property
    def endpoint(self) -> Optional[str]:
        """Get the HTTP endpoint for exporting spans."""

    @property
    def protocol(self) -> OtelProtocol:
        """Get the protocol used for exporting spans."""

    @property
    def timeout(self) -> Optional[int]:
        """Get the timeout for requests in seconds."""

    @property
    def compression(self) -> Optional[CompressionType]:
        """Get the compression type used for exporting spans."""

    @property
    def headers(self) -> Optional[dict[str, str]]:
        """Get the HTTP headers used for exporting spans."""

class HttpSpanExporter:
    """Exporter that sends spans to an HTTP endpoint."""

    def __init__(
        self,
        batch_export: bool = True,
        export_config: Optional[OtelExportConfig] = None,
        sample_ratio: Optional[float] = None,
    ) -> None:
        """Initialize the HttpSpanExporter.

        Args:
            batch_export (bool):
                Whether to use batch exporting. Defaults to True.
            export_config (Optional[OtelExportConfig]):
                Configuration for exporting spans.
            sample_ratio (Optional[float]):
                The sampling ratio for traces. If None, defaults to always sample.
        """

    @property
    def sample_ratio(self) -> Optional[float]:
        """Get the sampling ratio."""

    @property
    def batch_export(self) -> bool:
        """Get whether batch exporting is enabled."""

    @property
    def endpoint(self) -> Optional[str]:
        """Get the HTTP endpoint for exporting spans."""

    @property
    def protocol(self) -> OtelProtocol:
        """Get the protocol used for exporting spans."""

    @property
    def timeout(self) -> Optional[int]:
        """Get the timeout for HTTP requests in seconds."""

    @property
    def headers(self) -> Optional[dict[str, str]]:
        """Get the HTTP headers used for exporting spans."""

    @property
    def compression(self) -> Optional[CompressionType]:
        """Get the compression type used for exporting spans."""

class GrpcSpanExporter:
    """Exporter that sends spans to a gRPC endpoint."""

    def __init__(
        self,
        batch_export: bool = True,
        export_config: Optional[OtelExportConfig] = None,
        sample_ratio: Optional[float] = None,
    ) -> None:
        """Initialize the GrpcSpanExporter.

        Args:
            batch_export (bool):
                Whether to use batch exporting. Defaults to True.
            export_config (Optional[OtelExportConfig]):
                Configuration for exporting spans.
            sample_ratio (Optional[float]):
                The sampling ratio for traces. If None, defaults to always sample.
        """

    @property
    def sample_ratio(self) -> Optional[float]:
        """Get the sampling ratio."""

    @property
    def batch_export(self) -> bool:
        """Get whether batch exporting is enabled."""

    @property
    def endpoint(self) -> Optional[str]:
        """Get the gRPC endpoint for exporting spans."""

    @property
    def protocol(self) -> OtelProtocol:
        """Get the protocol used for exporting spans."""

    @property
    def timeout(self) -> Optional[int]:
        """Get the timeout for gRPC requests in seconds."""

    @property
    def compression(self) -> Optional[CompressionType]:
        """Get the compression type used for exporting spans."""

class TraceRecord:
    created_at: datetime.datetime
    trace_id: str
    space: str
    name: str
    version: str
    scope: str
    trace_state: str
    start_time: datetime.datetime
    end_time: datetime.datetime
    duration_ms: int
    status: str
    root_span_id: str
    attributes: Optional[dict]

    def get_attributes(self) -> Dict[str, Any]: ...

class TraceSpanRecord:
    created_at: datetime.datetime
    span_id: str
    trace_id: str
    parent_span_id: Optional[str]
    space: str
    name: str
    version: str
    scope: str
    span_name: str
    span_kind: str
    start_time: datetime.datetime
    end_time: datetime.datetime
    duration_ms: int
    status_code: str
    status_message: str
    attributes: dict
    events: dict
    links: dict

    def get_attributes(self) -> Dict[str, Any]: ...
    def get_events(self) -> Dict[str, Any]: ...
    def get_links(self) -> Dict[str, Any]: ...
    def __str__(self) -> str: ...

class TestSpanExporter:
    """Exporter for testing that collects spans in memory."""

    def __init__(self, batch_export: bool = True) -> None:
        """Initialize the TestSpanExporter.

        Args:
            batch_export (bool):
                Whether to use batch exporting. Defaults to True.
        """

    @property
    def traces(self) -> list[TraceRecord]:
        """Get the collected trace records."""

    @property
    def spans(self) -> list[TraceSpanRecord]:
        """Get the collected trace span records."""

    @property
    def baggage(self) -> list[TraceBaggageRecord]:
        """Get the collected trace baggage records."""

    def clear(self) -> None:
        """Clear all collected trace records."""

def shutdown_tracer() -> None:
    """Shutdown the tracer and flush any remaining spans."""

### evaluate.pyi ###
class EvaluationTaskType:
    """Types of evaluation tasks for LLM assessments."""

    Assertion: "EvaluationTaskType"
    """Assertion-based evaluation task."""
    LLMJudge: "EvaluationTaskType"
    """LLM judge-based evaluation task."""
    HumanValidation: "EvaluationTaskType"
    """Human validation evaluation task."""
    TraceAssertion: "EvaluationTaskType"
    """Trace assertion-based evaluation task."""

class ComparisonOperator:
    """Comparison operators for assertion-based evaluations.

    Defines the available comparison operators that can be used to evaluate
    assertions against expected values in LLM evaluation workflows.

    Examples:
        >>> operator = ComparisonOperator.GreaterThan
        >>> operator = ComparisonOperator.Equal
    """

    Equals: "ComparisonOperator"
    """Equality comparison (==)"""

    NotEqual: "ComparisonOperator"
    """Inequality comparison (!=)"""

    GreaterThan: "ComparisonOperator"
    """Greater than comparison (>)"""

    GreaterThanOrEqual: "ComparisonOperator"
    """Greater than or equal comparison (>=)"""

    LessThan: "ComparisonOperator"
    """Less than comparison (<)"""

    LessThanOrEqual: "ComparisonOperator"
    """Less than or equal comparison (<=)"""

    Contains: "ComparisonOperator"
    """Contains substring or element (in)"""

    NotContains: "ComparisonOperator"
    """Does not contain substring or element (not in)"""

    StartsWith: "ComparisonOperator"
    """Starts with substring"""

    EndsWith: "ComparisonOperator"
    """Ends with substring"""

    Matches: "ComparisonOperator"
    """Matches regular expression pattern"""

    HasLengthGreaterThan: "ComparisonOperator"
    """Has specified length greater than"""

    HasLengthLessThan: "ComparisonOperator"
    """Has specified length less than"""

    HasLengthEqual: "ComparisonOperator"
    """Has specified length equal to"""

    HasLengthGreaterThanOrEqual: "ComparisonOperator"
    """Has specified length greater than or equal to"""

    HasLengthLessThanOrEqual: "ComparisonOperator"
    """Has specified length less than or equal to"""

    # type validations
    IsNumeric: "ComparisonOperator"
    """Is a numeric value"""

    IsString: "ComparisonOperator"
    """Is a string value"""

    IsBoolean: "ComparisonOperator"
    """Is a boolean value"""

    IsNull: "ComparisonOperator"
    """Is null (None) value"""

    IsArray: "ComparisonOperator"
    """Is an array (list) value"""

    IsObject: "ComparisonOperator"
    """Is an object (dict) value"""

    IsEmail: "ComparisonOperator"
    """Is a valid email format"""

    IsUrl: "ComparisonOperator"
    """Is a valid URL format"""

    IsUuid: "ComparisonOperator"
    """Is a valid UUID format"""

    IsIso8601: "ComparisonOperator"
    """Is a valid ISO 8601 date format"""

    IsJson: "ComparisonOperator"
    """Is a valid JSON format"""

    MatchesRegex: "ComparisonOperator"
    """Matches a regular expression pattern"""

    InRange: "ComparisonOperator"
    """Is within a specified numeric range"""

    NotInRange: "ComparisonOperator"
    """Is outside a specified numeric range"""

    IsPositive: "ComparisonOperator"
    """Is a positive number"""

    IsNegative: "ComparisonOperator"
    """Is a negative number"""
    IsZero: "ComparisonOperator"
    """Is zero"""

    ContainsAll: "ComparisonOperator"
    """Contains all specified elements"""

    ContainsAny: "ComparisonOperator"
    """Contains any of the specified elements"""

    ContainsNone: "ComparisonOperator"
    """Contains none of the specified elements"""

    IsEmpty: "ComparisonOperator"
    """Is empty"""

    IsNotEmpty: "ComparisonOperator"
    """Is not empty"""

    HasUniqueItems: "ComparisonOperator"
    """Has unique items"""

    IsAlphabetic: "ComparisonOperator"
    """Is alphabetic"""

    IsAlphanumeric: "ComparisonOperator"
    """Is alphanumeric"""

    IsLowerCase: "ComparisonOperator"
    """Is lowercase"""

    IsUpperCase: "ComparisonOperator"
    """Is uppercase"""

    ContainsWord: "ComparisonOperator"
    """Contains a specific word"""

    ApproximatelyEquals: "ComparisonOperator"
    """Approximately equals within a tolerance"""

class AssertionTask:
    """Assertion-based evaluation task for LLM monitoring.

    Defines a rule-based assertion that evaluates values extracted from LLM
    context/responses against expected conditions without requiring additional LLM calls.
    Assertions are efficient, deterministic evaluations ideal for validating
    structured outputs, checking thresholds, or verifying data constraints.

    Assertions can operate on:
        - Nested fields via dot-notation paths (e.g., "response.user.age")
        - Top-level context values when field_path is None
        - String, numeric, boolean, or collection values

    Common Use Cases:
        - Validate response structure ("response.status" == "success")
        - Check numeric thresholds ("response.confidence" >= 0.8)
        - Verify required fields exist ("response.user.id" is not None)
        - Validate string patterns ("response.language" contains "en")

    Examples:
        Basic numeric comparison:

        >>> # Context at runtime: {"response": {"user": {"age": 25}}}
        >>> task = AssertionTask(
        ...     id="check_user_age",
        ...     field_path="response.user.age",
        ...     operator=ComparisonOperator.GreaterThan,
        ...     expected_value=18,
        ...     description="Verify user is an adult"
        ... )

        Checking top-level fields:

        >>> # Context at runtime: {"user": {"age": 25}}
        >>> task = AssertionTask(
        ...     id="check_age",
        ...     field_path="user.age",
        ...     operator=ComparisonOperator.GreaterThanOrEqual,
        ...     expected_value=21,
        ...     description="Check minimum age requirement"
        ... )

        Operating on entire context (no nested path):

        >>> # Context at runtime: 25
        >>> task = AssertionTask(
        ...     id="age_threshold",
        ...     field_path=None,
        ...     operator=ComparisonOperator.GreaterThan,
        ...     expected_value=18,
        ...     description="Validate age value"
        ... )

        String validation:

        >>> # Context: {"response": {"status": "completed"}}
        >>> task = AssertionTask(
        ...     id="status_check",
        ...     field_path="response.status",
        ...     operator=ComparisonOperator.Equals,
        ...     expected_value="completed",
        ...     description="Verify completion status"
        ... )

        Collection membership:

        >>> # Context: {"response": {"tags": ["valid", "processed"]}}
        >>> task = AssertionTask(
        ...     id="tag_validation",
        ...     field_path="response.tags",
        ...     operator=ComparisonOperator.Contains,
        ...     expected_value="valid",
        ...     description="Check for required tag"
        ... )

        With dependencies:

        >>> task = AssertionTask(
        ...     id="confidence_check",
        ...     field_path="response.confidence",
        ...     operator=ComparisonOperator.GreaterThan,
        ...     expected_value=0.9,
        ...     description="High confidence validation",
        ...     depends_on=["status_check"]
        ... )

    Note:
        - Field paths use dot-notation for nested access
        - Field paths are case-sensitive
        - When field_path is None, the entire context is used as the value
        - Type mismatches between actual and expected values will fail the assertion
        - Dependencies are executed before this task
    """

    def __init__(
        self,
        id: str,
        expected_value: Any,
        operator: ComparisonOperator,
        field_path: Optional[str] = None,
        description: Optional[str] = None,
        depends_on: Optional[Sequence[str]] = None,
        condition: bool = False,
    ):
        """Initialize an assertion task for rule-based evaluation.

        Args:
            id:
                Unique identifier for the task. Will be converted to lowercase.
                Used to reference this task in dependencies and results.
            expected_value:
                The expected value to compare against. Can be any JSON-serializable
                type: str, int, float, bool, list, dict, or None.
            operator:
                Comparison operator to use for the assertion. Must be a
                ComparisonOperator enum value.
            field_path:
                Optional dot-notation path to extract value from context
                (e.g., "response.user.age"). If None, the entire context
                is used as the comparison value.
            description:
                Optional human-readable description of what this assertion validates.
                Useful for understanding evaluation results.
            depends_on:
                Optional list of task IDs that must complete successfully before
                this task executes. Empty list if not provided.
            condition:
                If True, this assertion task acts as a condition for subsequent tasks.
                If the assertion fails, dependent tasks will be skipped and this task
                will be excluded from final results.

        Raises:
            TypeError: If expected_value is not JSON-serializable or if operator
                is not a valid ComparisonOperator.
        """

    @property
    def id(self) -> str:
        """Unique task identifier (lowercase)."""

    @id.setter
    def id(self, id: str) -> None:
        """Set task identifier (will be converted to lowercase)."""

    @property
    def field_path(self) -> Optional[str]:
        """Dot-notation path to field in context, or None for entire context."""

    @field_path.setter
    def field_path(self, field_path: Optional[str]) -> None:
        """Set field path for value extraction."""

    @property
    def operator(self) -> ComparisonOperator:
        """Comparison operator for the assertion."""

    @operator.setter
    def operator(self, operator: ComparisonOperator) -> None:
        """Set comparison operator."""

    @property
    def expected_value(self) -> Any:
        """Expected value for comparison.

        Returns:
            The expected value as a Python object (deserialized from internal
            JSON representation).
        """

    @property
    def description(self) -> Optional[str]:
        """Human-readable description of the assertion."""

    @description.setter
    def description(self, description: Optional[str]) -> None:
        """Set assertion description."""

    @property
    def depends_on(self) -> List[str]:
        """List of task IDs this task depends on."""

    @depends_on.setter
    def depends_on(self, depends_on: List[str]) -> None:
        """Set task dependencies."""

    @property
    def condition(self) -> bool:
        """Indicates if this task is a condition for subsequent tasks."""

    @condition.setter
    def condition(self, condition: bool) -> None:
        """Set whether this task is a condition for subsequent tasks."""

    def __str__(self) -> str:
        """Return string representation of the assertion task."""

class LLMJudgeTask:
    """LLM-powered evaluation task for complex assessments.

    Uses an additional LLM call to evaluate responses based on sophisticated
    criteria that require reasoning, context understanding, or subjective judgment.
    LLM judges are ideal for evaluations that cannot be captured by deterministic
    rules, such as semantic similarity, quality assessment, or nuanced criteria.

    Unlike AssertionTask which provides efficient, deterministic rule-based evaluation,
    LLMJudgeTask leverages an LLM's reasoning capabilities for:
        - Semantic similarity and relevance assessment
        - Quality, coherence, and fluency evaluation
        - Factual accuracy and hallucination detection
        - Tone, sentiment, and style analysis
        - Custom evaluation criteria requiring judgment
        - Complex reasoning over multiple context elements

    The LLM judge executes a prompt that receives context (either raw or from
    dependencies) and returns a response that is then compared against the expected
    value using the specified operator.

    Common Use Cases:
        - Evaluate semantic similarity between generated and reference answers
        - Assess response quality on subjective criteria (helpfulness, clarity)
        - Detect factual inconsistencies or hallucinations
        - Score tone appropriateness for different audiences
        - Judge whether responses meet complex, nuanced requirements

    Examples:
        Basic relevance check using LLM judge:

        >>> # Define a prompt that evaluates relevance
        >>> relevance_prompt = Prompt(
        ...     system_instructions="Evaluate if the response is relevant to the query",
        ...     messages="Given the query '{{query}}' and response '{{response}}', rate the relevance from 0 to 10 as an integer.",
        ...     model="gpt-4",
        ...     provider= Provider.OpenAI,
        ...     output_type=Score # returns a structured output with schema {"score": float, "reason": str}
        ... )

        >>> # Context at runtime: {"query": "What is AI?", "response": "AI is..."}
        >>> task = LLMJudgeTask(
        ...     id="relevance_judge",
        ...     prompt=relevance_prompt,
        ...     expected_value=8,
        ...     field_path="score",
        ...     operator=ComparisonOperator.GreaterThanOrEqual,
        ...     description="Ensure response relevance score >= 8"
        ... )

        Factuality check with structured output:

        >>> # Prompt returns a Pydantic model with factuality assessment
        >>> from pydantic import BaseModel
        >>> class FactCheckResult(BaseModel):
        ...     is_factual: bool
        ...     confidence: float

        >>> fact_check_prompt = Prompt(
        ...     system_instructions="Verify factual claims in the response",
        ...     messages="Assess the factual accuracy of the response: '{{response}}'. Provide a JSON with fields 'is_factual' (bool) and 'confidence' (float).", # pylint: disable=line-too-long
        ...     model="gpt-4",
        ...     provider= Provider.OpenAI,
        ...     output_type=FactCheckResult
        ... )

        >>> # Context: {"response": "Paris is the capital of France"}
        >>> task = LLMJudgeTask(
        ...     id="fact_checker",
        ...     prompt=fact_check_prompt,
        ...     expected_value={"is_factual": True, "confidence": 0.95},
        ...     field_path="response",
        ...     operator=ComparisonOperator.Contains
        ... )

        Quality assessment with dependencies:

        >>> # This judge depends on previous relevance check
        >>> quality_prompt = Prompt(
        ...     system_instructions="Assess the overall quality of the response",
        ...     messages="Given the response '{{response}}', rate its quality from 0 to 5",
        ...     model="gemini-3.0-flash",
        ...     provider= Provider.Google,
        ...     output_type=Score
        ... )

        >>> task = LLMJudgeTask(
        ...     id="quality_judge",
        ...     prompt=quality_prompt,
        ...     expected_value=0.7,
        ...     field_path=None,
        ...     operator=ComparisonOperator.GreaterThan,
        ...     depends_on=["relevance_judge"],
        ...     description="Evaluate overall quality after relevance check"
        ... )
    Note:
        - LLM judge tasks incur additional latency and cost vs assertions
        - Scouter does not auto-inject any additional prompts or context apart from what is defined
          in the Prompt object
        - For tasks that contain dependencies, upstream results are passed as context to downstream tasks.
        - Use dependencies to chain evaluations and pass results between tasks
        - max_retries helps handle transient LLM failures (defaults to 3)
        - Field paths work the same as AssertionTask (dot-notation for nested access)
        - Consider cost/latency tradeoffs when designing judge evaluations
    """

    def __init__(
        self,
        id: str,
        prompt: Prompt,
        expected_value: Any,
        field_path: Optional[str],
        operator: ComparisonOperator,
        description: Optional[str] = None,
        depends_on: Optional[List[str]] = None,
        max_retries: Optional[int] = None,
        condition: bool = False,
    ):
        """Initialize an LLM judge task for advanced evaluation.

        Creates an evaluation task that uses an LLM to assess responses based on
        sophisticated criteria requiring reasoning or subjective judgment. The LLM
        receives context (raw or from dependencies) and returns a response that
        is compared against the expected value.

        Args:
            id (str):
                Unique identifier for the task. Will be converted to lowercase.
                Used to reference this task in dependencies and results.
            prompt (Prompt):
                Prompt configuration defining the LLM evaluation task.
            expected_value (Any):
                The expected value to compare against the LLM's response. Type depends
                on prompt response type. Can be any JSON-serializable type: str, int,
                float, bool, list, dict, or None.
            field_path (Optional[str]):
                Optional dot-notation path to extract value from context before passing
                to the LLM prompt (e.g., "response.text"), the entire response will be
                evaluated.
            operator (ComparisonOperator):
                Comparison operator to apply between LLM response and expected_value
            description (Optional[str]):
                Optional human-readable description of what this judge evaluates.
            depends_on (Optional[List[str]]):
                Optional list of task IDs that must complete successfully before this
                task executes. Results from dependencies are passed to the LLM prompt
                as additional context parameters. Empty list if not provided.
            max_retries (Optional[int]):
                Optional maximum number of retry attempts if the LLM call fails
                (network errors, rate limits, etc.). Defaults to 3 if not provided.
                Set to 0 to disable retries.
            condition (bool):
                If True, this judge task acts as a condition for subsequent tasks.
                If the judge fails, dependent tasks will be skipped and this task
                will be excluded from final results.
        """

    @property
    def id(self) -> str:
        """Unique task identifier (lowercase)."""

    @id.setter
    def id(self, id: str) -> None:
        """Set task identifier (will be converted to lowercase)."""

    @property
    def prompt(self) -> Prompt:
        """Prompt configuration for the LLM evaluation task.

        Defines the LLM model, evaluation instructions, and response format.
        The prompt must have response_type of Score or Pydantic.
        """

    @property
    def field_path(self) -> Optional[str]:
        """Dot-notation path to extract value from context before LLM evaluation.

        If specified, extracts nested value from context (e.g., "response.text")
        and passes it to the LLM prompt. If None, the entire context or
        dependency results are passed.
        """

    @property
    def operator(self) -> ComparisonOperator:
        """Comparison operator for evaluating LLM response against expected value.

        For Score responses: use numeric operators (GreaterThan, Equals, etc.)
        For Pydantic responses: use structural operators (Contains, Equals, etc.)
        """

    @property
    def expected_value(self) -> Any:
        """Expected value to compare against LLM response.

        Returns:
            The expected value as a Python object (deserialized from internal
            JSON representation).
        """

    @property
    def depends_on(self) -> List[str]:
        """List of task IDs this task depends on.

        Dependency results are passed to the LLM prompt as additional context
        parameters, enabling chained evaluations.
        """

    @depends_on.setter
    def depends_on(self, depends_on: List[str]) -> None:
        """Set task dependencies."""

    @property
    def max_retries(self) -> Optional[int]:
        """Maximum number of retry attempts for LLM call failures.

        Handles transient failures like network errors or rate limits.
        Defaults to 3 if not specified during initialization.
        """

    @max_retries.setter
    def max_retries(self, max_retries: Optional[int]) -> None:
        """Set maximum retry attempts."""

    @property
    def condition(self) -> bool:
        """Indicates if this task is a condition for subsequent tasks."""

    @condition.setter
    def condition(self, condition: bool) -> None:
        """Set whether this task is a condition for subsequent tasks."""

    def __str__(self) -> str:
        """Return string representation of the LLM judge task."""

class SpanStatus:
    """Status codes for trace spans.

    Represents the execution status of a span within a distributed trace,
    following OpenTelemetry status conventions.

    Examples:
        >>> status = SpanStatus.Ok
        >>> error_status = SpanStatus.Error
    """

    Ok: "SpanStatus"
    """Span completed successfully without errors."""

    Error: "SpanStatus"
    """Span encountered an error during execution."""

    Unset: "SpanStatus"
    """Span status has not been explicitly set."""

class AggregationType:
    """Aggregation operations for span attribute values.

    Defines how numeric or collection values should be aggregated across
    multiple spans matching a filter. Used in TraceAssertion.span_aggregation
    to compute statistics over filtered spans.

    Examples:
        >>> # Compute average duration across LLM spans
        >>> aggregation = AggregationType.Average
        >>>
        >>> # Count total spans matching filter
        >>> count = AggregationType.Count
    """

    Count: "AggregationType"
    """Count the number of spans matching the filter."""

    Sum: "AggregationType"
    """Sum numeric attribute values across spans."""

    Average: "AggregationType"
    """Calculate mean of numeric attribute values."""

    Min: "AggregationType"
    """Find minimum numeric attribute value."""

    Max: "AggregationType"
    """Find maximum numeric attribute value."""

    First: "AggregationType"
    """Get attribute value from first matching span (by start time)."""

    Last: "AggregationType"
    """Get attribute value from last matching span (by start time)."""

class SpanFilter:
    """Filter for selecting specific spans within a trace.

    Provides composable filtering logic to identify spans based on name,
    attributes, status, duration, or combinations thereof. Filters can be
    combined using and() and or() methods for complex queries.

    SpanFilter is used to target specific spans for assertions in
    TraceAssertionTask, enabling precise behavioral validation.

    Examples:
        Filter by exact span name:

        >>> filter = SpanFilter.by_name("llm.generate")

        Filter by name pattern (regex):

        >>> filter = SpanFilter.by_name_pattern(r"retry.*")

        Filter spans with specific attribute:

        >>> filter = SpanFilter.with_attribute("model")

        Filter spans with attribute value (note: requires PyValueWrapper):

        >>> # Note: In Python, pass native types; they're converted internally
        >>> # This is handled automatically by the with_attribute_value method
        >>> filter = SpanFilter.with_attribute_value("model", "gpt-4")

        Filter by span status:

        >>> filter = SpanFilter.with_status(SpanStatus.Error)

        Filter by duration constraints:

        >>> filter = SpanFilter.with_duration(min_ms=100, max_ms=5000)

        Combine filters with AND logic:

        >>> base = SpanFilter.by_name_pattern("llm.*")
        >>> with_model = base.and_(SpanFilter.with_attribute("model"))
        >>> # Matches spans: name matches "llm.*" AND has "model" attribute

        Combine filters with OR logic:

        >>> retries = SpanFilter.by_name_pattern("retry.*")
        >>> errors = SpanFilter.with_status(SpanStatus.Error)
        >>> either = retries.or_(errors)
        >>> # Matches spans: name matches "retry.*" OR status is Error

        Complex nested filter:

        >>> # Find LLM spans that either errored or took too long
        >>> llm_filter = SpanFilter.by_name_pattern("llm.*")
        >>> error_filter = SpanFilter.with_status(SpanStatus.Error)
        >>> slow_filter = SpanFilter.with_duration(min_ms=10000)
        >>> combined = llm_filter.and_(error_filter.or_(slow_filter))

    Note:
        - Filters are immutable; and() and or() return new filter instances
        - Regex patterns use standard regex syntax
        - Duration is measured in milliseconds
        - Attribute values are internally wrapped for type safety
    """

    class ByName:
        """Filter spans by exact name match."""

        name: str
        def and_(self, other: SpanFilter) -> SpanFilter: ...
        def or_(self, other: SpanFilter) -> SpanFilter: ...

    class ByNamePattern:
        """Filter spans by regex name pattern."""

        pattern: str
        def and_(self, other: SpanFilter) -> SpanFilter: ...
        def or_(self, other: SpanFilter) -> SpanFilter: ...

    class WithAttribute:
        """Filter spans with specific attribute key."""

        key: str
        def and_(self, other: SpanFilter) -> SpanFilter: ...
        def or_(self, other: SpanFilter) -> SpanFilter: ...

    class WithAttributeValue:
        """Filter spans with specific attribute key-value pair."""

        key: str
        value: object  # PyValueWrapper is internal, expose as object
        def and_(self, other: SpanFilter) -> SpanFilter: ...
        def or_(self, other: SpanFilter) -> SpanFilter: ...

    class WithStatus:
        """Filter spans by status code."""

        status: SpanStatus
        def and_(self, other: SpanFilter) -> SpanFilter: ...
        def or_(self, other: SpanFilter) -> SpanFilter: ...

    class WithDuration:
        """Filter spans with duration constraints."""

        min_ms: Optional[float]
        max_ms: Optional[float]
        def and_(self, other: SpanFilter) -> SpanFilter: ...
        def or_(self, other: SpanFilter) -> SpanFilter: ...

    class Sequence:
        """Match a sequence of span names in order."""

        names: List[str]
        def and_(self, other: SpanFilter) -> SpanFilter: ...
        def or_(self, other: SpanFilter) -> SpanFilter: ...

    class And:
        """Combine multiple filters with AND logic."""

        filters: List[SpanFilter]
        def and_(self, other: SpanFilter) -> SpanFilter: ...
        def or_(self, other: SpanFilter) -> SpanFilter: ...

    class Or:
        """Combine multiple filters with OR logic."""

        filters: List[SpanFilter]
        def and_(self, other: SpanFilter) -> SpanFilter: ...
        def or_(self, other: SpanFilter) -> SpanFilter: ...

    @staticmethod
    def by_name(name: str) -> "SpanFilter":
        """Filter spans by exact name match.

        Args:
            name (str):
                Exact span name to match (case-sensitive).

        Returns:
            SpanFilter that matches spans with the specified name.
        """

    @staticmethod
    def by_name_pattern(pattern: str) -> "SpanFilter":
        """Filter spans by regex name pattern.

        Args:
            pattern (str):
                Regular expression pattern to match span names.

        Returns:
            SpanFilter that matches spans whose names match the pattern.
        """

    @staticmethod
    def with_attribute(key: str) -> "SpanFilter":
        """Filter spans that have a specific attribute key.

        Args:
            key (str):
                Attribute key to check for existence.

        Returns:
            SpanFilter that matches spans with the specified attribute.
        """

    @staticmethod
    def with_attribute_value(key: str, value: "SerializedType") -> "SpanFilter":
        """Filter spans that have a specific attribute key-value pair.

        Args:
            key (str):
                Attribute key to check.
            value (SerializedType):
                Attribute value to match (must be JSON-serializable).

        Returns:
            SpanFilter that matches spans with the specified key-value pair.
        """

    @staticmethod
    def with_status(status: SpanStatus) -> "SpanFilter":
        """Filter spans by execution status.

        Args:
            status (SpanStatus):
                SpanStatus to match (Ok, Error, or Unset).

        Returns:
            SpanFilter that matches spans with the specified status.
        """

    @staticmethod
    def with_duration(min_ms: Optional[float] = None, max_ms: Optional[float] = None) -> "SpanFilter":
        """Filter spans by duration constraints.

        Args:
            min_ms (Optional[float]):
                Optional minimum duration in milliseconds.
            max_ms (Optional[float]):
                Optional maximum duration in milliseconds.

        Returns:
            SpanFilter that matches spans within the duration range.
            If both are None, matches all spans.
        """

    @staticmethod
    def sequence(names: List[str]) -> "SpanFilter":
        """Filter for spans appearing in specific order.

        Args:
            names (List[str]):
                List of span names that must appear in order.

        Returns:
            SpanFilter that matches the span sequence.
        """

    def and_(self, other: "SpanFilter") -> "SpanFilter":
        """Combine this filter with another using AND logic.

        Args:
            other (SpanFilter):
                Another SpanFilter to combine with.

        Returns:
            New SpanFilter matching spans that satisfy both conditions.
        """

    def or_(self, other: "SpanFilter") -> "SpanFilter":
        """Combine this filter with another using OR logic.

        Args:
            other (SpanFilter):
                Another SpanFilter to combine with.

        Returns:
            New SpanFilter matching spans that satisfy either condition.
        """

class TraceAssertion:
    """Assertion target for trace and span properties.

    Defines what aspect of a trace or its spans should be evaluated.
    TraceAssertion types fall into three categories:

    1. Span-level assertions: Evaluate properties of filtered spans
       (count, existence, attributes, duration, aggregations)

    2. Span collection assertions: Evaluate span sets and sequences
       (span_set for existence, span_sequence for ordering)

    3. Trace-level assertions: Evaluate entire trace properties
       (total duration, span count, error count, max depth)

    Each assertion type extracts a value that is then compared against
    an expected value using the operator specified in TraceAssertionTask.

    Examples:
        Check execution order of spans:

        >>> assertion = TraceAssertion.span_sequence([
        ...     "validate_input",
        ...     "process_data",
        ...     "generate_output"
        ... ])
        >>> # Use with SequenceMatches operator

        Check all required spans exist (order doesn't matter):

        >>> assertion = TraceAssertion.span_set([
        ...     "call_tool",
        ...     "run_agent",
        ...     "double_check"
        ... ])
        >>> # Use with ContainsAll operator

        Count spans matching a filter:

        >>> filter = SpanFilter.by_name("retry_operation")
        >>> assertion = TraceAssertion.span_count(filter)
        >>> # Use with LessThanOrEqual to limit retries

        Check if specific span exists:

        >>> filter = SpanFilter.by_name_pattern("llm.*")
        >>> assertion = TraceAssertion.span_exists(filter)
        >>> # Use with Equals(True) to verify LLM was called

        Get attribute value from span:

        >>> filter = SpanFilter.by_name("llm.generate")
        >>> assertion = TraceAssertion.span_attribute(filter, "model")
        >>> # Use with Equals("gpt-4") to verify model

        Get span duration:

        >>> filter = SpanFilter.by_name("database_query")
        >>> assertion = TraceAssertion.span_duration(filter)
        >>> # Use with LessThan to enforce SLA

        Aggregate numeric attribute across spans:

        >>> filter = SpanFilter.by_name_pattern("llm.*")
        >>> assertion = TraceAssertion.span_aggregation(
        ...     filter,
        ...     "token_count",
        ...     AggregationType.Sum
        ... )
        >>> # Use with LessThan to limit total tokens

        Check total trace duration:

        >>> assertion = TraceAssertion.trace_duration()
        >>> # Use with LessThan to enforce response time

        Count total spans in trace:

        >>> assertion = TraceAssertion.trace_span_count()
        >>> # Use with range operators to validate complexity

        Count error spans:

        >>> assertion = TraceAssertion.trace_error_count()
        >>> # Use with Equals(0) to ensure no errors

        Count unique services involved:

        >>> assertion = TraceAssertion.trace_service_count()
        >>> # Use to validate service boundaries

        Get maximum span depth:

        >>> assertion = TraceAssertion.trace_max_depth()
        >>> # Use to detect deep recursion

        Get trace-level attribute:

        >>> assertion = TraceAssertion.trace_attribute("user_id")
        >>> # Use to validate trace context

    Note:
        - Span assertions require SpanFilter to target specific spans
        - Aggregations only work on numeric attributes
        - Sequence matching preserves span order by start time
        - Trace-level assertions evaluate the entire trace without filtering
    """

    class SpanSequence:
        """Extracts a sequence of span names in order."""

        span_names: List[str]

    class SpanSet:
        """Checks for existence of all specified span names."""

        span_names: List[str]

    class SpanCount:
        """Counts spans matching a filter."""

        filter: SpanFilter

    class SpanExists:
        """Checks if any span matches a filter."""

        filter: SpanFilter

    class SpanAttribute:
        """Extracts attribute value from span matching filter."""

        filter: SpanFilter
        attribute_key: str

    class SpanDuration:
        """Extracts duration of span matching filter."""

        filter: SpanFilter

    class SpanAggregation:
        """Aggregates numeric attribute across filtered spans."""

        filter: SpanFilter
        attribute_key: str
        aggregation: AggregationType

    class TraceAttribute:
        """Extracts trace-level attribute value."""

        attribute_key: str

    @staticmethod
    def span_sequence(span_names: List[str]) -> "TraceAssertion":
        """Assert spans appear in specific order.

        Args:
            span_names (List[str]):
                List of span names that must appear sequentially.

        Returns:
            TraceAssertion that extracts the span sequence.
            Use with SequenceMatches operator.
        """

    @staticmethod
    def span_set(span_names: List[str]) -> "TraceAssertion":
        """Assert all specified spans exist (order independent).

        Args:
            span_names (List[str]):
                List of span names that must all be present.

        Returns:
            TraceAssertion that checks for span set membership.
            Use with ContainsAll operator.
        """

    @staticmethod
    def span_count(filter: SpanFilter) -> "TraceAssertion":
        """Count spans matching the filter.

        Args:
            filter (SpanFilter):
                SpanFilter defining which spans to count.

        Returns:
            TraceAssertion that extracts the span count.
            Use with numeric comparison operators.
        """

    @staticmethod
    def span_exists(filter: SpanFilter) -> "TraceAssertion":
        """Check if any span matches the filter.

        Args:
            filter (SpanFilter):
                SpanFilter defining which span to look for.

        Returns:
            TraceAssertion that extracts boolean existence.
            Use with Equals(True/False).
        """

    @staticmethod
    def span_attribute(filter: SpanFilter, attribute_key: str) -> "TraceAssertion":
        """Get attribute value from span matching filter.

        Args:
            filter (SpanFilter):
                SpanFilter to identify the span.
            attribute_key (str):
                Attribute key to extract.

        Returns:
            TraceAssertion that extracts the attribute value.
            Use with appropriate operators for the value type.
        """

    @staticmethod
    def span_duration(filter: SpanFilter) -> "TraceAssertion":
        """Get duration of span matching filter.

        Args:
            filter (SpanFilter):
                SpanFilter to identify the span.

        Returns:
            TraceAssertion that extracts span duration in milliseconds.
            Use with numeric comparison operators.
        """

    @staticmethod
    def span_aggregation(filter: SpanFilter, attribute_key: str, aggregation: AggregationType) -> "TraceAssertion":
        """Aggregate numeric attribute across filtered spans.

        Args:
            filter (SpanFilter):
                SpanFilter to identify spans.
            attribute_key (str):
                Numeric attribute to aggregate.
            aggregation (AggregationType):
                Defining how to aggregate.

        Returns:
            TraceAssertion that computes the aggregation.
            Use with numeric comparison operators.
        """

    @staticmethod
    def trace_duration() -> "TraceAssertion":
        """Get total duration of the entire trace.

        Returns:
            TraceAssertion that extracts trace duration in milliseconds.
            Use with numeric comparison operators for SLA validation.
        """

    @staticmethod
    def trace_span_count() -> "TraceAssertion":
        """Count total spans in the trace.

        Returns:
            TraceAssertion that extracts total span count.
            Use with numeric operators to validate trace complexity.
        """

    @staticmethod
    def trace_error_count() -> "TraceAssertion":
        """Count spans with error status in the trace.

        Returns:
            TraceAssertion that counts error spans.
            Use with Equals(0) to ensure no errors occurred.
        """

    @staticmethod
    def trace_service_count() -> "TraceAssertion":
        """Count unique services involved in the trace.

        Returns:
            TraceAssertion that counts distinct services.
            Use to validate service boundaries or detect sprawl.
        """

    @staticmethod
    def trace_max_depth() -> "TraceAssertion":
        """Get maximum nesting depth of span tree.

        Returns:
            TraceAssertion that extracts max span depth.
            Use to detect deep recursion or validate call hierarchy.
        """

    @staticmethod
    def trace_attribute(attribute_key: str) -> "TraceAssertion":
        """Get trace-level attribute value.

        Args:
            attribute_key (str):
                Attribute key from trace context.

        Returns:
            TraceAssertion that extracts the trace attribute.
            Use with appropriate operators for the value type.
        """

class TraceAssertionTask:
    """Trace-based evaluation task for behavioral assertions.

    Evaluates trace and span properties to validate execution behavior,
    performance characteristics, and service interactions. Unlike AssertionTask
    which operates on LLM responses, TraceAssertionTask analyzes distributed
    traces to ensure agents and services behave correctly.

    TraceAssertionTask is essential for:
        - Validating agent workflow execution order
        - Ensuring required services are called
        - Enforcing performance SLAs
        - Detecting error patterns
        - Verifying span attributes and metadata
        - Analyzing service dependencies

    Each task combines three components:
        1. TraceAssertion: What to measure (span count, duration, etc.)
        2. ComparisonOperator: How to compare (equals, greater than, etc.)
        3. Expected Value: What value to compare against

    Common Use Cases:
        - Workflow validation: Verify spans execute in correct order
        - Completeness checks: Ensure all required steps were executed
        - Performance monitoring: Enforce latency SLAs
        - Error detection: Validate error-free execution
        - Resource validation: Check correct models/services were used
        - Complexity bounds: Limit retry counts or recursion depth

    Examples:
        Verify agent execution order:

        >>> task = TraceAssertionTask(
        ...     id="verify_agent_workflow",
        ...     assertion=TraceAssertion.span_sequence([
        ...         "call_tool",
        ...         "run_agent",
        ...         "double_check"
        ...     ]),
        ...     operator=ComparisonOperator.SequenceMatches,
        ...     expected_value=True,
        ...     description="Verify correct agent execution order"
        ... )

        Ensure all required steps exist:

        >>> task = TraceAssertionTask(
        ...     id="verify_required_steps",
        ...     assertion=TraceAssertion.span_set([
        ...         "validate_input",
        ...         "process_data",
        ...         "generate_output"
        ...     ]),
        ...     operator=ComparisonOperator.ContainsAll,
        ...     expected_value=True,
        ...     description="Ensure all pipeline steps were executed"
        ... )

        Enforce total trace duration SLA:

        >>> task = TraceAssertionTask(
        ...     id="verify_performance",
        ...     assertion=TraceAssertion.trace_duration(),
        ...     operator=ComparisonOperator.LessThan,
        ...     expected_value=5000.0,  # 5 seconds in milliseconds
        ...     description="Ensure execution completes within 5 seconds"
        ... )

        Limit retry attempts:

        >>> filter = SpanFilter.by_name("retry_operation")
        >>> task = TraceAssertionTask(
        ...     id="verify_retry_limit",
        ...     assertion=TraceAssertion.span_count(filter),
        ...     operator=ComparisonOperator.LessThanOrEqual,
        ...     expected_value=3,
        ...     description="Ensure no more than 3 retries"
        ... )

        Verify correct model was used:

        >>> filter = SpanFilter.by_name("llm.generate")
        >>> task = TraceAssertionTask(
        ...     id="verify_model_used",
        ...     assertion=TraceAssertion.span_attribute(filter, "model"),
        ...     operator=ComparisonOperator.Equals,
        ...     expected_value="gpt-4",
        ...     description="Verify gpt-4 was used"
        ... )

        Ensure error-free execution:

        >>> task = TraceAssertionTask(
        ...     id="no_errors",
        ...     assertion=TraceAssertion.trace_error_count(),
        ...     operator=ComparisonOperator.Equals,
        ...     expected_value=0,
        ...     description="Verify no errors occurred"
        ... )

        Limit total token usage:

        >>> filter = SpanFilter.by_name_pattern("llm.*")
        >>> task = TraceAssertionTask(
        ...     id="token_budget",
        ...     assertion=TraceAssertion.span_aggregation(
        ...         filter,
        ...         "token_count",
        ...         AggregationType.Sum
        ...     ),
        ...     operator=ComparisonOperator.LessThan,
        ...     expected_value=10000,
        ...     description="Ensure total tokens under budget"
        ... )

        With dependencies:

        >>> task = TraceAssertionTask(
        ...     id="verify_database_performance",
        ...     assertion=TraceAssertion.span_duration(
        ...         SpanFilter.by_name("database_query")
        ...     ),
        ...     operator=ComparisonOperator.LessThan,
        ...     expected_value=100,  # 100ms
        ...     depends_on=["verify_agent_workflow"],
        ...     description="Verify database query performance after workflow validation"
        ... )

    Note:
        - Traces must be collected and available before evaluation
        - Span names and attributes depend on instrumentation
        - Duration is measured in milliseconds
        - Use dependencies to chain trace assertions with other tasks
        - Condition tasks can gate subsequent evaluations
    """

    def __init__(
        self,
        id: str,
        assertion: TraceAssertion,
        expected_value: Any,
        operator: ComparisonOperator,
        description: Optional[str] = None,
        depends_on: Optional[List[str]] = None,
        condition: bool = False,
    ):
        """Initialize a trace assertion task for behavioral validation.

        Args:
            id (str):
                Unique identifier for the task. Will be converted to lowercase.
                Used to reference this task in dependencies and results.
            assertion (TraceAssertion):
                TraceAssertion defining what to measure (span count, duration,
                attributes, etc.). Determines the value extracted from the trace.
            expected_value (Any):
                Expected value to compare against. Type depends on the assertion:
                - Numeric for counts, durations, aggregations
                - Boolean for existence checks
                - String/dict for attribute comparisons
                - List for sequence/set operations
            operator (ComparisonOperator):
                ComparisonOperator defining how to compare the extracted value
                against expected_value. Must be appropriate for the assertion type.
            description (Optional[str]):
                Optional human-readable description of what this assertion validates.
                Useful for understanding evaluation results.
            depends_on (Optional[List[str]]):
                Optional list of task IDs that must complete successfully before
                this task executes. Empty list if not provided.
            condition (bool):
                If True, this assertion acts as a condition for subsequent tasks.
                If the assertion fails, dependent tasks will be skipped and this
                task will be excluded from final results.

        Raises:
            TypeError: If expected_value is not JSON-serializable or if operator
                is not a valid ComparisonOperator.
        """

    @property
    def id(self) -> str:
        """Unique task identifier (lowercase)."""

    @id.setter
    def id(self, id: str) -> None:
        """Set task identifier (will be converted to lowercase)."""

    @property
    def assertion(self) -> TraceAssertion:
        """TraceAssertion defining what to measure in the trace."""

    @assertion.setter
    def assertion(self, assertion: TraceAssertion) -> None:
        """Set trace assertion target.

        Args:
            assertion (TraceAssertion):
                TraceAssertion defining what to measure.
        """

    @property
    def operator(self) -> ComparisonOperator:
        """Comparison operator for the assertion."""

    @operator.setter
    def operator(self, operator: ComparisonOperator) -> None:
        """Set comparison operator.

        Args:
            operator (ComparisonOperator):
                ComparisonOperator defining how to compare values.
        """

    @property
    def expected_value(self) -> Any:
        """Expected value for comparison.

        Returns:
            The expected value as a Python object (deserialized from internal
            JSON representation).
        """

    @property
    def description(self) -> Optional[str]:
        """Human-readable description of the assertion."""

    @description.setter
    def description(self, description: Optional[str]) -> None:
        """Set assertion description.

        Args:
            description (Optional[str]):
                Human-readable description of the assertion.
        """

    @property
    def depends_on(self) -> List[str]:
        """List of task IDs this task depends on."""

    @depends_on.setter
    def depends_on(self, depends_on: List[str]) -> None:
        """Set task dependencies.

        Args:
            depends_on (List[str]):
                List of task IDs that must complete before this task.
        """

    @property
    def condition(self) -> bool:
        """Indicates if this task is a condition for subsequent tasks."""

    @condition.setter
    def condition(self, condition: bool) -> None:
        """Set whether this task is a condition for subsequent tasks."""

    def __str__(self) -> str:
        """Return string representation of the trace assertion task."""

class AssertionResult:
    @property
    def passed(self) -> bool: ...
    @property
    def actual(self) -> Any: ...
    @property
    def expected(self) -> Any: ...
    @property
    def message(self) -> str: ...
    def __str__(self): ...

class AssertionResults:
    @property
    def results(self) -> Dict[str, AssertionResult]: ...
    def __str__(self): ...
    def __getitem__(self, key: str) -> AssertionResult: ...

def execute_trace_assertion_tasks(tasks: List[TraceAssertionTask], spans: List[TraceSpan]) -> AssertionResults:
    """Execute trace assertion tasks against provided spans.

    Args:
        tasks (List[TraceAssertionTask]):
            List of TraceAssertionTask to evaluate.
        spans (List[TraceSpan]):
            List of TraceSpan representing the collected trace data.

    Returns:
        AssertionResults containing results for each trace assertion task.

    Raises:
        ValueError: If tasks list is empty or spans are not provided.
    """

### mock.pyi ###
class ScouterTestServer:
    def __init__(
        self,
        cleanup: bool = True,
        rabbit_mq: bool = False,
        kafka: bool = False,
        openai: bool = False,
        base_path: Optional[Path] = None,
    ) -> None:
        """Instantiates the test server.

        When the test server is used as a context manager, it will start the server
        in a background thread and set the appropriate env vars so that the client
        can connect to the server. The server will be stopped when the context manager
        exits and the env vars will be reset.

        Args:
            cleanup (bool, optional):
                Whether to cleanup the server after the test. Defaults to True.
            rabbit_mq (bool, optional):
                Whether to use RabbitMQ as the transport. Defaults to False.
            kafka (bool, optional):
                Whether to use Kafka as the transport. Defaults to False.
            openai (bool, optional):
                Whether to create a mock OpenAITest server. Defaults to False.
            base_path (Optional[Path], optional):
                The base path for the server. Defaults to None. This is primarily
                used for testing loading attributes from a pyproject.toml file.
        """

    def start_server(self) -> None:
        """Starts the test server."""

    def stop_server(self) -> None:
        """Stops the test server."""

    def __enter__(self) -> "ScouterTestServer":
        """Starts the test server."""

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """Stops the test server."""

    def set_env_vars_for_client(self) -> None:
        """Sets the env vars for the client to connect to the server."""

    def remove_env_vars_for_client(self) -> None:
        """Removes the env vars for the client to connect to the server."""

    @staticmethod
    def cleanup() -> None:
        """Cleans up the test server."""

class MockConfig:
    def __init__(self, **kwargs) -> None:
        """Mock configuration for the ScouterQueue

        Args:
            **kwargs: Arbitrary keyword arguments to set as attributes.
        """

def create_simple_trace() -> List["TraceSpan"]:
    """Creates a simple trace with a few spans.

    Returns:
        List[TraceSpan]: A list of TraceSpan objects representing the trace.
    """

def create_nested_trace() -> List["TraceSpan"]:
    """Creates a nested trace with parent-child relationships.

    Returns:
        List[TraceSpan]: A list of TraceSpan objects representing the trace.
    """

def create_trace_with_attributes() -> List["TraceSpan"]:
    """Creates a trace with spans that have attributes.

    Returns:
        List[TraceSpan]: A list of TraceSpan objects representing the trace.
    """

def create_multi_service_trace() -> List["TraceSpan"]:
    """Creates a trace that spans multiple services.

    Returns:
        List[TraceSpan]: A list of TraceSpan objects representing the trace.
    """

def create_sequence_pattern_trace() -> List["TraceSpan"]:
    """Creates a trace with a sequence pattern of spans.

    Returns:
        List[TraceSpan]: A list of TraceSpan objects representing the trace.
    """

def create_trace_with_errors() -> List["TraceSpan"]:
    """Creates a trace with spans that contain errors.

    Returns:
        List[TraceSpan]: A list of TraceSpan objects representing the trace.
    """

### scouter.pyi ###
#################
# _scouter.types
#################

class DriftType:
    Spc: "DriftType"
    Psi: "DriftType"
    Custom: "DriftType"
    GenAI: "DriftType"

    def value(self) -> str: ...
    @staticmethod
    def from_value(value: str) -> "DriftType": ...

class CommonCrons:
    Every1Minute: "CommonCrons"
    Every5Minutes: "CommonCrons"
    Every15Minutes: "CommonCrons"
    Every30Minutes: "CommonCrons"
    EveryHour: "CommonCrons"
    Every6Hours: "CommonCrons"
    Every12Hours: "CommonCrons"
    EveryDay: "CommonCrons"
    EveryWeek: "CommonCrons"

    @property
    def cron(self) -> str:
        """Return the cron"""

    def get_next(self) -> str:
        """Return the next cron time"""

class ScouterDataType:
    Pandas: "ScouterDataType"
    Polars: "ScouterDataType"
    Numpy: "ScouterDataType"
    Arrow: "ScouterDataType"
    LLM: "ScouterDataType"

class CompressionType:
    NA: "CompressionType"
    Gzip: "CompressionType"
    Snappy: "CompressionType"
    Lz4: "CompressionType"
    Zstd: "CompressionType"

class ConsoleDispatchConfig:
    def __init__(self):
        """Initialize alert config"""

    @property
    def enabled(self) -> bool:
        """Return the alert dispatch type"""

class SlackDispatchConfig:
    def __init__(self, channel: str):
        """Initialize alert config

        Args:
            channel:
                Slack channel name for where alerts will be reported
        """

    @property
    def channel(self) -> str:
        """Return the slack channel name"""

    @channel.setter
    def channel(self, channel: str) -> None:
        """Set the slack channel name for where alerts will be reported"""

class OpsGenieDispatchConfig:
    def __init__(self, team: str):
        """Initialize alert config

        Args:
            team:
                Opsegenie team to be notified in the event of drift
        """

    @property
    def team(self) -> str:
        """Return the opesgenie team name"""

    @team.setter
    def team(self, team: str) -> None:
        """Set the opesgenie team name"""

class AlertDispatchType:
    Slack: "AlertDispatchType"
    OpsGenie: "AlertDispatchType"
    Console: "AlertDispatchType"

    @staticmethod
    def to_string() -> str:
        """Return the string representation of the alert dispatch type"""

DispatchConfigType = ConsoleDispatchConfig | SlackDispatchConfig | OpsGenieDispatchConfig

class AlertZone:
    Zone1: "AlertZone"
    Zone2: "AlertZone"
    Zone3: "AlertZone"
    Zone4: "AlertZone"
    NotApplicable: "AlertZone"

class SpcAlertType:
    OutOfBounds = "SpcAlertType"
    Consecutive = "SpcAlertType"
    Alternating = "SpcAlertType"
    AllGood = "SpcAlertType"
    Trend = "SpcAlertType"

class SpcAlertRule:
    def __init__(
        self,
        rule: str = "8 16 4 8 2 4 1 1",
        zones_to_monitor: List[AlertZone] = [
            AlertZone.Zone1,
            AlertZone.Zone2,
            AlertZone.Zone3,
            AlertZone.Zone4,
        ],
    ) -> None:
        """Initialize alert rule

        Args:
            rule:
                Rule to use for alerting. Eight digit integer string.
                Defaults to '8 16 4 8 2 4 1 1'
            zones_to_monitor:
                List of zones to monitor. Defaults to all zones.
        """

    @property
    def rule(self) -> str:
        """Return the alert rule"""

    @rule.setter
    def rule(self, rule: str) -> None:
        """Set the alert rule"""

    @property
    def zones_to_monitor(self) -> List[AlertZone]:
        """Return the zones to monitor"""

    @zones_to_monitor.setter
    def zones_to_monitor(self, zones_to_monitor: List[AlertZone]) -> None:
        """Set the zones to monitor"""

class PsiNormalThreshold:
    def __init__(self, alpha: float = 0.05):
        """Initialize PSI threshold using normal approximation.

        Uses the asymptotic normal distribution of PSI to calculate critical values
        for population drift detection.

        Args:
            alpha: Significance level (0.0 to 1.0, exclusive). Common values:
                   0.05 (95% confidence), 0.01 (99% confidence)

        Raises:
            ValueError: If alpha not in range (0.0, 1.0)
        """

    @property
    def alpha(self) -> float:
        """Statistical significance level for drift detection."""

    @alpha.setter
    def alpha(self, alpha: float) -> None:
        """Set significance level (must be between 0.0 and 1.0, exclusive)."""

class PsiChiSquareThreshold:
    def __init__(self, alpha: float = 0.05):
        """Initialize PSI threshold using chi-square approximation.

        Uses the asymptotic chi-square distribution of PSI.

        The chi-square method is generally more statistically rigorous than
        normal approximation, especially for smaller sample sizes.

        Args:
            alpha: Significance level (0.0 to 1.0, exclusive). Common values:
                   0.05 (95% confidence), 0.01 (99% confidence)

        Raises:
            ValueError: If alpha not in range (0.0, 1.0)
        """

    @property
    def alpha(self) -> float:
        """Statistical significance level for drift detection."""

    @alpha.setter
    def alpha(self, alpha: float) -> None:
        """Set significance level (must be between 0.0 and 1.0, exclusive)."""

class PsiFixedThreshold:
    def __init__(self, threshold: float = 0.25):
        """Initialize PSI threshold using a fixed value.

        Uses a predetermined PSI threshold value, similar to traditional
        "rule of thumb" approaches (e.g., 0.10 for moderate drift, 0.25
        for significant drift).

        Args:
            threshold: Fixed PSI threshold value (must be positive).
                      Common industry values: 0.10, 0.25

        Raises:
            ValueError: If threshold is not positive
        """

    @property
    def threshold(self) -> float:
        """Fixed PSI threshold value for drift detection."""

    @threshold.setter
    def threshold(self, threshold: float) -> None:
        """Set threshold value (must be positive)."""

PsiThresholdType = PsiNormalThreshold | PsiChiSquareThreshold | PsiFixedThreshold

class PsiAlertConfig:
    def __init__(
        self,
        dispatch_config: Optional[SlackDispatchConfig | OpsGenieDispatchConfig] = None,
        schedule: Optional[str | CommonCrons] = None,
        features_to_monitor: List[str] = [],
        threshold: Optional[PsiThresholdType] = PsiChiSquareThreshold(),
    ):
        """Initialize alert config

        Args:
            dispatch_config:
                Alert dispatch configuration to use. Defaults to an internal "Console" type where
                the alerts will be logged to the console
            schedule:
                Schedule to run monitor. Defaults to daily at midnight
            features_to_monitor:
                List of features to monitor. Defaults to empty list, which means all features
            threshold:
                Configuration that helps determine how to calculate PSI critical values.
                Defaults to PsiChiSquareThreshold, which uses the chi-square distribution.
        """

    @property
    def dispatch_type(self) -> AlertDispatchType:
        """Return the alert dispatch type"""

    @property
    def dispatch_config(self) -> DispatchConfigType:
        """Return the dispatch config"""

    @property
    def threshold(self) -> PsiThresholdType:
        """Return the threshold config"""

    @property
    def schedule(self) -> str:
        """Return the schedule"""

    @schedule.setter
    def schedule(self, schedule: str) -> None:
        """Set the schedule"""

    @property
    def features_to_monitor(self) -> List[str]:
        """Return the features to monitor"""

    @features_to_monitor.setter
    def features_to_monitor(self, features_to_monitor: List[str]) -> None:
        """Set the features to monitor"""

class SpcAlertConfig:
    def __init__(
        self,
        rule: Optional[SpcAlertRule] = None,
        dispatch_config: Optional[SlackDispatchConfig | OpsGenieDispatchConfig] = None,
        schedule: Optional[str | CommonCrons] = None,
        features_to_monitor: List[str] = [],
    ):
        """Initialize alert config

        Args:
            rule:
                Alert rule to use. Defaults to Standard
            dispatch_config:
                Alert dispatch config. Defaults to console
            schedule:
                Schedule to run monitor. Defaults to daily at midnight
            features_to_monitor:
                List of features to monitor. Defaults to empty list, which means all features

        """

    @property
    def dispatch_type(self) -> AlertDispatchType:
        """Return the alert dispatch type"""

    @property
    def dispatch_config(self) -> DispatchConfigType:
        """Return the dispatch config"""

    @property
    def rule(self) -> SpcAlertRule:
        """Return the alert rule"""

    @rule.setter
    def rule(self, rule: SpcAlertRule) -> None:
        """Set the alert rule"""

    @property
    def schedule(self) -> str:
        """Return the schedule"""

    @schedule.setter
    def schedule(self, schedule: str) -> None:
        """Set the schedule"""

    @property
    def features_to_monitor(self) -> List[str]:
        """Return the features to monitor"""

    @features_to_monitor.setter
    def features_to_monitor(self, features_to_monitor: List[str]) -> None:
        """Set the features to monitor"""

class SpcAlert:
    def __init__(self, kind: SpcAlertType, zone: AlertZone):
        """Initialize alert"""

    @property
    def kind(self) -> SpcAlertType:
        """Alert kind"""

    @property
    def zone(self) -> AlertZone:
        """Zone associated with alert"""

    def __str__(self) -> str:
        """Return the string representation of the alert."""

class AlertThreshold:
    """
    Enum representing different alert conditions for monitoring metrics.

    Attributes:
        Below: Indicates that an alert should be triggered when the metric is below a threshold.
        Above: Indicates that an alert should be triggered when the metric is above a threshold.
        Outside: Indicates that an alert should be triggered when the metric is outside a specified range.
    """

    Below: "AlertThreshold"
    Above: "AlertThreshold"
    Outside: "AlertThreshold"

    @staticmethod
    def from_value(value: str) -> "AlertThreshold":
        """
        Creates an AlertThreshold enum member from a string value.

        Args:
            value (str): The string representation of the alert condition.

        Returns:
            AlertThreshold: The corresponding AlertThreshold enum member.
        """

class AlertCondition:
    def __init__(
        self,
        baseline_value: float,
        alert_threshold: AlertThreshold,
        delta: Optional[float],
    ):
        """Initialize a AlertCondition instance.
        Args:
            baseline_value (float):
                The baseline value to compare against for alerting.
            alert_threshold (AlertThreshold):
                The condition that determines when an alert should be triggered.
                Must be one of the AlertThreshold enum members like Below, Above, or Outside.
            delta (Optional[float], optional):
                Optional delta value that modifies the baseline to create the alert boundary.
                The interpretation depends on alert_threshold:
                - Above: alert if value > (baseline + delta)
                - Below: alert if value < (baseline - delta)
                - Outside: alert if value is outside [baseline - delta, baseline + delta]
        Example:
            alert_threshold = AlertCondition(AlertCondition.BELOW, 2.0)
        """

    def upper_bound(self) -> float:
        """Calculate and return the upper bound for alerting based on baseline and delta."""

    def lower_bound(self) -> float:
        """Calculate and return the lower bound for alerting based on baseline and delta."""

    def should_alert(self, value: float) -> bool:
        """Determine if an alert should be triggered based on the provided value."""

class CustomMetricAlertConfig:
    def __init__(
        self,
        dispatch_config: Optional[SlackDispatchConfig | OpsGenieDispatchConfig] = None,
        schedule: Optional[str | CommonCrons] = None,
    ):
        """Initialize alert config

        Args:
            dispatch_config:
                Alert dispatch config. Defaults to console
            schedule:
                Schedule to run monitor. Defaults to daily at midnight

        """

    @property
    def dispatch_type(self) -> AlertDispatchType:
        """Return the alert dispatch type"""

    @property
    def dispatch_config(self) -> DispatchConfigType:
        """Return the dispatch config"""

    @property
    def schedule(self) -> str:
        """Return the schedule"""

    @schedule.setter
    def schedule(self, schedule: str) -> None:
        """Set the schedule"""

    @property
    def alert_conditions(self) -> dict[str, AlertCondition]:
        """Return the alert_condition that were set during metric definition"""

    @alert_conditions.setter
    def alert_conditions(self, alert_conditions: dict[str, AlertCondition]) -> None:
        """Update the alert_condition that were set during metric definition"""

class GenAIAlertConfig:
    def __init__(
        self,
        dispatch_config: Optional[SlackDispatchConfig | OpsGenieDispatchConfig] = None,
        schedule: Optional[str | CommonCrons] = None,
        alert_condition: Optional[AlertCondition] = None,
    ):
        """Initialize alert config

        Args:
            dispatch_config:
                Alert dispatch config. Defaults to console
            schedule:
                Schedule to run monitor. Defaults to daily at midnight
            alert_condition:
                Alert condition for a GenAI drift profile

        """

    @property
    def dispatch_type(self) -> AlertDispatchType:
        """Return the alert dispatch type"""

    @property
    def dispatch_config(self) -> DispatchConfigType:
        """Return the dispatch config"""

    @property
    def schedule(self) -> str:
        """Return the schedule"""

    @schedule.setter
    def schedule(self, schedule: str) -> None:
        """Set the schedule"""

    @property
    def alert_conditions(self) -> Optional[AlertCondition]:
        """Return the alert condition"""

class TransportType:
    Kafka = "TransportType"
    RabbitMQ = "TransportType"
    Redis = "TransportType"
    HTTP = "TransportType"
    Grpc = "TransportType"

class HttpConfig:
    server_uri: str
    username: str
    password: str
    auth_token: str

    def __init__(
        self,
        server_uri: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        auth_token: Optional[str] = None,
    ) -> None:
        """HTTP configuration to use with the HTTPProducer.

        Args:
            server_uri:
                URL of the HTTP server to publish messages to.
                If not provided, the value of the HTTP_server_uri environment variable is used.

            username:
                Username for basic authentication.

            password:
                Password for basic authentication.

            auth_token:
                Authorization token to use for authentication.

        """

    def __str__(self): ...

class GrpcConfig:
    server_uri: str
    username: str
    password: str

    def __init__(
        self,
        server_uri: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ) -> None:
        """gRPC configuration to use with the GrpcProducer.

        Args:
            server_uri:
                URL of the gRPC server to publish messages to.
                If not provided, the value of the SCOUTER_GRPC_URI environment variable is used.

            username:
                Username for basic authentication.
                If not provided, the value of the SCOUTER_USERNAME environment variable is used.

            password:
                Password for basic authentication.
                If not provided, the value of the SCOUTER_PASSWORD environment variable is used.
        """

    def __str__(self): ...

class KafkaConfig:
    brokers: str
    topic: str
    compression_type: str
    message_timeout_ms: int
    message_max_bytes: int
    log_level: LogLevel
    config: Dict[str, str]
    max_retries: int
    transport_type: TransportType

    def __init__(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        brokers: Optional[str] = None,
        topic: Optional[str] = None,
        compression_type: Optional[str] = None,
        message_timeout_ms: int = 600_000,
        message_max_bytes: int = 2097164,
        log_level: LogLevel = LogLevel.Info,
        config: Dict[str, str] = {},
        max_retries: int = 3,
    ) -> None:
        """Kafka configuration for connecting to and publishing messages to Kafka brokers.

        This configuration supports both authenticated (SASL) and unauthenticated connections.
        When credentials are provided, SASL authentication is automatically enabled with
        secure defaults.

        Authentication Priority (first match wins):
            1. Direct parameters (username/password)
            2. Environment variables (KAFKA_USERNAME/KAFKA_PASSWORD)
            3. Configuration dictionary (sasl.username/sasl.password)

        SASL Security Defaults:
            - security.protocol: "SASL_SSL" (override via KAFKA_SECURITY_PROTOCOL env var)
            - sasl.mechanism: "PLAIN" (override via KAFKA_SASL_MECHANISM env var)

        Args:
            username:
                SASL username for authentication.
                Fallback: KAFKA_USERNAME environment variable.
            password:
                SASL password for authentication.
                Fallback: KAFKA_PASSWORD environment variable.
            brokers:
                Comma-separated list of Kafka broker addresses (host:port).
                Fallback: KAFKA_BROKERS environment variable.
                Default: "localhost:9092"
            topic:
                Target Kafka topic for message publishing.
                Fallback: KAFKA_TOPIC environment variable.
                Default: "scouter_monitoring"
            compression_type:
                Message compression algorithm.
                Options: "none", "gzip", "snappy", "lz4", "zstd"
                Default: "gzip"
            message_timeout_ms:
                Maximum time to wait for message delivery (milliseconds).
                Default: 600000 (10 minutes)
            message_max_bytes:
                Maximum message size in bytes.
                Default: 2097164 (~2MB)
            log_level:
                Logging verbosity for the Kafka producer.
                Default: LogLevel.Info
            config:
                Additional Kafka producer configuration parameters.
                See: https://kafka.apache.org/documentation/#producerconfigs
                Note: Direct parameters take precedence over config dictionary values.
            max_retries:
                Maximum number of retry attempts for failed message deliveries.
                Default: 3

        Examples:
            Basic usage (unauthenticated):
            ```python
            config = KafkaConfig(
                brokers="kafka1:9092,kafka2:9092",
                topic="my_topic"
            )
            ```

            SASL authentication:
            ```python
            config = KafkaConfig(
                username="my_user",
                password="my_password",
                brokers="secure-kafka:9093",
                topic="secure_topic"
            )
            ```

            Advanced configuration:
            ```python
            config = KafkaConfig(
                brokers="kafka:9092",
                compression_type="lz4",
                config={
                    "acks": "all",
                    "batch.size": "32768",
                    "linger.ms": "10"
                }
            )
            ```
        """

    def __str__(self): ...

class RabbitMQConfig:
    address: str
    queue: str
    max_retries: int
    transport_type: TransportType

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        queue: Optional[str] = None,
        max_retries: int = 3,
    ) -> None:
        """RabbitMQ configuration to use with the RabbitMQProducer.

        Args:
            host:
                RabbitMQ host.
                If not provided, the value of the RABBITMQ_HOST environment variable is used.

            port:
                RabbitMQ port.
                If not provided, the value of the RABBITMQ_PORT environment variable is used.

            username:
                RabbitMQ username.
                If not provided, the value of the RABBITMQ_USERNAME environment variable is used.

            password:
                RabbitMQ password.
                If not provided, the value of the RABBITMQ_PASSWORD environment variable is used.

            queue:
                RabbitMQ queue to publish messages to.
                If not provided, the value of the RABBITMQ_QUEUE environment variable is used.

            max_retries:
                Maximum number of retries to attempt when publishing messages.
                Default is 3.
        """

    def __str__(self): ...

class RedisConfig:
    address: str
    channel: str
    transport_type: TransportType

    def __init__(
        self,
        address: Optional[str] = None,
        chanel: Optional[str] = None,
    ) -> None:
        """Redis configuration to use with a Redis producer

        Args:
            address (str):
                Redis address.
                If not provided, the value of the REDIS_ADDR environment variable is used and defaults to
                "redis://localhost:6379".

            channel (str):
                Redis channel to publish messages to.

                If not provided, the value of the REDIS_CHANNEL environment variable is used and defaults to "scouter_monitoring".
        """

    def __str__(self): ...

class TracePaginationResponse:
    """Response structure for paginated trace list requests."""

    items: List[TraceListItem]

class TraceSpansResponse:
    """Response structure containing a list of spans for a trace."""

    spans: List[TraceSpan]

    def get_span_by_name(self, span_name: str) -> Optional[TraceSpan]:
        """Retrieve a span by its name."""

class TraceBaggageResponse:
    """Response structure containing trace baggage records."""

    baggage: List[TraceBaggageRecord]

class TraceMetricsRequest:
    """Request payload for fetching trace metrics."""

    space: Optional[str]
    name: Optional[str]
    version: Optional[str]
    start_time: datetime.datetime
    end_time: datetime.datetime
    bucket_interval: str

    def __init__(
        self,
        start_time: datetime.datetime,
        end_time: datetime.datetime,
        bucket_interval: str,
        space: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
    ) -> None:
        """Initialize trace metrics request.

        Args:
            start_time:
                Start time boundary (UTC)
            end_time:
                End time boundary (UTC)
            bucket_interval:
                The time interval for metric aggregation buckets (e.g., '1 minutes', '30 minutes')
            space:
                Model space filter
            name:
                Model name filter
            version:
                Model version filter
        """

class TraceMetricsResponse:
    """Response structure containing aggregated trace metrics."""

    metrics: List[TraceMetricBucket]

class TagsResponse:
    """Response structure containing a list of tag records."""

    tags: List[TagRecord]

class TimeInterval:
    FifteenMinutes: "TimeInterval"
    ThirtyMinutes: "TimeInterval"
    OneHour: "TimeInterval"
    FourHours: "TimeInterval"
    SixHours: "TimeInterval"
    TwelveHours: "TimeInterval"
    TwentyFourHours: "TimeInterval"
    SevenDays: "TimeInterval"
    Custom: "TimeInterval"

class DriftRequest:
    def __init__(
        self,
        uid: str,
        space: str,
        time_interval: TimeInterval,
        max_data_points: int,
        start_datetime: Optional[datetime.datetime] = None,
        end_datetime: Optional[datetime.datetime] = None,
    ) -> None:
        """Initialize drift request

        Args:
            uid:
                Unique identifier tied to drift profile
            space:
                Space associated with drift profile
            time_interval:
                Time window for drift request
            max_data_points:
                Maximum data points to return
            start_datetime:
                Optional start datetime for drift request
            end_datetime:
                Optional end datetime for drift request
        """

class ProfileStatusRequest:
    def __init__(self, name: str, space: str, version: str, drift_type: DriftType, active: bool) -> None:
        """Initialize profile status request

        Args:
            name:
                Model name
            space:
                Model space
            version:
                Model version
            drift_type:
                Profile drift type. A (repo/name/version can be associated with more than one drift type)
            active:
                Whether to set the profile as active or inactive
        """

class GetProfileRequest:
    def __init__(self, name: str, space: str, version: str, drift_type: DriftType) -> None:
        """Initialize get profile request

        Args:
            name:
                Profile name
            space:
                Profile space
            version:
                Profile version
            drift_type:
                Profile drift type. A (repo/name/version can be associated with more than one drift type)
        """

class Alert:
    created_at: datetime.datetime
    entity_name: str
    alert: Dict[str, str]
    id: int
    active: bool

class DriftAlertPaginationRequest:
    def __init__(
        self,
        uid: str,
        active: bool = False,
        limit: Optional[int] = None,
        cursor_created_at: Optional[datetime.datetime] = None,
        cursor_id: Optional[int] = None,
        direction: Optional[Literal["next", "previous"]] = "previous",
        start_datetime: Optional[datetime.datetime] = None,
        end_datetime: Optional[datetime.datetime] = None,
    ) -> None:
        """Initialize drift alert request. Used for paginated alert retrieval.

        Args:
            uid:
                Unique identifier tied to drift profile
            active:
                Whether to get active alerts only
            limit:
                Limit for number of alerts to return
            cursor_created_at:
                Pagination cursor: created at timestamp
            cursor_id:
                Pagination cursor: alert ID
            direction:
                Pagination direction: "next" or "previous"
            start_datetime:
                Optional start datetime for alert filtering
            end_datetime:
                Optional end datetime for alert filtering
        """

class AlertCursor:
    created_at: datetime.datetime
    id: int

class DriftAlertPaginationResponse:
    items: List[Alert]
    has_next: bool
    next_cursor: Optional[AlertCursor]
    has_previous: bool
    previous_cursor: Optional[AlertCursor]

# Client
class ScouterClient:
    """Helper client for interacting with Scouter Server"""

    def __init__(self, config: Optional[HttpConfig] = None) -> None:
        """Initialize ScouterClient

        Args:
            config:
                HTTP configuration for interacting with the server.
        """

    def get_binned_drift(
        self,
        drift_request: DriftRequest,
        drift_type: DriftType,
    ) -> Any:
        """Get drift map from server

        Args:
            drift_request:
                DriftRequest object
            drift_type:
                Drift type for request

        Returns:
            Drift map of type BinnedMetrics | BinnedPsiFeatureMetrics | BinnedSpcFeatureMetrics
        """

    def get_genai_task_binned_drift(self, drift_request: DriftRequest) -> Any:
        """Get GenAI task drift map from server
        Args:
            drift_request:
                DriftRequest object
        """

    def register_profile(self, profile: Any, set_active: bool = False, deactivate_others: bool = False) -> bool:
        """Registers a drift profile with the server

        Args:
            profile:
                Drift profile
            set_active:
                Whether to set the profile as active or inactive
            deactivate_others:
                Whether to deactivate other profiles

        Returns:
            boolean
        """

    def update_profile_status(self, request: ProfileStatusRequest) -> bool:
        """Update profile status

        Args:
            request:
                ProfileStatusRequest

        Returns:
            boolean
        """

    def get_alerts(self, request: DriftAlertPaginationRequest) -> DriftAlertPaginationResponse:
        """Get alerts

        Args:
            request:
                DriftAlertPaginationRequest

        Returns:
            DriftAlertPaginationResponse
        """

    def download_profile(self, request: GetProfileRequest, path: Optional[Path]) -> str:
        """Download profile

        Args:
            request:
                GetProfileRequest
            path:
                Path to save profile

        Returns:
            Path to downloaded profile
        """

    def get_paginated_traces(self, filters: TraceFilters) -> TracePaginationResponse:
        """Get paginated traces
        Args:
            filters:
                TraceFilters object
        Returns:
            TracePaginationResponse
        """

    def get_trace_spans(
        self,
        trace_id: str,
        service_name: Optional[str] = None,
    ) -> TraceSpansResponse:
        """Get trace spans

        Args:
            trace_id:
                Trace ID
            service_name:
                Service name

        Returns:
            TraceSpansResponse
        """

    def get_trace_spans_from_tags(
        self,
        tags: List[Tuple[str, str]],
        match_all: bool = False,
        service_name: Optional[str] = None,
    ) -> TraceSpansResponse:
        """Get trace spans from tags
        Args:
            tags:
                List of tags to filter by
            match_all:
                Whether to match all tags or any tag
            service_name:
                Service name

        Returns:
            TraceSpansResponse
        """

    def get_trace_baggage(self, trace_id: str) -> TraceBaggageResponse:
        """Get trace baggage

        Args:
            trace_id:
                Trace ID

        Returns:
            TraceBaggageResponse
        """

    def get_trace_metrics(self, request: TraceMetricsRequest) -> TraceMetricsResponse:
        """Get trace metrics

        Args:
            request:
                TraceMetricsRequest

        Returns:
            TraceMetricsResponse
        """

    def get_tags(self, entity_type: str, entity_id: str) -> TagsResponse:
        """Get tags for an entity

        Args:
            entity_type:
                Entity type
            entity_id:
                Entity ID

        Returns:
            TagsResponse
        """

class BinnedMetricStats:
    avg: float
    lower_bound: float
    upper_bound: float

    def __str__(self) -> str: ...

class BinnedMetric:
    metric: str
    created_at: List[datetime.datetime]
    stats: List[BinnedMetricStats]

    def __str__(self) -> str: ...

class BinnedMetrics:
    @property
    def metrics(self) -> Dict[str, BinnedMetric]: ...
    def __str__(self) -> str: ...
    def __getitem__(self, key: str) -> Optional[BinnedMetric]: ...

class BinnedPsiMetric:
    created_at: List[datetime.datetime]
    psi: List[float]
    overall_psi: float
    bins: Dict[int, float]

    def __str__(self) -> str: ...

class BinnedPsiFeatureMetrics:
    features: Dict[str, BinnedMetric]

    def __str__(self) -> str: ...

class SpcDriftFeature:
    created_at: List[datetime.datetime]
    values: List[float]

    def __str__(self) -> str: ...

class BinnedSpcFeatureMetrics:
    features: Dict[str, SpcDriftFeature]

    def __str__(self) -> str: ...

class EntityType:
    Feature: "EntityType"
    Metric: "EntityType"
    GenAI: "EntityType"

class RecordType:
    Spc: "RecordType"
    Psi: "RecordType"
    Observability: "RecordType"
    Custom: "RecordType"
    Trace: "RecordType"
    GenAIEval: "RecordType"
    GenAITask: "RecordType"
    GenAIWorkflow: "RecordType"

class ServerRecord:
    def __init__(self, record: Any) -> None:
        """Initialize server record

        Args:
            record:
                Server record to initialize
        """

    @property
    def record(
        self,
    ) -> Union[SpcRecord, PsiRecord, CustomMetricRecord, ObservabilityMetrics]:
        """Return the drift server record."""

class ServerRecords:
    def __init__(self, records: List[ServerRecord]) -> None:
        """Initialize server records

        Args:
            records:
                List of server records
        """

    @property
    def records(self) -> List[ServerRecord]:
        """Return the drift server records."""

    def model_dump_json(self) -> str:
        """Return the json representation of the record."""

    def __str__(self) -> str:
        """Return the string representation of the record."""

class SpcRecord:
    def __init__(
        self,
        uid: str,
        feature: str,
        value: float,
    ):
        """Initialize spc drift server record

        Args:
            uid:
                Unique identifier for the spc record.
                Must correspond to an existing entity in Scouter.
            feature:
                Feature name
            value:
                Feature value
        """

    @property
    def created_at(self) -> datetime.datetime:
        """Return the created at timestamp."""

    @property
    def uid(self) -> str:
        """Return the unique identifier."""

    @property
    def feature(self) -> str:
        """Return the feature."""

    @property
    def value(self) -> float:
        """Return the sample value."""

    def __str__(self) -> str:
        """Return the string representation of the record."""

    def model_dump_json(self) -> str:
        """Return the json representation of the record."""

    def to_dict(self) -> Dict[str, str]:
        """Return the dictionary representation of the record."""

class PsiRecord:
    def __init__(
        self,
        uid: str,
        feature: str,
        bin_id: int,
        bin_count: int,
    ):
        """Initialize spc drift server record

        Args:
            uid:
                Unique identifier for the psi record.
                Must correspond to an existing entity in Scouter.
            feature:
                Feature name
            bin_id:
                Bundle ID
            bin_count:
                Bundle ID
        """

    @property
    def created_at(self) -> datetime.datetime:
        """Return the created at timestamp."""

    @property
    def uid(self) -> str:
        """Returns the unique identifier."""

    @property
    def feature(self) -> str:
        """Return the feature."""

    @property
    def bin_id(self) -> int:
        """Return the bin id."""

    @property
    def bin_count(self) -> int:
        """Return the sample value."""

    def __str__(self) -> str:
        """Return the string representation of the record."""

    def model_dump_json(self) -> str:
        """Return the json representation of the record."""

    def to_dict(self) -> Dict[str, str]:
        """Return the dictionary representation of the record."""

class CustomMetricRecord:
    def __init__(
        self,
        uid: str,
        metric: str,
        value: float,
    ):
        """Initialize spc drift server record

        Args:
            uid:
                Unique identifier for the metric record.
                Must correspond to an existing entity in Scouter.
            metric:
                Metric name
            value:
                Metric value
        """

    @property
    def created_at(self) -> datetime.datetime:
        """Return the created at timestamp."""

    @property
    def uid(self) -> str:
        """Returns the unique identifier."""

    @property
    def metric(self) -> str:
        """Return the metric name."""

    @property
    def value(self) -> float:
        """Return the metric value."""

    def __str__(self) -> str:
        """Return the string representation of the record."""

    def model_dump_json(self) -> str:
        """Return the json representation of the record."""

    def to_dict(self) -> Dict[str, str]:
        """Return the dictionary representation of the record."""

class QueueFeature:
    def __init__(self, name: str, value: Any) -> None:
        """Initialize feature. Will attempt to convert the value to it's corresponding feature type.
        Current support types are int, float, string.

        Args:
            name:
                Name of the feature
            value:
                Value of the feature. Can be an int, float, or string.

        Example:
            ```python
            feature = Feature("feature_1", 1) # int feature
            feature = Feature("feature_2", 2.0) # float feature
            feature = Feature("feature_3", "value") # string feature
            ```
        """

    @staticmethod
    def int(name: str, value: int) -> "QueueFeature":
        """Create an integer feature

        Args:
            name:
                Name of the feature
            value:
                Value of the feature
        """

    @staticmethod
    def float(name: str, value: float) -> "QueueFeature":
        """Create a float feature

        Args:
            name:
                Name of the feature
            value:
                Value of the feature
        """

    @staticmethod
    def string(name: str, value: str) -> "QueueFeature":
        """Create a string feature

        Args:
            name:
                Name of the feature
            value:
                Value of the feature
        """

    @staticmethod
    def categorical(name: str, value: str) -> "QueueFeature":
        """Create a categorical feature

        Args:
            name:
                Name of the feature
            value:
                Value of the feature
        """

class Features:
    def __init__(
        self,
        features: List[QueueFeature] | Dict[str, Union[int, float, str]],
    ) -> None:
        """Initialize a features class

        Args:
            features:
                List of features or a dictionary of key-value pairs.
                If a list, each item must be an instance of Feature.
                If a dictionary, each key is the feature name and each value is the feature value.
                Supported types for values are int, float, and string.

        Example:
            ```python
            # Passing a list of features
            features = Features(
                features=[
                    Feature.int("feature_1", 1),
                    Feature.float("feature_2", 2.0),
                    Feature.string("feature_3", "value"),
                ]
            )

            # Passing a dictionary (pydantic model) of features
            class MyFeatures(BaseModel):
                feature1: int
                feature2: float
                feature3: str

            my_features = MyFeatures(
                feature1=1,
                feature2=2.0,
                feature3="value",
            )

            features = Features(my_features.model_dump())
            ```
        """

    def __str__(self) -> str:
        """Return the string representation of the features"""

    @property
    def features(self) -> List[QueueFeature]:
        """Return the list of features"""

    @property
    def entity_type(self) -> EntityType:
        """Return the entity type"""

class Metric:
    def __init__(self, name: str, value: float | int) -> None:
        """Initialize metric

        Args:
            name:
                Name of the metric
            value:
                Value to assign to the metric. Can be an int or float but will be converted to float.
        """

    def __str__(self) -> str:
        """Return the string representation of the metric"""

class Metrics:
    def __init__(self, metrics: List[Metric] | Dict[str, Union[int, float]]) -> None:
        """Initialize metrics

        Args:
            metrics:
                List of metrics or a dictionary of key-value pairs.
                If a list, each item must be an instance of Metric.
                If a dictionary, each key is the metric name and each value is the metric value.


        Example:
            ```python

            # Passing a list of metrics
            metrics = Metrics(
                metrics=[
                    Metric("metric_1", 1.0),
                    Metric("metric_2", 2.5),
                    Metric("metric_3", 3),
                ]
            )

            # Passing a dictionary (pydantic model) of metrics
            class MyMetrics(BaseModel):
                metric1: float
                metric2: int

            my_metrics = MyMetrics(
                metric1=1.0,
                metric2=2,
            )

            metrics = Metrics(my_metrics.model_dump())
        """

    def __str__(self) -> str:
        """Return the string representation of the metrics"""

    @property
    def metrics(self) -> List["Metric"]:
        """Return the list of metrics"""

    @property
    def entity_type(self) -> EntityType:
        """Return the entity type"""

class Queue:
    """Individual queue associated with a drift profile"""

    def insert(self, item: Union[Features, Metrics, GenAIEvalRecord]) -> None:
        """Insert a record into the queue

        Args:
            item:
                Item to insert into the queue.
                Can be an instance for Features, Metrics, or GenAIEvalRecord.

        Example:
            ```python
            features = Features(
                features=[
                    Feature("feature_1", 1),
                    Feature("feature_2", 2.0),
                    Feature("feature_3", "value"),
                ]
            )
            queue.insert(features)
            ```
        """

    @property
    def identifier(self) -> str:
        """Return the identifier of the queue"""

class ScouterQueue:
    """Main queue class for Scouter. Publishes drift records to the configured transport"""

    @staticmethod
    def from_path(
        path: Dict[str, Path],
        transport_config: Union[
            KafkaConfig,
            RabbitMQConfig,
            RedisConfig,
            HttpConfig,
            GrpcConfig,
        ],
    ) -> "ScouterQueue":
        """Initializes Scouter queue from one or more drift profile paths.

        ```
        ╔══════════════════════════════════════════════════════════════════════════╗
        ║                    SCOUTER QUEUE ARCHITECTURE                            ║
        ╠══════════════════════════════════════════════════════════════════════════╣
        ║                                                                          ║
        ║  Python Runtime (Client)                                                 ║
        ║  ┌────────────────────────────────────────────────────────────────────┐  ║
        ║  │  ScouterQueue.from_path()                                          │  ║
        ║  │    • Load drift profiles (SPC, PSI, Custom, LLM)                   │  ║
        ║  │    • Configure transport (Kafka, RabbitMQ, Redis, HTTP, gRPC)      │  ║
        ║  └───────────────────────────┬────────────────────────────────────────┘  ║
        ║                              │                                           ║
        ║                              ▼                                           ║
        ║  ┌────────────────────────────────────────────────────────────────────┐  ║
        ║  │  queue["profile_alias"].insert(Features | Metrics | GenAIEvalRecord)     │  ║
        ║  └───────────────────────────┬────────────────────────────────────────┘  ║
        ║                              │                                           ║
        ╚══════════════════════════════╪═══════════════════════════════════════════╝
                                       │
                                       │  Language Boundary
                                       │
        ╔══════════════════════════════╪═══════════════════════════════════════════╗
        ║  Rust Runtime (Producer)     ▼                                           ║
        ║  ┌────────────────────────────────────────────────────────────────────┐  ║
        ║  │  Queue<T> (per profile)                                            │  ║
        ║  │    • Buffer records in memory                                      │  ║
        ║  │    • Validate against drift profile schema                         │  ║
        ║  │    • Convert to ServerRecord format                                │  ║
        ║  └───────────────────────────┬────────────────────────────────────────┘  ║
        ║                              │                                           ║
        ║                              ▼                                           ║
        ║  ┌────────────────────────────────────────────────────────────────────┐  ║
        ║  │  Transport Producer                                                │  ║
        ║  │    • KafkaProducer    → Kafka brokers                              │  ║
        ║  │    • RabbitMQProducer → RabbitMQ exchange                          │  ║
        ║  │    • RedisProducer    → Redis pub/sub                              │  ║
        ║  │    • HttpProducer     → HTTP endpoint                              │  ║
        ║  │    • GrpcProducer     → gRPC server                                │  ║
        ║  └───────────────────────────┬────────────────────────────────────────┘  ║
        ║                              │                                           ║
        ╚══════════════════════════════╪═══════════════════════════════════════════╝
                                       │
                                       │  Network/Message Bus
                                       │
        ╔══════════════════════════════╪═══════════════════════════════════════════╗
        ║  Scouter Server              ▼                                           ║
        ║  ┌────────────────────────────────────────────────────────────────────┐  ║
        ║  │  Consumer (Kafka/RabbitMQ/Redis/HTTP/gRPC)                         │  ║
        ║  │    • Receive drift records                                         │  ║
        ║  │    • Deserialize & validate                                        │  ║
        ║  └───────────────────────────┬────────────────────────────────────────┘  ║
        ║                              │                                           ║
        ║                              ▼                                           ║
        ║  ┌────────────────────────────────────────────────────────────────────┐  ║
        ║  │  Processing Pipeline                                               │  ║
        ║  │    • Calculate drift metrics (SPC, PSI)                            │  ║
        ║  │    • Evaluate alert conditions                                     │  ║
        ║  │    • Store in PostgreSQL                                           │  ║
        ║  │    • Dispatch alerts (Slack, OpsGenie, Console)                    │  ║
        ║  └────────────────────────────────────────────────────────────────────┘  ║
        ║                                                                          ║
        ╚══════════════════════════════════════════════════════════════════════════╝
        ```
        Flow Summary:
            1. **Python Runtime**: Initialize queue with drift profiles and transport config
            2. **Insert Records**: Call queue["alias"].insert() with Features/Metrics/GenAIEvalRecord
            3. **Rust Queue**: Buffer and validate records against profile schema
            4. **Transport Producer**: Serialize and publish to configured transport
            5. **Network**: Records travel via Kafka/RabbitMQ/Redis/HTTP/gRPC
            6. **Scouter Server**: Consumer receives, processes, and stores records
            7. **Alerting**: Evaluate drift conditions and dispatch alerts if triggered

        Args:
            path (Dict[str, Path]):
                Dictionary of drift profile paths.
                Each key is a user-defined alias for accessing a queue.

                Supported profile types:
                    • SpcDriftProfile    - Statistical Process Control monitoring
                    • PsiDriftProfile    - Population Stability Index monitoring
                    • CustomDriftProfile - Custom metric monitoring
                    • GenAIEvalProfile    - LLM evaluation monitoring

            transport_config (Union[KafkaConfig, RabbitMQConfig, RedisConfig, HttpConfig, GrpcConfig]):
                Transport configuration for the queue publisher.

                Available transports:
                    • KafkaConfig     - Apache Kafka message bus
                    • RabbitMQConfig  - RabbitMQ message broker
                    • RedisConfig     - Redis pub/sub
                    • HttpConfig      - Direct HTTP to Scouter server
                    • GrpcConfig      - Direct gRPC to Scouter server

        Returns:
            ScouterQueue:
                Configured queue with Rust-based producers for each drift profile.

        Examples:
            Basic SPC monitoring with Kafka:
                >>> queue = ScouterQueue.from_path(
                ...     path={"spc": Path("spc_drift_profile.json")},
                ...     transport_config=KafkaConfig(
                ...         brokers="localhost:9092",
                ...         topic="scouter_monitoring",
                ...     ),
                ... )
                >>> queue["spc"].insert(
                ...     Features(features=[
                ...         Feature("feature_1", 1.5),
                ...         Feature("feature_2", 2.3),
                ...     ])
                ... )

            Multi-profile monitoring with HTTP:
                >>> queue = ScouterQueue.from_path(
                ...     path={
                ...         "spc": Path("spc_profile.json"),
                ...         "psi": Path("psi_profile.json"),
                ...         "custom": Path("custom_profile.json"),
                ...     },
                ...     transport_config=HttpConfig(
                ...         server_uri="http://scouter-server:8000",
                ...     ),
                ... )
                >>> queue["psi"].insert(Features(...))
                >>> queue["custom"].insert(Metrics(...))

            LLM monitoring with gRPC:
                >>> queue = ScouterQueue.from_path(
                ...     path={"genai_eval": Path("genai_profile.json")},
                ...     transport_config=GrpcConfig(
                ...         server_uri="http://scouter-server:50051",
                ...         username="monitoring_user",
                ...         password="secure_password",
                ...     ),
                ... )
                >>> queue["genai_eval"].insert(
                ...     GenAIEvalRecord(context={"input": "...", "response": "..."})
                ... )
        """

    def __getitem__(self, key: str) -> Queue:
        """Get the queue for the specified key

        Args:
            key (str):
                Key to get the queue for

        """

    def shutdown(self) -> None:
        """Shutdown the queue. This will close and flush all queues and transports"""

    @property
    def transport_config(
        self,
    ) -> Union[KafkaConfig, RabbitMQConfig, RedisConfig, HttpConfig, MockConfig]:
        """Return the transport configuration used by the queue"""

class GenAIEvalRecord:
    """LLM record containing context tied to a Large Language Model interaction
    that is used to evaluate drift in LLM responses.


    Examples:
        >>> record = GenAIEvalRecord(
        ...     context={
        ...         "input": "What is the capital of France?",
        ...         "response": "Paris is the capital of France."
        ...     },
        ... )
        >>> print(record.context["input"])
        "What is the capital of France?"
    """

    def __init__(
        self,
        context: Context,
        id: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> None:
        """Creates a new LLM record to associate with an `GenAIEvalProfile`.
        The record is sent to the `Scouter` server via the `ScouterQueue` and is
        then used to inject context into the evaluation prompts.

        Args:
            context (Dict[str, Any] | BaseModel):
                Additional context information as a dictionary or a pydantic BaseModel. During evaluation,
                this will be merged with the input and response data and passed to the assigned
                evaluation prompts. So if you're evaluation prompts expect additional context via
                bound variables (e.g., `${foo}`), you can pass that here as key value pairs.
                {"foo": "bar"}
            id (Optional[str], optional):
                Optional unique identifier for the record.
            session_id (Optional[str], optional):
                Optional session identifier to group related records.

        Raises:
            TypeError: If context is not a dict or a pydantic BaseModel.

        """

    @property
    def session_id(self) -> str:
        """Get the session ID."""

    @session_id.setter
    def session_id(self, session_id: str) -> None:
        """Set the session ID."""

    @property
    def record_id(self) -> Optional[str]:
        """Get the record ID."""

    @record_id.setter
    def record_id(self, record_id: str) -> None:
        """Set the record ID."""

    @property
    def created_at(self) -> datetime.datetime:
        """Get the created at timestamp."""

    @property
    def uid(self) -> str:
        """Get the unique identifier for the record."""

    @property
    def context(self) -> Dict[str, Any]:
        """Get the contextual information.

        Returns:
            The context data as a Python object (deserialized from JSON).

        Raises:
            TypeError: If the stored JSON cannot be converted to a Python object.
        """

    def __str__(self) -> str:
        """Return the string representation of the record."""

    def model_dump_json(self) -> str:
        """Return the json representation of the record."""

    def update_context_field(self, key: str, value: Any) -> None:
        """Update a specific field in the context.
        If the key does not exist, it will be added.

        Args:
            key (str):
                The key of the context field to update.
            value (Any):
                The new value for the context field.
        """

class LatencyMetrics:
    @property
    def p5(self) -> float:
        """5th percentile"""

    @property
    def p25(self) -> float:
        """25th percentile"""

    @property
    def p50(self) -> float:
        """50th percentile"""

    @property
    def p95(self) -> float:
        """95th percentile"""

    @property
    def p99(self) -> float:
        """99th percentile"""

class RouteMetrics:
    @property
    def route_name(self) -> str:
        """Return the route name"""

    @property
    def metrics(self) -> LatencyMetrics:
        """Return the metrics"""

    @property
    def request_count(self) -> int:
        """Request count"""

    @property
    def error_count(self) -> int:
        """Error count"""

    @property
    def error_latency(self) -> float:
        """Error latency"""

    @property
    def status_codes(self) -> Dict[int, int]:
        """Dictionary of status codes and counts"""

class ObservabilityMetrics:
    @property
    def space(self) -> str:
        """Return the space"""

    @property
    def name(self) -> str:
        """Return the name"""

    @property
    def version(self) -> str:
        """Return the version"""

    @property
    def request_count(self) -> int:
        """Request count"""

    @property
    def error_count(self) -> int:
        """Error count"""

    @property
    def route_metrics(self) -> List[RouteMetrics]:
        """Route metrics object"""

    def __str__(self) -> str:
        """Return the string representation of the observability metrics"""

    def model_dump_json(self) -> str:
        """Return the json representation of the observability metrics"""

class Observer:
    def __init__(self, uid: str) -> None:
        """Initializes an api metric observer

        Args:
            uid:
                Unique identifier for the observer
        """

    def increment(self, route: str, latency: float, status_code: int) -> None:
        """Increment the feature value

        Args:
            route:
                Route name
            latency:
                Latency of request
            status_code:
                Status code of request
        """

    def collect_metrics(self) -> Optional[ServerRecords]:
        """Collect metrics from observer"""

    def reset_metrics(self) -> None:
        """Reset the observer metrics"""

class FeatureMap:
    @property
    def features(self) -> Dict[str, Dict[str, int]]:
        """Return the feature map."""

    def __str__(self) -> str:
        """Return the string representation of the feature map."""

class SpcFeatureDriftProfile:
    @property
    def id(self) -> str:
        """Return the id."""

    @property
    def center(self) -> float:
        """Return the center."""

    @property
    def one_ucl(self) -> float:
        """Return the zone 1 ucl."""

    @property
    def one_lcl(self) -> float:
        """Return the zone 1 lcl."""

    @property
    def two_ucl(self) -> float:
        """Return the zone 2 ucl."""

    @property
    def two_lcl(self) -> float:
        """Return the zone 2 lcl."""

    @property
    def three_ucl(self) -> float:
        """Return the zone 3 ucl."""

    @property
    def three_lcl(self) -> float:
        """Return the zone 3 lcl."""

    @property
    def timestamp(self) -> str:
        """Return the timestamp."""

class SpcDriftConfig:
    def __init__(
        self,
        space: str = "__missing__",
        name: str = "__missing__",
        version: str = "0.1.0",
        sample_size: int = 25,
        alert_config: SpcAlertConfig = SpcAlertConfig(),
        config_path: Optional[Path] = None,
    ):
        """Initialize monitor config

        Args:
            space:
                Model space
            name:
                Model name
            version:
                Model version. Defaults to 0.1.0
            sample_size:
                Sample size
            alert_config:
                Alert configuration
            config_path:
                Optional path to load config from.
        """

    @property
    def sample_size(self) -> int:
        """Return the sample size."""

    @sample_size.setter
    def sample_size(self, sample_size: int) -> None:
        """Set the sample size."""

    @property
    def name(self) -> str:
        """Model Name"""

    @name.setter
    def name(self, name: str) -> None:
        """Set model name"""

    @property
    def space(self) -> str:
        """Model space"""

    @space.setter
    def space(self, space: str) -> None:
        """Set model space"""

    @property
    def version(self) -> str:
        """Model version"""

    @version.setter
    def version(self, version: str) -> None:
        """Set model version"""

    @property
    def uid(self) -> str:
        """Unique identifier for the drift config"""

    @uid.setter
    def uid(self, uid: str) -> None:
        """Set unique identifier for the drift config"""

    @property
    def feature_map(self) -> Optional[FeatureMap]:
        """Feature map"""

    @property
    def alert_config(self) -> SpcAlertConfig:
        """Alert configuration"""

    @alert_config.setter
    def alert_config(self, alert_config: SpcAlertConfig) -> None:
        """Set alert configuration"""

    @property
    def drift_type(self) -> DriftType:
        """Drift type"""

    @staticmethod
    def load_from_json_file(path: Path) -> "SpcDriftConfig":
        """Load config from json file

        Args:
            path:
                Path to json file to load config from.
        """

    def __str__(self) -> str:
        """Return the string representation of the config."""

    def model_dump_json(self) -> str:
        """Return the json representation of the config."""

    def update_config_args(
        self,
        space: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
        sample_size: Optional[int] = None,
        alert_config: Optional[SpcAlertConfig] = None,
    ) -> None:
        """Inplace operation that updates config args

        Args:
            space:
                Model space
            name:
                Model name
            version:
                Model version
            sample_size:
                Sample size
            alert_config:
                Alert configuration
        """

class SpcDriftProfile:
    @property
    def uid(self) -> str:
        """Return the unique identifier for the drift profile"""

    @property
    def scouter_version(self) -> str:
        """Return scouter version used to create DriftProfile"""

    @property
    def features(self) -> Dict[str, SpcFeatureDriftProfile]:
        """Return the list of features."""

    @property
    def config(self) -> SpcDriftConfig:
        """Return the monitor config."""

    def model_dump_json(self) -> str:
        """Return json representation of drift profile"""

    def model_dump(self) -> Dict[str, Any]:
        """Return dictionary representation of drift profile"""

    def save_to_json(self, path: Optional[Path] = None) -> Path:
        """Save drift profile to json file

        Args:
            path:
                Optional path to save the drift profile. If None, outputs to `spc_drift_profile.json`


        Returns:
            Path to the saved json file
        """

    @staticmethod
    def model_validate_json(json_string: str) -> "SpcDriftProfile":
        """Load drift profile from json

        Args:
            json_string:
                JSON string representation of the drift profile

        """

    @staticmethod
    def from_file(path: Path) -> "SpcDriftProfile":
        """Load drift profile from file

        Args:
            path: Path to the file
        """

    @staticmethod
    def model_validate(data: Dict[str, Any]) -> "SpcDriftProfile":
        """Load drift profile from dictionary

        Args:
            data:
                DriftProfile dictionary
        """

    def update_config_args(
        self,
        space: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
        sample_size: Optional[int] = None,
        alert_config: Optional[SpcAlertConfig] = None,
    ) -> None:
        """Inplace operation that updates config args

        Args:
            name:
                Model name
            space:
                Model space
            version:
                Model version
            sample_size:
                Sample size
            alert_config:
                Alert configuration
        """

    def __str__(self) -> str:
        """Sting representation of DriftProfile"""

class FeatureDrift:
    @property
    def samples(self) -> List[float]:
        """Return list of samples"""

    @property
    def drift(self) -> List[float]:
        """Return list of drift values"""

    def __str__(self) -> str:
        """Return string representation of feature drift"""

class SpcFeatureDrift:
    @property
    def samples(self) -> List[float]:
        """Return list of samples"""

    @property
    def drift(self) -> List[float]:
        """Return list of drift values"""

class SpcDriftMap:
    """Drift map of features"""

    @property
    def space(self) -> str:
        """Space to associate with drift map"""

    @property
    def name(self) -> str:
        """name to associate with drift map"""

    @property
    def version(self) -> str:
        """Version to associate with drift map"""

    @property
    def features(self) -> Dict[str, SpcFeatureDrift]:
        """Returns dictionary of features and their data profiles"""

    def __str__(self) -> str:
        """Return string representation of data drift"""

    def model_dump_json(self) -> str:
        """Return json representation of data drift"""

    @staticmethod
    def model_validate_json(json_string: str) -> "SpcDriftMap":
        """Load drift map from json file.

        Args:
            json_string:
                JSON string representation of the drift map
        """

    def save_to_json(self, path: Optional[Path] = None) -> Path:
        """Save drift map to json file

        Args:
            path:
                Optional path to save the drift map. If None, outputs to `spc_drift_map.json`

        Returns:
            Path to the saved json file

        """

    def to_numpy(self) -> Any:
        """Return drift map as a tuple of sample_array, drift_array and list of features"""

class Manual:
    def __init__(self, num_bins: int):
        """Manual equal-width binning strategy.

        Divides the feature range into a fixed number of equally sized bins.

        Args:
            num_bins:
                The exact number of bins to create.
        """

    @property
    def num_bins(self) -> int:
        """The number of bins you want created"""

    @num_bins.setter
    def num_bins(self, num_bins: int) -> None:
        """Set the number of bins you want created"""

class SquareRoot:
    def __init__(self):
        """Use the SquareRoot equal-width method.

        For more information, please see: https://en.wikipedia.org/wiki/Histogram
        """

class Sturges:
    def __init__(self):
        """Use the Sturges equal-width method.

        For more information, please see: https://en.wikipedia.org/wiki/Histogram
        """

class Rice:
    def __init__(self):
        """Use the Rice equal-width method.

        For more information, please see: https://en.wikipedia.org/wiki/Histogram
        """

class Doane:
    def __init__(self):
        """Use the Doane equal-width method.

        For more information, please see: https://en.wikipedia.org/wiki/Histogram
        """

class Scott:
    def __init__(self):
        """Use the Scott equal-width method.

        For more information, please see: https://en.wikipedia.org/wiki/Histogram
        """

class TerrellScott:
    def __init__(self):
        """Use the Terrell-Scott equal-width method.

        For more information, please see: https://en.wikipedia.org/wiki/Histogram
        """

class FreedmanDiaconis:
    def __init__(self):
        """Use the Freedman–Diaconis equal-width method.

        For more information, please see: https://en.wikipedia.org/wiki/Histogram
        """

EqualWidthMethods = Manual | SquareRoot | Sturges | Rice | Doane | Scott | TerrellScott | FreedmanDiaconis

class EqualWidthBinning:
    def __init__(self, method: EqualWidthMethods = Doane()):
        """Initialize the equal-width binning configuration.

        This strategy divides the range of values into bins of equal width.
        Several binning rules are supported to automatically determine the
        appropriate number of bins based on the input distribution.

        Note:
            Detailed explanations of each method are provided in their respective
            constructors or documentation.

        Args:
            method:
                Specifies how the number of bins should be determined.
                Options include:
                  - Manual(num_bins): Explicitly sets the number of bins.
                  - SquareRoot, Sturges, Rice, Doane, Scott, TerrellScott,
                    FreedmanDiaconis: Rules that infer bin counts from data.
                Defaults to Doane().
        """

    @property
    def method(self) -> EqualWidthMethods:
        """Specifies how the number of bins should be determined."""

    @method.setter
    def method(self, method: EqualWidthMethods) -> None:
        """Specifies how the number of bins should be determined."""

class QuantileBinning:
    def __init__(self, num_bins: int = 10):
        """Initialize the quantile binning strategy.

        This strategy uses the R-7 quantile method (Hyndman & Fan Type 7) to
        compute bin edges. It is the default quantile method in R and provides
        continuous, median-unbiased estimates that are approximately unbiased
        for normal distributions.

        The R-7 method defines quantiles using:
            - m = 1 - p
            - j = floor(n * p + m)
            - h = n * p + m - j
            - Q(p) = (1 - h) * x[j] + h * x[j+1]

        Reference:
            Hyndman, R. J. & Fan, Y. (1996). "Sample quantiles in statistical packages."
            The American Statistician, 50(4), pp. 361–365.
            PDF: https://www.amherst.edu/media/view/129116/original/Sample+Quantiles.pdf

        Args:
            num_bins:
                Number of bins to compute using the R-7 quantile method.
        """

    @property
    def num_bins(self) -> int:
        """The number of bins you want created using the r7 quantile method"""

    @num_bins.setter
    def num_bins(self, num_bins: int) -> None:
        """Set the number of bins you want created using the r7 quantile method"""

class PsiDriftConfig:
    def __init__(
        self,
        space: str = "__missing__",
        name: str = "__missing__",
        version: str = "0.1.0",
        alert_config: PsiAlertConfig = PsiAlertConfig(),
        config_path: Optional[Path] = None,
        categorical_features: Optional[list[str]] = None,
        binning_strategy: QuantileBinning | EqualWidthBinning = QuantileBinning(num_bins=10),
    ):
        """Initialize monitor config

        Args:
            space:
                Model space
            name:
                Model name
            version:
                Model version. Defaults to 0.1.0
            alert_config:
                Alert configuration
            config_path:
                Optional path to load config from.
            categorical_features:
                List of features to treat as categorical for PSI calculation.
            binning_strategy:
                Strategy for binning continuous features during PSI calculation.
                Supports:
                  - QuantileBinning (R-7 method, Hyndman & Fan Type 7).
                  - EqualWidthBinning which divides the range of values into fixed-width bins.
                Default is QuantileBinning with 10 bins. You can also specify methods like Doane's rule with EqualWidthBinning.
        """

    @property
    def name(self) -> str:
        """Model Name"""

    @name.setter
    def name(self, name: str) -> None:
        """Set model name"""

    @property
    def space(self) -> str:
        """Model space"""

    @space.setter
    def space(self, space: str) -> None:
        """Set model space"""

    @property
    def version(self) -> str:
        """Model version"""

    @version.setter
    def version(self, version: str) -> None:
        """Set model version"""

    @property
    def uid(self) -> str:
        """Unique identifier for the drift config"""

    @uid.setter
    def uid(self, uid: str) -> None:
        """Set unique identifier for the drift config"""

    @property
    def feature_map(self) -> Optional[FeatureMap]:
        """Feature map"""

    @property
    def alert_config(self) -> PsiAlertConfig:
        """Alert configuration"""

    @alert_config.setter
    def alert_config(self, alert_config: PsiAlertConfig) -> None:
        """Set alert configuration"""

    @property
    def drift_type(self) -> DriftType:
        """Drift type"""

    @property
    def binning_strategy(self) -> QuantileBinning | EqualWidthBinning:
        """binning_strategy"""

    @binning_strategy.setter
    def binning_strategy(self, binning_strategy: QuantileBinning | EqualWidthBinning) -> None:
        """Set binning_strategy"""

    @property
    def categorical_features(self) -> list[str]:
        """list of categorical features"""

    @categorical_features.setter
    def categorical_features(self, categorical_features: list[str]) -> None:
        """Set list of categorical features"""

    @staticmethod
    def load_from_json_file(path: Path) -> "PsiDriftConfig":
        """Load config from json file

        Args:
            path:
                Path to json file to load config from.
        """

    def __str__(self) -> str:
        """Return the string representation of the config."""

    def model_dump_json(self) -> str:
        """Return the json representation of the config."""

    def update_config_args(
        self,
        space: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
        alert_config: Optional[PsiAlertConfig] = None,
        categorical_features: Optional[list[str]] = None,
        binning_strategy: Optional[QuantileBinning | EqualWidthBinning] = None,
    ) -> None:
        """Inplace operation that updates config args

        Args:
            space:
                Model space
            name:
                Model name
            version:
                Model version
            alert_config:
                Alert configuration
            categorical_features:
                Categorical features
            binning_strategy:
                Binning strategy
        """

class PsiDriftProfile:
    @property
    def uid(self) -> str:
        """Return the unique identifier for the drift profile"""

    @property
    def scouter_version(self) -> str:
        """Return scouter version used to create DriftProfile"""

    @property
    def features(self) -> Dict[str, PsiFeatureDriftProfile]:
        """Return the list of features."""

    @property
    def config(self) -> PsiDriftConfig:
        """Return the monitor config."""

    def model_dump_json(self) -> str:
        """Return json representation of drift profile"""

    def model_dump(self) -> Dict[str, Any]:
        """Return dictionary representation of drift profile"""

    def save_to_json(self, path: Optional[Path] = None) -> Path:
        """Save drift profile to json file

        Args:
            path:
                Optional path to save the drift profile. If None, outputs to `psi_drift_profile.json`

        Returns:
            Path to the saved json file
        """

    @staticmethod
    def model_validate_json(json_string: str) -> "PsiDriftProfile":
        """Load drift profile from json

        Args:
            json_string:
                JSON string representation of the drift profile

        """

    @staticmethod
    def from_file(path: Path) -> "PsiDriftProfile":
        """Load drift profile from file

        Args:
            path: Path to the file
        """

    @staticmethod
    def model_validate(data: Dict[str, Any]) -> "PsiDriftProfile":
        """Load drift profile from dictionary

        Args:
            data:
                DriftProfile dictionary
        """

    def update_config_args(
        self,
        space: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
        alert_config: Optional[PsiAlertConfig] = None,
        categorical_features: Optional[list[str]] = None,
        binning_strategy: Optional[QuantileBinning | EqualWidthBinning] = None,
    ) -> None:
        """Inplace operation that updates config args

        Args:
            name:
                Model name
            space:
                Model space
            version:
                Model version
            alert_config:
                Alert configuration
            categorical_features:
                Categorical Features
            binning_strategy:
                Binning strategy
        """

    def __str__(self) -> str:
        """Sting representation of DriftProfile"""

class Bin:
    @property
    def id(self) -> int:
        """Return the bin id."""

    @property
    def lower_limit(self) -> float:
        """Return the lower limit of the bin."""

    @property
    def upper_limit(self) -> Optional[float]:
        """Return the upper limit of the bin."""

    @property
    def proportion(self) -> float:
        """Return the proportion of data found in the bin."""

class BinType:
    Numeric: "BinType"
    Category: "BinType"

class PsiFeatureDriftProfile:
    @property
    def id(self) -> str:
        """Return the feature name"""

    @property
    def bins(self) -> List[Bin]:
        """Return the bins"""

    @property
    def timestamp(self) -> str:
        """Return the timestamp."""

    @property
    def bin_type(self) -> BinType:
        """Return the timestamp."""

class PsiDriftMap:
    """Drift map of features"""

    @property
    def space(self) -> str:
        """Space to associate with drift map"""

    @property
    def name(self) -> str:
        """name to associate with drift map"""

    @property
    def version(self) -> str:
        """Version to associate with drift map"""

    @property
    def features(self) -> Dict[str, float]:
        """Returns dictionary of features and their reported drift, if any"""

    def __str__(self) -> str:
        """Return string representation of data drift"""

    def model_dump_json(self) -> str:
        """Return json representation of data drift"""

    @staticmethod
    def model_validate_json(json_string: str) -> "PsiDriftMap":
        """Load drift map from json file.

        Args:
            json_string:
                JSON string representation of the drift map
        """

    def save_to_json(self, path: Optional[Path] = None) -> Path:
        """Save drift map to json file

        Args:
            path:
                Optional path to save the drift map. If None, outputs to `psi_drift_map.json`

        Returns:
            Path to the saved json file

        """

class CustomMetricDriftConfig:
    def __init__(
        self,
        space: str = "__missing__",
        name: str = "__missing__",
        version: str = "0.1.0",
        sample_size: int = 25,
        alert_config: CustomMetricAlertConfig = CustomMetricAlertConfig(),
    ):
        """Initialize drift config
        Args:
            space:
                Model space
            name:
                Model name
            version:
                Model version. Defaults to 0.1.0
            sample_size:
                Sample size
            alert_config:
                Custom metric alert configuration
        """

    @property
    def space(self) -> str:
        """Model space"""

    @space.setter
    def space(self, space: str) -> None:
        """Set model space"""

    @property
    def name(self) -> str:
        """Model Name"""

    @name.setter
    def name(self, name: str) -> None:
        """Set model name"""

    @property
    def version(self) -> str:
        """Model version"""

    @version.setter
    def version(self, version: str) -> None:
        """Set model version"""

    @property
    def uid(self) -> str:
        """Unique identifier for the drift config"""

    @uid.setter
    def uid(self, uid: str) -> None:
        """Set unique identifier for the drift config"""

    @property
    def drift_type(self) -> DriftType:
        """Drift type"""

    @property
    def alert_config(self) -> CustomMetricAlertConfig:
        """get alert_config"""

    @alert_config.setter
    def alert_config(self, alert_config: CustomMetricAlertConfig) -> None:
        """Set alert_config"""

    @staticmethod
    def load_from_json_file(path: Path) -> "CustomMetricDriftConfig":
        """Load config from json file
        Args:
            path:
                Path to json file to load config from.
        """

    def __str__(self) -> str:
        """Return the string representation of the config."""

    def model_dump_json(self) -> str:
        """Return the json representation of the config."""

    def update_config_args(
        self,
        space: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
        alert_config: Optional[CustomMetricAlertConfig] = None,
    ) -> None:
        """Inplace operation that updates config args
        Args:
            space:
                Model space
            name:
                Model name
            version:
                Model version
            alert_config:
                Custom metric alert configuration
        """

class CustomMetric:
    def __init__(
        self,
        name: str,
        baseline_value: float,
        alert_threshold: AlertThreshold,
        delta: Optional[float] = None,
    ):
        """
        Initialize a custom metric for alerting.

        This class represents a custom metric that uses comparison-based alerting. It applies
        an alert condition to a single metric value.

        Args:
            name (str):
                The name of the metric being monitored. This should be a descriptive identifier for the metric.
            baseline_value (float):
                The baseline value of the metric.
            alert_threshold (AlertThreshold):
                The condition used to determine when an alert should be triggered.
            delta (Optional[float]):
                The delta value used in conjunction with the alert_threshold.
                If supplied, this value will be added or subtracted from the provided metric value to
                determine if an alert should be triggered.

        """

    @property
    def name(self) -> str:
        """Return the metric name"""

    @name.setter
    def name(self, name: str) -> None:
        """Set the metric name"""

    @property
    def baseline_value(self) -> float:
        """Return the baseline value"""

    @baseline_value.setter
    def baseline_value(self, value: float) -> None:
        """Set the baseline value"""

    @property
    def alert_condition(self) -> AlertCondition:
        """Return the alert_condition"""

    @alert_condition.setter
    def alert_condition(self, alert_condition: AlertCondition) -> None:
        """Set the alert_condition"""

    @property
    def alert_threshold(self) -> AlertThreshold:
        """Return the alert_threshold"""

    @property
    def delta(self) -> Optional[float]:
        """Return the delta value"""

    def __str__(self) -> str:
        """Return the string representation of the config."""

class CustomDriftProfile:
    def __init__(
        self,
        config: CustomMetricDriftConfig,
        metrics: list[CustomMetric],
    ):
        """Initialize a CustomDriftProfile instance.

        Args:
            config (CustomMetricDriftConfig):
                The configuration for custom metric drift detection.
            metrics (list[CustomMetric]):
                A list of CustomMetric objects representing the metrics to be monitored.

        Example:
            config = CustomMetricDriftConfig(...)
            metrics = [CustomMetric("accuracy", 0.95), CustomMetric("f1_score", 0.88)]
            profile = CustomDriftProfile(config, metrics, "1.0.0")
        """

    @property
    def uid(self) -> str:
        """Return the unique identifier for the drift profile"""

    @property
    def config(self) -> CustomMetricDriftConfig:
        """Return the drift config"""

    @property
    def metrics(self) -> dict[str, float]:
        """Return custom metrics and their corresponding values"""

    @property
    def scouter_version(self) -> str:
        """Return scouter version used to create DriftProfile"""

    @property
    def custom_metrics(self) -> list[CustomMetric]:
        """Return custom metric objects that were used to create the drift profile"""

    def __str__(self) -> str:
        """Sting representation of DriftProfile"""

    def model_dump_json(self) -> str:
        """Return json representation of drift profile"""

    def model_dump(self) -> Dict[str, Any]:
        """Return dictionary representation of drift profile"""

    def save_to_json(self, path: Optional[Path] = None) -> Path:
        """Save drift profile to json file

        Args:
            path:
                Optional path to save the drift profile. If None, outputs to `custom_drift_profile.json`

        Returns:
            Path to the saved json file
        """

    @staticmethod
    def model_validate_json(json_string: str) -> "CustomDriftProfile":
        """Load drift profile from json

        Args:
            json_string:
                JSON string representation of the drift profile

        """

    @staticmethod
    def model_validate(data: Dict[str, Any]) -> "CustomDriftProfile":
        """Load drift profile from dictionary

        Args:
            data:
                DriftProfile dictionary
        """

    @staticmethod
    def from_file(path: Path) -> "CustomDriftProfile":
        """Load drift profile from file

        Args:
            path: Path to the file
        """

    def update_config_args(
        self,
        space: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
        alert_config: Optional[CustomMetricAlertConfig] = None,
    ) -> None:
        """Inplace operation that updates config args

        Args:
            space (Optional[str]):
                Model space
            name (Optional[str]):
                Model name
            version (Optional[str]):
                Model version
            alert_config (Optional[CustomMetricAlertConfig]):
                Custom metric alert configuration

        Returns:
            None
        """

class GenAIEvalConfig:
    def __init__(
        self,
        space: str = "__missing__",
        name: str = "__missing__",
        version: str = "0.1.0",
        sample_ratio: float = 1.0,
        alert_config: GenAIAlertConfig = GenAIAlertConfig(),
    ):
        """Initialize drift config
        Args:
            space:
                Space to associate with the config
            name:
                Name to associate with the config
            version:
                Version to associate with the config. Defaults to 0.1.0
            sample_ratio:
                Sample rate percentage for data collection. Must be between 0.0 and 1.0.
                Defaults to 1.0 (100%).
            alert_config:
                Custom metric alert configuration
        """

    @property
    def space(self) -> str:
        """Model space"""

    @space.setter
    def space(self, space: str) -> None:
        """Set model space"""

    @property
    def name(self) -> str:
        """Model Name"""

    @name.setter
    def name(self, name: str) -> None:
        """Set model name"""

    @property
    def version(self) -> str:
        """Model version"""

    @version.setter
    def version(self, version: str) -> None:
        """Set model version"""

    @property
    def uid(self) -> str:
        """Unique identifier for the drift config"""

    @uid.setter
    def uid(self, uid: str) -> None:
        """Set unique identifier for the drift config"""

    @property
    def drift_type(self) -> DriftType:
        """Drift type"""

    @property
    def alert_config(self) -> GenAIAlertConfig:
        """get alert_config"""

    @alert_config.setter
    def alert_config(self, alert_config: GenAIAlertConfig) -> None:
        """Set alert_config"""

    @staticmethod
    def load_from_json_file(path: Path) -> "GenAIEvalConfig":
        """Load config from json file
        Args:
            path:
                Path to json file to load config from.
        """

    def __str__(self) -> str:
        """Return the string representation of the config."""

    def model_dump_json(self) -> str:
        """Return the json representation of the config."""

    def update_config_args(
        self,
        space: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
        alert_config: Optional[GenAIAlertConfig] = None,
    ) -> None:
        """Inplace operation that updates config args
        Args:
            space:
                Space to associate with the config
            name:
                Name to associate with the config
            version:
                Version to associate with the config
            alert_config:
                LLM alert configuration
        """

class GenAIEvalProfile:
    """Profile for LLM evaluation and drift detection.

    GenAIEvalProfile combines assertion tasks and LLM judge tasks into a unified
    evaluation framework for monitoring LLM performance. Evaluations run asynchronously
    on the Scouter server, enabling scalable drift detection without blocking your
    application.

    Architecture:
        The profile automatically orchestrates two types of evaluation tasks:

        1. **Assertion Tasks**: Fast, deterministic rule-based validations
           - Execute locally without additional LLM calls
           - Ideal for structural validation, threshold checks, pattern matching
           - Zero latency overhead, minimal cost

        2. **LLM Judge Tasks**: Advanced reasoning-based evaluations
           - Leverage additional LLM calls for complex assessments
           - Automatically compiled into an internal Workflow for execution
           - Support dependencies to chain evaluations and pass results
           - Ideal for semantic similarity, quality assessment, factuality checks

    Task Execution Order:
        Tasks are executed based on their dependency graph using topological sort:

        ```
        ╔══════════════════════════════════════════════════════════════╗
        ║              TASK EXECUTION ARCHITECTURE                     ║
        ╠══════════════════════════════════════════════════════════════╣
        ║                                                              ║
        ║  Level 0: Independent Tasks (no dependencies)                ║
        ║  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          ║
        ║  │ Assertion A │  │ Assertion B │  │ LLM Judge X │          ║
        ║  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘          ║
        ║         │                │                │                  ║
        ║         └────────┬───────┴────────┬───────┘                  ║
        ║                  │                │                          ║
        ║  Level 1: Tasks depending on Level 0                         ║
        ║         ┌────────▼────────┐  ┌────▼────────┐                ║
        ║         │  LLM Judge Y    │  │Assertion C  │                ║
        ║         │ (depends: A, X) │  │(depends: B) │                ║
        ║         └────────┬────────┘  └────┬────────┘                ║
        ║                  │                │                          ║
        ║  Level 2: Final aggregation tasks                            ║
        ║                  └────────┬───────┘                          ║
        ║                  ┌────────▼────────┐                         ║
        ║                  │  LLM Judge Z    │                         ║
        ║                  │ (depends: Y, C) │                         ║
        ║                  └─────────────────┘                         ║
        ║                                                              ║
        ╚══════════════════════════════════════════════════════════════╝
        ```

    Workflow Generation:
        When LLM judge tasks are present, the profile automatically:
        1. Builds an internal Workflow from LLMJudgeTask configurations
        2. Validates task dependencies form a valid DAG
        3. Ensures Prompt configurations are compatible with execution
        4. Optimizes execution order for parallel processing where possible

    Common Use Cases:
        - Multi-stage LLM evaluation (relevance → quality → toxicity)
        - Hybrid assertion + LLM judge pipelines (fast checks, then deep analysis)
        - Dependent evaluations (use upstream results in downstream prompts)
        - Cost-optimized monitoring (assertions for 90%, LLM judges for 10%)

    Examples:
        Pure assertion-based monitoring (no LLM calls):

        >>> config = GenAIEvalConfig(
        ...     space="production",
        ...     name="chatbot",
        ...     version="1.0",
        ...     sample_ratio=10
        ... )
        >>>
        >>> tasks = [
        ...     AssertionTask(
        ...         id="response_length",
        ...         field_path="response",
        ...         operator=ComparisonOperator.HasLength,
        ...         expected_value={"min": 10, "max": 500},
        ...         description="Ensure response is reasonable length"
        ...     ),
        ...     AssertionTask(
        ...         id="confidence_threshold",
        ...         field_path="metadata.confidence",
        ...         operator=ComparisonOperator.GreaterThanOrEqual,
        ...         expected_value=0.7,
        ...         description="Require minimum confidence"
        ...     )
        ... ]
        >>>
        >>> profile = GenAIEvalProfile(
        ...     config=config,
        ...     tasks=tasks
        ... )

        LLM judge-based semantic monitoring:

        >>> relevance_prompt = Prompt(
        ...     system_instructions="Evaluate response relevance to query",
        ...     messages="Query: {{input}}\\nResponse: {{response}}\\nRate 0-10:",
        ...     model="gpt-4o-mini",
        ...     provider=Provider.OpenAI,
        ...     output_type=Score
        ... )
        >>>
        >>> judge_tasks = [
        ...     LLMJudgeTask(
        ...         id="relevance_judge",
        ...         prompt=relevance_prompt,
        ...         expected_value=7,
        ...         field_path="score",
        ...         operator=ComparisonOperator.GreaterThanOrEqual,
        ...         description="Ensure relevance score >= 7"
        ...     )
        ... ]
        >>>
        >>> profile = GenAIEvalProfile(
        ...     config=config,
        ...     tasks=judge_tasks
        ... )

        Hybrid monitoring with dependencies:

        >>> # Fast assertion checks first
        >>> assertion_tasks = [
        ...     AssertionTask(
        ...         id="not_empty",
        ...         field_path="response",
        ...         operator=ComparisonOperator.HasLength,
        ...         expected_value={"min": 1},
        ...         description="Response must not be empty"
        ...     )
        ... ]
        >>>
        >>> # Deep LLM analysis only if assertions pass
        >>> quality_prompt = Prompt(
        ...     system_instructions="Assess response quality",
        ...     messages="{{response}}",
        ...     model="claude-3-5-sonnet-20241022",
        ...     provider=Provider.Anthropic,
        ...     output_type=Score
        ... )
        >>>
        >>> judge_tasks = [
        ...     LLMJudgeTask(
        ...         id="quality_judge",
        ...         prompt=quality_prompt,
        ...         expected_value=8,
        ...         field_path="score",
        ...         operator=ComparisonOperator.GreaterThanOrEqual,
        ...         depends_on=["not_empty"],  # Only run if assertion passes
        ...         description="Quality assessment after validation"
        ...     )
        ... ]
        >>>
        >>> profile = GenAIEvalProfile(
        ...     config=config,
        ...     tasks=assertion_tasks + judge_tasks
        ... )

        Multi-stage dependent LLM judges:

        >>> # Stage 1: Relevance check
        >>> relevance_task = LLMJudgeTask(
        ...     id="relevance",
        ...     prompt=relevance_prompt,
        ...     expected_value=7,
        ...     field_path="score",
        ...     operator=ComparisonOperator.GreaterThanOrEqual
        ... )
        >>>
        >>> # Stage 2: Toxicity check (only if relevant)
        >>> toxicity_prompt = Prompt(...)
        >>> toxicity_task = LLMJudgeTask(
        ...     id="toxicity",
        ...     prompt=toxicity_prompt,
        ...     expected_value=0.2,
        ...     field_path="relevance.score",
        ...     operator=ComparisonOperator.LessThan,
        ...     depends_on=["relevance"]  # Chain evaluations
        ... )
        >>>
        >>> # Stage 3: Final quality (only if relevant and non-toxic)
        >>> quality_task = LLMJudgeTask(
        ...     id="quality",
        ...     prompt=quality_prompt,
        ...     expected_value=8,
        ...     field_path="toxicity.score",
        ...     operator=ComparisonOperator.GreaterThanOrEqual,
        ...     depends_on=["relevance", "toxicity"]  # Multiple deps
        ... )
        >>>
        >>> profile = GenAIEvalProfile(
        ...     config=config,
        ...     tasks=[relevance_task, toxicity_task, quality_task]
        ... )

    Note:
        - At least one task (assertion or LLM judge) is required
        - LLM judge tasks are automatically compiled into an internal Workflow
        - Task dependencies must form a valid DAG (no circular dependencies)
        - Execution order is optimized via topological sort
        - Independent tasks at the same level can execute in parallel
        - Failed tasks halt execution of dependent downstream tasks
    """

    def __init__(
        self,
        config: GenAIEvalConfig,
        tasks: List[Union[AssertionTask, LLMJudgeTask]],
    ):
        """Initialize a GenAIEvalProfile for LLM evaluation and drift detection.

        Creates a profile that combines assertion tasks and LLM judge tasks into
        a unified evaluation framework. LLM judge tasks are automatically compiled
        into an internal Workflow for execution on the Scouter server.

        Args:
            config (GenAIEvalConfig):
                Configuration for the GenAI drift profile containing space, name,
                version, sample rate, and alert settings.
            tasks (List[Union[AssertionTask, LLMJudgeTask]]):
                List of evaluation tasks to include in the profile. Can contain
                both AssertionTask and LLMJudgeTask instances. At least one task
                (assertion or LLM judge) is required.

        Returns:
            GenAIEvalProfile: Configured profile ready for GenAI drift monitoring.

        Raises:
            ProfileError: If validation fails due to:
                - Empty task lists (both assertion_tasks and llm_judge_tasks are None/empty)
                - Circular dependencies in task dependency graph
                - Invalid task configurations (malformed prompts, missing fields, etc.)

        Examples:
            Assertion-only profile:

            >>> config = GenAIEvalConfig(space="prod", name="bot", version="1.0")
            >>> assertions = [
            ...     AssertionTask(id="length_check", ...),
            ...     AssertionTask(id="confidence_check", ...)
            ... ]
            >>> profile = GenAIEvalProfile(config, tasks=assertions)

            LLM judge-only profile:

            >>> judges = [
            ...     LLMJudgeTask(id="relevance", prompt=..., ...),
            ...     LLMJudgeTask(id="quality", prompt=..., depends_on=["relevance"])
            ... ]
            >>> profile = GenAIEvalProfile(config, tasks=judges)

            Hybrid profile:

            >>> profile = GenAIEvalProfile(
            ...     config=config,
            ...     tasks=assertions + judges
            ... )
        """

    @property
    def uid(self) -> str:
        """Unique identifier for the drift profile.

        Derived from the config's space, name, and version. Used for tracking
        and querying evaluation results.
        """

    @uid.setter
    def uid(self, uid: str) -> None:
        """Set unique identifier for the drift profile."""

    @property
    def config(self) -> GenAIEvalConfig:
        """Configuration for the drift profile.

        Contains space, name, version, sample rate, and alert settings.
        """

    @property
    def assertion_tasks(self) -> List[AssertionTask]:
        """List of assertion tasks for deterministic validation.

        Assertions execute without additional LLM calls, providing fast,
        cost-effective validation of structural properties, thresholds,
        and patterns.
        """

    @property
    def llm_judge_tasks(self) -> List[LLMJudgeTask]:
        """List of LLM judge tasks for reasoning-based evaluation.

        LLM judges use additional LLM calls to assess complex criteria
        like semantic similarity, quality, and factuality. Automatically
        compiled into an internal Workflow for execution.
        """

    @property
    def scouter_version(self) -> str:
        """Scouter version used to create this profile.

        Used for compatibility tracking and migration support.
        """

    def has_llm_tasks(self) -> bool:
        """Check if profile contains LLM judge tasks.

        Returns:
            bool: True if llm_judge_tasks is non-empty, False otherwise.

        Example:
            >>> if profile.has_llm_tasks():
            ...     print("Profile uses LLM judges (additional cost/latency)")
        """

    def has_assertions(self) -> bool:
        """Check if profile contains assertion tasks.

        Returns:
            bool: True if assertion_tasks is non-empty, False otherwise.

        Example:
            >>> if profile.has_assertions():
            ...     print("Profile includes fast assertion checks")
        """

    def get_execution_plan(self) -> List[List[str]]:
        """Get the execution plan for all tasks.

        Returns task IDs grouped by execution level based on dependency graph.
        Tasks at the same level can execute in parallel. Each subsequent level
        depends on completion of all previous levels.

        Uses topological sort to determine optimal execution order while
        respecting task dependencies.

        Returns:
            List[List[str]]: Nested list where each inner list contains task IDs
                for that execution level. Level 0 contains tasks with no dependencies,
                Level 1 contains tasks depending only on Level 0, etc.

        Raises:
            ProfileError: If circular dependencies are detected in the task graph.

        Example:
            >>> plan = profile.get_execution_plan()
            >>> print(f"Level 0 (parallel): {plan[0]}")
            >>> print(f"Level 1 (after L0): {plan[1]}")
            >>> print(f"Total levels: {len(plan)}")

            Output:
            Level 0 (parallel): ['assertion_a', 'assertion_b', 'judge_x']
            Level 1 (after L0): ['judge_y', 'assertion_c']
            Total levels: 2
        """

    def print_execution_plan(self) -> None:
        """Print the execution plan for all tasks."""

    def __str__(self) -> str:
        """String representation of GenAIEvalProfile.

        Returns:
            str: Human-readable string showing config and task counts.
        """

    def model_dump_json(self) -> str:
        """Serialize profile to JSON string.

        Returns:
            str: JSON string representation of the profile including config,
                tasks, workflow (if present), and metadata.

        Example:
            >>> json_str = profile.model_dump_json()
            >>> # Save to file, send to API, etc.
        """

    def model_dump(self) -> Dict[str, Any]:
        """Serialize profile to dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation of the profile.

        Example:
            >>> data = profile.model_dump()
            >>> print(data["config"]["space"])
            >>> print(f"Task count: {len(data['assertion_tasks'])}")
        """

    def save_to_json(self, path: Optional[Path] = None) -> Path:
        """Save profile to JSON file.

        Args:
            path (Optional[Path]):
                Optional path to save the profile. If None, saves to
                "genai_eval_profile.json" in the current directory.

        Returns:
            Path: Path where the profile was saved.

        Example:
            >>> path = profile.save_to_json(Path("my_profile.json"))
            >>> print(f"Saved to: {path}")
        """

    @staticmethod
    def model_validate(data: Dict[str, Any]) -> "GenAIEvalProfile":
        """Load profile from dictionary.

        Args:
            data (Dict[str, Any]):
                Dictionary representation of the profile.

        Returns:
            GenAIEvalProfile: Reconstructed profile instance.

        Raises:
            ProfileError: If dictionary structure is invalid or missing required fields.

        Example:
            >>> data = {"config": {...}, "assertion_tasks": [...]}
            >>> profile = GenAIEvalProfile.model_validate(data)
        """

    @staticmethod
    def model_validate_json(json_string: str) -> "GenAIEvalProfile":
        """Load profile from JSON string.

        Args:
            json_string (str):
                JSON string representation of the profile.

        Returns:
            GenAIEvalProfile: Reconstructed profile instance.

        Raises:
            ProfileError: If JSON is malformed or invalid.

        Example:
            >>> json_str = '{"config": {...}, "assertion_tasks": [...]}'
            >>> profile = GenAIEvalProfile.model_validate_json(json_str)
        """

    @staticmethod
    def from_file(path: Path) -> "GenAIEvalProfile":
        """Load profile from JSON file.

        Args:
            path (Path):
                Path to the JSON file containing the profile.

        Returns:
            GenAIEvalProfile: Loaded profile instance.

        Raises:
            ProfileError: If file doesn't exist, is malformed, or invalid.

        Example:
            >>> profile = GenAIEvalProfile.from_file(Path("my_profile.json"))
        """

    def update_config_args(
        self,
        space: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
        uid: Optional[str] = None,
        alert_config: Optional[GenAIAlertConfig] = None,
    ) -> None:
        """Update profile configuration in-place.

        Modifies the profile's config without recreating the entire profile.
        Useful for adjusting space/name/version after initial creation or
        updating alert settings.

        Args:
            space (Optional[str]):
                New model space. If None, keeps existing value.
            name (Optional[str]):
                New model name. If None, keeps existing value.
            version (Optional[str]):
                New model version. If None, keeps existing value.
            uid (Optional[str]):
                New unique identifier. If None, keeps existing value.
            alert_config (Optional[GenAIAlertConfig]):
                New alert configuration. If None, keeps existing value.

        Example:
            >>> profile.update_config_args(
            ...     space="production",
            ...     alert_config=GenAIAlertConfig(schedule="0 */6 * * *")
            ... )
        """

class Drifter:
    def __init__(self) -> None:
        """Instantiate Rust Drifter class that is
        used to create monitoring profiles and compute drifts.
        """

    @overload
    def create_drift_profile(
        self,
        data: Any,
        config: SpcDriftConfig,
        data_type: Optional[ScouterDataType] = None,
    ) -> SpcDriftProfile:
        """Create a SPC (Statistical process control) drift profile from the provided data.

        Args:
            data:
                Data to create a data profile from. Data can be a numpy array,
                a polars dataframe or a pandas dataframe.

                **Data is expected to not contain any missing values, NaNs or infinities**

            config:
                SpcDriftConfig
            data_type:
                Optional data type. Inferred from data if not provided.

        Returns:
            SpcDriftProfile
        """

    @overload
    def create_drift_profile(
        self,
        data: Any,
        data_type: Optional[ScouterDataType] = None,
    ) -> SpcDriftProfile:
        """Create a SPC (Statistical process control) drift profile from the provided data.

        Args:
            data:
                Data to create a data profile from. Data can be a numpy array,
                a polars dataframe or a pandas dataframe.

                **Data is expected to not contain any missing values, NaNs or infinities**

            config:
                SpcDriftConfig
            data_type:
                Optional data type. Inferred from data if not provided.

        Returns:
            SpcDriftProfile
        """

    @overload
    def create_drift_profile(
        self,
        data: Any,
        config: PsiDriftConfig,
        data_type: Optional[ScouterDataType] = None,
    ) -> PsiDriftProfile:
        """Create a PSI (population stability index) drift profile from the provided data.

        Args:
            data:
                Data to create a data profile from. Data can be a numpy array,
                a polars dataframe or a pandas dataframe.

                **Data is expected to not contain any missing values, NaNs or infinities**

            config:
                PsiDriftConfig
            data_type:
                Optional data type. Inferred from data if not provided.

        Returns:
            PsiDriftProfile
        """

    @overload
    def create_drift_profile(
        self,
        data: Union[CustomMetric, List[CustomMetric]],
        config: CustomMetricDriftConfig,
        data_type: Optional[ScouterDataType] = None,
    ) -> CustomDriftProfile:
        """Create a custom drift profile from data.

        Args:
            data:
                CustomMetric or list of CustomMetric.
            config:
                CustomMetricDriftConfig
            data_type:
                Optional data type. Inferred from data if not provided.

        Returns:
            CustomDriftProfile
        """

    def create_drift_profile(  # type: ignore
        self,
        data: Any,
        config: Optional[Union[SpcDriftConfig, PsiDriftConfig, CustomMetricDriftConfig]] = None,
        data_type: Optional[ScouterDataType] = None,
    ) -> Union[SpcDriftProfile, PsiDriftProfile, CustomDriftProfile]:
        """Create a drift profile from data.

        Args:
            data:
                Data to create a data profile from. Data can be a numpy array,
                a polars dataframe, pandas dataframe or a list of CustomMetric if creating
                a custom metric profile.

                **Data is expected to not contain any missing values, NaNs or infinities**

            config:
                Drift config that will be used for monitoring
            data_type:
                Optional data type. Inferred from data if not provided.

        Returns:
            SpcDriftProfile, PsiDriftProfile or CustomDriftProfile
        """

    def create_genai_drift_profile(
        self, config: GenAIEvalConfig, tasks: Sequence[LLMJudgeTask | AssertionTask | TraceAssertionTask]
    ) -> GenAIEvalProfile:
        """Initialize a GenAIEvalProfile for LLM evaluation and drift detection.

        LLM evaluations are run asynchronously on the scouter server.

        Overview:
            GenAI evaluations are defined using assertion tasks and LLM judge tasks.
            Assertion tasks evaluate specific metrics based on model responses, and do not require
            the use of an LLM judge or extra call. It is recommended to use assertion tasks whenever possible
            to reduce cost and latency. LLM judge tasks leverage an additional LLM call to evaluate
            model responses based on more complex criteria. Together, these tasks provide a flexible framework
            for monitoring LLM performance and detecting drift over time.


        Args:
            config (GenAIEvalConfig):
                The configuration for the GenAI drift profile containing space, name,
                version, and alert settings.
            tasks (List[LLMJudgeTask | AssertionTask]):
                List of evaluation tasks to include in the profile. Can contain
                both AssertionTask and LLMJudgeTask instances. At least one task
                (assertion or LLM judge) is required.

        Returns:
            GenAIEvalProfile: Configured profile ready for GenAI drift monitoring.

        Raises:
            ProfileError: If workflow validation fails, metrics are empty when no
                workflow is provided, or if workflow tasks don't match metric names.

        Examples:
            Basic usage with metrics only:

            >>> config = GenAIEvalConfig("my_space", "my_model", "1.0")
            >>>  tasks = [
            ...     LLMJudgeTask(
            ...         id="response_relevance",
            ...         prompt=relevance_prompt,
            ...         expected_value=7,
            ...         field_path="score",
            ...         operator=ComparisonOperator.GreaterThanOrEqual,
            ...         description="Ensure relevance score >= 7"
            ...     )
            ... ]
            >>> profile = Drifter().create_genai_drift_profile(config, tasks)

        """

    @overload
    def compute_drift(
        self,
        data: Any,
        drift_profile: SpcDriftProfile,
        data_type: Optional[ScouterDataType] = None,
    ) -> SpcDriftMap:
        """Create a drift map from data.

        Args:
            data:
                Data to create a data profile from. Data can be a numpy array,
                a polars dataframe or a pandas dataframe.
            drift_profile:
                Drift profile to use to compute drift map
            data_type:
                Optional data type. Inferred from data if not provided.

        Returns:
            SpcDriftMap
        """

    @overload
    def compute_drift(
        self,
        data: Any,
        drift_profile: PsiDriftProfile,
        data_type: Optional[ScouterDataType] = None,
    ) -> PsiDriftMap:
        """Create a drift map from data.

        Args:
            data:
                Data to create a data profile from. Data can be a numpy array,
                a polars dataframe or a pandas dataframe.
            drift_profile:
                Drift profile to use to compute drift map
            data_type:
                Optional data type. Inferred from data if not provided.

        Returns:
            PsiDriftMap
        """

    @overload
    def compute_drift(
        self,
        data: List[GenAIEvalRecord],
        drift_profile: GenAIEvalProfile,
        data_type: Optional[ScouterDataType] = None,
    ) -> "GenAIEvalResultSet":
        """Create a drift map from data.

        Args:
            data (List[GenAIEvalRecord]):
                Data to create a data profile from. Data can be a list of GenAIEvalRecord.
            profile (GenAIEvalProfile):
                Drift profile to use to compute drift map
            data_type:
                Optional data type. Inferred from data if not provided.

        Returns:
            GenAIEvalResultSet
        """

    def compute_drift(  # type: ignore
        self,
        data: Any,
        drift_profile: Union[SpcDriftProfile, PsiDriftProfile, GenAIEvalProfile],
        data_type: Optional[ScouterDataType] = None,
    ) -> Union[SpcDriftMap, PsiDriftMap, GenAIEvalResultSet]:
        """Create a drift map from data.

        Args:
            data:
                Data to create a data profile from. Data can be a numpy array,
                a polars dataframe or a pandas dataframe.
            drift_profile:
                Drift profile to use to compute drift map
            data_type:
                Optional data type. Inferred from data if not provided.

        Returns:
            SpcDriftMap, PsiDriftMap or GenAIEvalResultSet
        """

class GenAIEvalTaskResult:
    """Individual task result from an LLM evaluation run"""

    @property
    def created_at(self) -> datetime.datetime:
        """Get the creation timestamp of this task result"""

    @property
    def record_uid(self) -> str:
        """Get the unique identifier for the record associated with this task result"""

    @property
    def task_id(self) -> str:
        """Get the unique identifier for the evaluation task"""

    @property
    def task_type(self) -> EvaluationTaskType:
        """Get the type of evaluation task (Assertion, LLMJudge, or HumanValidation)"""

    @property
    def passed(self) -> bool:
        """Check if the task evaluation passed"""

    @property
    def value(self) -> float:
        """Get the evaluated value from the task"""

    @property
    def field_path(self) -> Optional[str]:
        """Get the field path used for value extraction, if any"""

    @property
    def operator(self) -> ComparisonOperator:
        """Get the comparison operator used in the evaluation"""

    @property
    def expected(self) -> Any:
        """Get the expected value for comparison.

        Returns:
            The expected value as a Python object (deserialized from JSON).
        """

    @property
    def actual(self) -> Any:
        """Get the actual value that was evaluated.

        Returns:
            The actual value as a Python object (deserialized from JSON).
        """

    @property
    def message(self) -> str:
        """Get the evaluation result message"""

    def __str__(self) -> str:
        """String representation of the task result"""

    def model_dump_json(self) -> str:
        """Serialize the task result to JSON string"""

class GenAIEvalDataset:
    """Defines the dataset used for LLM evaluation"""

    def __init__(
        self,
        records: Sequence[GenAIEvalRecord],
        tasks: Sequence[LLMJudgeTask | AssertionTask],
    ):
        """Initialize the GenAIEvalDataset with records and tasks.

        Args:
            records (List[GenAIEvalRecord]):
                List of LLM evaluation records to be evaluated.
            tasks (List[LLMJudgeTask | AssertionTask]):
                List of evaluation tasks to apply to the records.
        """

    @property
    def records(self) -> List[GenAIEvalRecord]:
        """Get the list of LLM evaluation records in this dataset"""

    @property
    def llm_judge_tasks(self) -> List[LLMJudgeTask]:
        """Get the list of LLM judge tasks in this dataset"""

    @property
    def assertion_tasks(self) -> List[AssertionTask]:
        """Get the list of assertion tasks in this dataset"""

    def evaluate(
        self,
        config: Optional[EvaluationConfig] = None,
    ) -> "GenAIEvalResults":
        """Evaluate the records using the defined tasks.

        Args:
            config (Optional[EvaluationConfig]):
                Optional configuration for the evaluation process.

        Returns:
            GenAIEvalResults:
                The results of the evaluation.
        """

    def print_execution_plan(self) -> None:
        """Print the execution plan for all tasks in the dataset."""

    def with_updated_contexts_by_id(
        self,
        updated_contexts: Dict[str, Any],
    ) -> "GenAIEvalDataset":
        """Create a new GenAIEvalDataset with updated contexts for specific records.

        Example:
            >>> updated_contexts = {
            ...     "record_1_uid": {"new_field": "new_value"},
            ...     "record_2_uid": {"another_field": 123}
            ... }
            >>> new_dataset = dataset.with_updated_contexts_by_id(updated_contexts)
        Args:
            updated_contexts (Dict[str, Any]):
                A dictionary mapping record UIDs to their new context data.
        Returns:
            GenAIEvalDataset:
                A new dataset instance with the updated contexts.
        """

class GenAIEvalSet:
    """Evaluation set for a specific evaluation run"""

    @property
    def records(self) -> List[GenAIEvalTaskResult]:
        """Get the list of task results in this evaluation set"""

    @property
    def created_at(self) -> datetime.datetime:
        """Get the creation timestamp of this evaluation set"""

    @property
    def record_uid(self) -> str:
        """Get the unique identifier for the records in this evaluation set"""

    @property
    def total_tasks(self) -> int:
        """Get the total number of tasks evaluated in this set"""

    @property
    def passed_tasks(self) -> int:
        """Get the number of tasks that passed in this evaluation set"""

    @property
    def failed_tasks(self) -> int:
        """Get the number of tasks that failed in this evaluation set"""

    @property
    def pass_rate(self) -> float:
        """Get the pass rate (percentage of passed tasks) in this evaluation set"""

    @property
    def duration_ms(self) -> int:
        """Get the duration of the evaluation set in milliseconds"""

    def as_table(self, show_tasks: bool = False) -> str:
        """Pretty print the evaluation workflow or task results as a table

        Args:
            show_tasks (bool):
                Whether to show individual task results or just the summary. Default is False
                meaning only the workflow summary is shown.
        """

    def __str__(self): ...

class GenAIEvalResultSet:
    """Defines the results of a specific evaluation run"""

    @property
    def records(self) -> List[GenAIEvalSet]:
        """Get the list of evaluation sets in this result set"""

class AlignedEvalResult:
    """Eval Result for a specific evaluation"""

    @property
    def record_uid(self) -> str:
        """Get the unique identifier for the record associated with this result"""

    @property
    def eval_set(self) -> GenAIEvalSet:
        """Get the eval results"""

    @property
    def embedding(self) -> Dict[str, List[float]]:
        """Get embeddings of embedding targets"""

    @property
    def mean_embeddings(self) -> Dict[str, float]:
        """Get mean embeddings of embedding targets"""

    @property
    def similarity_scores(self) -> Dict[str, float]:
        """Get similarity scores of embedding targets"""

    @property
    def success(self) -> bool:
        """Check if the evaluation was successful"""

    @property
    def error_message(self) -> Optional[str]:
        """Get the error message if the evaluation failed"""

    @property
    def task_count(self) -> int:
        """Get the total number of tasks in the evaluation"""

class MissingTask:
    """Represents a task that exists in only one of the compared evaluations"""

    @property
    def task_id(self) -> str:
        """Get the task identifier"""

    @property
    def present_in(self) -> str:
        """Get which evaluation contains this task ('baseline_only' or 'comparison_only')"""

class TaskComparison:
    """Represents a comparison between the same task in baseline and comparison evaluations"""

    @property
    def task_id(self) -> str:
        """Get the task identifier"""

    @property
    def baseline_passed(self) -> bool:
        """Check if the task passed in the baseline evaluation"""

    @property
    def comparison_passed(self) -> bool:
        """Check if the task passed in the comparison evaluation"""

    @property
    def status_changed(self) -> bool:
        """Check if the task's pass/fail status changed between evaluations"""

    @property
    def record_uid(self) -> str:
        """Get the record unique identifier associated with this task comparison"""

class WorkflowComparison:
    """Represents a comparison between matching workflows in baseline and comparison evaluations"""

    @property
    def baseline_uid(self) -> str:
        """Get the baseline workflow unique identifier"""

    @property
    def comparison_uid(self) -> str:
        """Get the comparison workflow unique identifier"""

    @property
    def baseline_pass_rate(self) -> float:
        """Get the baseline workflow pass rate (0.0 to 1.0)"""

    @property
    def comparison_pass_rate(self) -> float:
        """Get the comparison workflow pass rate (0.0 to 1.0)"""

    @property
    def pass_rate_delta(self) -> float:
        """Get the change in pass rate (positive = improvement, negative = regression)"""

    @property
    def is_regression(self) -> bool:
        """Check if this workflow shows a significant regression"""

    @property
    def task_comparisons(self) -> List[TaskComparison]:
        """Get detailed task-by-task comparisons for this workflow"""

class ComparisonResults:
    """Results from comparing two GenAIEvalResults evaluations"""

    @property
    def workflow_comparisons(self) -> List[WorkflowComparison]:
        """Get all workflow-level comparisons"""

    @property
    def total_workflows(self) -> int:
        """Get the total number of workflows compared"""

    @property
    def improved_workflows(self) -> int:
        """Get the count of workflows that improved"""

    @property
    def regressed_workflows(self) -> int:
        """Get the count of workflows that regressed"""

    @property
    def unchanged_workflows(self) -> int:
        """Get the count of workflows with no significant change"""

    @property
    def mean_pass_rate_delta(self) -> float:
        """Get the mean change in pass rate across all workflows"""

    @property
    def task_status_changes(self) -> List[TaskComparison]:
        """Get all tasks where pass/fail status changed"""

    @property
    def missing_tasks(self) -> List[MissingTask]:
        """Get all tasks present in only one evaluation"""

    @property
    def baseline_workflow_count(self) -> int:
        """Get the number of workflows in the baseline evaluation"""

    @property
    def comparison_workflow_count(self) -> int:
        """Get the number of workflows in the comparison evaluation"""

    @property
    def has_missing_tasks(self) -> bool:
        """Check if there are any missing tasks between evaluations"""

    def __str__(self) -> str:
        """String representation of the comparison results"""

    @property
    def regressed(self) -> bool:
        """Check if any workflows regressed in the comparison"""

    def print_missing_tasks(self) -> None:
        """Print a formatted list of missing tasks to the console"""

    def print_task_aggregate_table(self) -> None:
        """Print a formatted table of task status changes to the console"""

    def print_summary_table(self) -> None:
        """Print a formatted summary table of workflow comparisons to the console"""

    def print_status_changes_table(self) -> None:
        """Print a formatted table of task status changes to the console"""

    def print_summary_stats(self) -> None:
        """Print summary statistics of the comparison results to the console"""

    def as_table(self) -> None:
        """Print comparison results as formatted tables to the console.

        Displays:
        - Workflow-level summary table
        - Task status changes table (if any)
        - Missing tasks list (if any)
        """

class GenAIEvalResults:
    """Defines the results of an LLM eval metric"""

    def __getitem__(self, key: str) -> AlignedEvalResult:
        """Get the task results for a specific record ID. A RuntimeError will be raised if the record ID does not exist."""

    @property
    def errored_tasks(self) -> List[str]:
        """Get a list of record IDs that had errors during evaluation"""

    @property
    def histograms(self) -> Optional[Dict[str, Histogram]]:
        """Get histograms for all calculated features (metrics, embeddings, similarities)"""

    @property
    def successful_count(self) -> int:
        """Get the count of successful evaluations"""

    @property
    def failed_count(self) -> int:
        """Get the count of failed evaluations"""

    def __str__(self):
        """String representation of the GenAIEvalResults"""

    def to_dataframe(self, polars: bool = False) -> Any:
        """
        Convert the results to a Pandas or Polars DataFrame.

        Args:
            polars (bool):
                Whether to return a Polars DataFrame. If False, a Pandas DataFrame will be returned.

        Returns:
            DataFrame:
                A Pandas or Polars DataFrame containing the results.
        """

    def model_dump_json(self) -> str:
        """Dump the results as a JSON string"""

    @staticmethod
    def model_validate_json(json_string: str) -> "GenAIEvalResults":
        """Validate and create an GenAIEvalResults instance from a JSON string

        Args:
            json_string (str):
                JSON string to validate and create the GenAIEvalResults instance from.
        """

    def as_table(self, show_tasks: bool = False) -> str:
        """Pretty print the workflow or task results as a table

        Args:
            show_tasks (bool):
                Whether to show individual task results or just the workflow summary. Default is False
                meaning only the workflow summary is shown.

        """

    def compare_to(self, baseline: "GenAIEvalResults", regression_threshold: float) -> ComparisonResults:
        """Compare the current evaluation results to a baseline with a regression threshold.

        Args:
            baseline (GenAIEvalResults):
                The baseline evaluation results to compare against.
            regression_threshold (float):
                The threshold for considering a regression significant.

        Returns:
            ComparisonResults
        """

class EvaluationConfig:
    """Configuration options for LLM evaluation."""

    def __init__(
        self,
        embedder: Optional[Embedder] = None,
        embedding_targets: Optional[List[str]] = None,
        compute_similarity: bool = False,
        compute_histograms: bool = False,
    ):
        """
        Initialize the EvaluationConfig with optional parameters.

        Args:
            embedder (Optional[Embedder]):
                Optional Embedder instance to use for generating embeddings for similarity-based metrics.
                If not provided, no embeddings will be generated.
            embedding_targets (Optional[List[str]]):
                Optional list of context keys to generate embeddings for. If not provided, embeddings will
                be generated for all string fields in the record context.
            compute_similarity (bool):
                Whether to compute similarity between embeddings. Default is False.
            compute_histograms (bool):
                Whether to compute histograms for all calculated features (metrics, embeddings, similarities).
                Default is False.
        """

########
# __scouter.profile__
########

class Distinct:
    @property
    def count(self) -> int:
        """total unique value counts"""

    @property
    def percent(self) -> float:
        """percent value uniqueness"""

class Quantiles:
    @property
    def q25(self) -> float:
        """25th quantile"""

    @property
    def q50(self) -> float:
        """50th quantile"""

    @property
    def q75(self) -> float:
        """75th quantile"""

    @property
    def q99(self) -> float:
        """99th quantile"""

class Histogram:
    @property
    def bins(self) -> List[float]:
        """Bin values"""

    @property
    def bin_counts(self) -> List[int]:
        """Bin counts"""

class NumericStats:
    @property
    def mean(self) -> float:
        """Return the mean."""

    @property
    def stddev(self) -> float:
        """Return the stddev."""

    @property
    def min(self) -> float:
        """Return the min."""

    @property
    def max(self) -> float:
        """Return the max."""

    @property
    def distinct(self) -> Distinct:
        """Distinct value counts"""

    @property
    def quantiles(self) -> Quantiles:
        """Value quantiles"""

    @property
    def histogram(self) -> Histogram:
        """Value histograms"""

class CharStats:
    @property
    def min_length(self) -> int:
        """Minimum string length"""

    @property
    def max_length(self) -> int:
        """Maximum string length"""

    @property
    def median_length(self) -> int:
        """Median string length"""

    @property
    def mean_length(self) -> float:
        """Mean string length"""

class WordStats:
    @property
    def words(self) -> Dict[str, Distinct]:
        """Distinct word counts"""

class StringStats:
    @property
    def distinct(self) -> Distinct:
        """Distinct value counts"""

    @property
    def char_stats(self) -> CharStats:
        """Character statistics"""

    @property
    def word_stats(self) -> WordStats:
        """word statistics"""

class FeatureProfile:
    @property
    def id(self) -> str:
        """Return the id."""

    @property
    def numeric_stats(self) -> Optional[NumericStats]:
        """Return the numeric stats."""

    @property
    def string_stats(self) -> Optional[StringStats]:
        """Return the string stats."""

    @property
    def timestamp(self) -> str:
        """Return the timestamp."""

    @property
    def correlations(self) -> Optional[Dict[str, float]]:
        """Feature correlation values"""

    def __str__(self) -> str:
        """Return the string representation of the feature profile."""

class DataProfile:
    """Data profile of features"""

    @property
    def features(self) -> Dict[str, FeatureProfile]:
        """Returns dictionary of features and their data profiles"""

    def __str__(self) -> str:
        """Return string representation of the data profile"""

    def model_dump_json(self) -> str:
        """Return json representation of data profile"""

    @staticmethod
    def model_validate_json(json_string: str) -> "DataProfile":
        """Load Data profile from json

        Args:
            json_string:
                JSON string representation of the data profile
        """

    def save_to_json(self, path: Optional[Path] = None) -> Path:
        """Save data profile to json file

        Args:
            path:
                Optional path to save the data profile. If None, outputs to `data_profile.json`

        Returns:
            Path to the saved data profile

        """

class DataProfiler:
    def __init__(self):
        """Instantiate DataProfiler class that is
        used to profile data"""

    def create_data_profile(
        self,
        data: Any,
        data_type: Optional[ScouterDataType] = None,
        bin_size: int = 20,
        compute_correlations: bool = False,
    ) -> DataProfile:
        """Create a data profile from data.

        Args:
            data:
                Data to create a data profile from. Data can be a numpy array,
                a polars dataframe or pandas dataframe.

                **Data is expected to not contain any missing values, NaNs or infinities**

                These types are incompatible with computing
                quantiles, histograms, and correlations. These values must be removed or imputed.

            data_type:
                Optional data type. Inferred from data if not provided.
            bin_size:
                Optional bin size for histograms. Defaults to 20 bins.
            compute_correlations:
                Whether to compute correlations or not.

        Returns:
            DataProfile
        """

    class TraceMetricsRequest:
        """Request to get trace metrics from the Scouter server."""

        def __init__(
            self,
            service_name: str,
            start_time: datetime.datetime,
            end_time: datetime.datetime,
            bucket_interval: str,
        ):
            """
            Initialize a TraceMetricsRequest.

            Args:
                service_name (str):
                    The name of the service to query metrics for.
                start_time (datetime):
                    The start time for the metrics query.
                end_time (datetime):
                    The end time for the metrics query.
                bucket_interval (str):
                    Optional interval for aggregating metrics (e.g., "1m", "5m").
            """

### GLOBAL EXPORTS ###
__all__ = [
    "ActiveSpan",
    "Agent",
    "AgentResponse",
    "AggregationType",
    "Alert",
    "AlertCondition",
    "AlertDispatchType",
    "AlertThreshold",
    "AlertZone",
    "AlignedEvalResult",
    "AllowedTools",
    "AllowedToolsMode",
    "Annotations",
    "AnthropicMessageResponse",
    "AnthropicSettings",
    "AnthropicThinkingConfig",
    "AnthropicTool",
    "AnthropicToolChoice",
    "AnthropicUsage",
    "ApiKeyConfig",
    "ApiSpecType",
    "AssertionResult",
    "AssertionResults",
    "AssertionTask",
    "Attribute",
    "Audio",
    "AudioParam",
    "AuthConfig",
    "AuthConfigValue",
    "AuthType",
    "AutoRoutingMode",
    "Base64ImageSource",
    "Base64PDFSource",
    "BatchConfig",
    "Behavior",
    "BinnedMetric",
    "BinnedMetricStats",
    "BinnedMetrics",
    "BinnedPsiFeatureMetrics",
    "BinnedPsiMetric",
    "BinnedSpcFeatureMetrics",
    "Blob",
    "BlockedReason",
    "CacheControl",
    "Candidate",
    "CharStats",
    "ChatCompletionMessage",
    "ChatMessage",
    "Choice",
    "Citation",
    "CitationCharLocation",
    "CitationCharLocationParam",
    "CitationContentBlockLocation",
    "CitationContentBlockLocationParam",
    "CitationMetadata",
    "CitationPageLocation",
    "CitationPageLocationParam",
    "CitationSearchResultLocationParam",
    "CitationWebSearchResultLocationParam",
    "CitationsConfigParams",
    "CitationsSearchResultLocation",
    "CitationsWebSearchResultLocation",
    "CodeExecution",
    "CodeExecutionResult",
    "CommonCrons",
    "ComparisonOperator",
    "CompletionTokenDetails",
    "ComputerUse",
    "ComputerUseEnvironment",
    "ConsoleDispatchConfig",
    "Content",
    "ContentEmbedding",
    "CustomChoice",
    "CustomDefinition",
    "CustomDriftProfile",
    "CustomMetric",
    "CustomMetricAlertConfig",
    "CustomMetricDriftConfig",
    "CustomMetricRecord",
    "CustomTool",
    "CustomToolChoice",
    "CustomToolFormat",
    "DataProfile",
    "DataProfiler",
    "DataStoreSpec",
    "Distinct",
    "Doane",
    "DocumentBlockParam",
    "DriftAlertPaginationRequest",
    "DriftAlertPaginationResponse",
    "DriftRequest",
    "DriftType",
    "Drifter",
    "DynamicRetrievalConfig",
    "DynamicRetrievalMode",
    "ElasticSearchParams",
    "Embedder",
    "EmbeddingObject",
    "EmbeddingTaskType",
    "EnterpriseWebSearch",
    "EntityType",
    "EqualWidthBinning",
    "EvaluationConfig",
    "EvaluationTaskType",
    "EventDetails",
    "ExecutableCode",
    "ExternalApi",
    "FeatureMap",
    "FeatureProfile",
    "Features",
    "File",
    "FileContentPart",
    "FileData",
    "FileSearch",
    "Filter",
    "FinishReason",
    "FreedmanDiaconis",
    "Function",
    "FunctionCall",
    "FunctionCallingConfig",
    "FunctionChoice",
    "FunctionDeclaration",
    "FunctionDefinition",
    "FunctionResponse",
    "FunctionTool",
    "FunctionToolChoice",
    "FunctionType",
    "GeminiContent",
    "GeminiEmbeddingConfig",
    "GeminiEmbeddingResponse",
    "GeminiSettings",
    "GeminiThinkingConfig",
    "GeminiTool",
    "GenAIAlertConfig",
    "GenAIEvalConfig",
    "GenAIEvalDataset",
    "GenAIEvalProfile",
    "GenAIEvalRecord",
    "GenAIEvalResultSet",
    "GenAIEvalResults",
    "GenAIEvalSet",
    "GenAIEvalTaskResult",
    "GenerateContentResponse",
    "GenerationConfig",
    "GetProfileRequest",
    "GoogleDate",
    "GoogleMaps",
    "GoogleSearch",
    "GoogleSearchNum",
    "GoogleSearchRetrieval",
    "GoogleServiceAccountConfig",
    "Grammar",
    "GrammarFormat",
    "GroundingChunk",
    "GroundingChunkType",
    "GroundingMetadata",
    "GroundingSupport",
    "GrpcConfig",
    "GrpcSpanExporter",
    "HarmBlockMethod",
    "HarmBlockThreshold",
    "HarmCategory",
    "HarmProbability",
    "HarmSeverity",
    "Histogram",
    "HttpBasicAuthConfig",
    "HttpConfig",
    "HttpElementLocation",
    "HttpSpanExporter",
    "ImageBlockParam",
    "ImageConfig",
    "ImageContentPart",
    "ImageUrl",
    "InnerAllowedTools",
    "InputAudioContentPart",
    "InputAudioData",
    "Interval",
    "KafkaConfig",
    "LLMJudgeTask",
    "Language",
    "LatLng",
    "LlmRanker",
    "LogContent",
    "LogLevel",
    "LogProbs",
    "LoggingConfig",
    "LogprobsCandidate",
    "LogprobsResult",
    "Manual",
    "ManualRoutingMode",
    "Maps",
    "MediaResolution",
    "MessageParam",
    "Metadata",
    "Metric",
    "Metrics",
    "Modality",
    "ModalityTokenCount",
    "Mode",
    "ModelArmorConfig",
    "ModelRoutingPreference",
    "ModelSettings",
    "MultiSpeakerVoiceConfig",
    "NumericStats",
    "OauthConfig",
    "OauthConfigValue",
    "OidcConfig",
    "OpenAIChatResponse",
    "OpenAIChatSettings",
    "OpenAIEmbeddingConfig",
    "OpenAIEmbeddingResponse",
    "OpenAITool",
    "OpenAIToolChoice",
    "OpsGenieDispatchConfig",
    "OtelExportConfig",
    "OtelProtocol",
    "Outcome",
    "PageSpan",
    "ParallelAiSearch",
    "Part",
    "PartMetadata",
    "PartialArgs",
    "PhishBlockThreshold",
    "PlainTextSource",
    "PrebuiltVoiceConfig",
    "PredictRequest",
    "PredictResponse",
    "Prediction",
    "PredictionContentPart",
    "ProfileStatusRequest",
    "Prompt",
    "PromptFeedback",
    "PromptTokenDetails",
    "Provider",
    "PsiAlertConfig",
    "PsiChiSquareThreshold",
    "PsiDriftConfig",
    "PsiDriftMap",
    "PsiDriftProfile",
    "PsiFixedThreshold",
    "PsiNormalThreshold",
    "PsiRecord",
    "QuantileBinning",
    "Quantiles",
    "Queue",
    "QueueFeature",
    "RabbitMQConfig",
    "RagChunk",
    "RagResource",
    "RagRetrievalConfig",
    "RankService",
    "Ranking",
    "RankingConfig",
    "RecordType",
    "RedactedThinkingBlock",
    "RedactedThinkingBlockParam",
    "RedisConfig",
    "ResponseType",
    "Retrieval",
    "RetrievalConfig",
    "RetrievalMetadata",
    "RetrievalSource",
    "RetrievedContext",
    "Rice",
    "Role",
    "RoutingConfig",
    "RoutingConfigMode",
    "RustyLogger",
    "SafetyRating",
    "SafetySetting",
    "Schema",
    "SchemaType",
    "Score",
    "Scott",
    "ScouterClient",
    "ScouterDataType",
    "ScouterQueue",
    "SearchEntryPoint",
    "SearchResultBlockParam",
    "Segment",
    "ServerRecord",
    "ServerRecords",
    "ServerToolUseBlock",
    "ServerToolUseBlockParam",
    "SimpleSearchParams",
    "SlackDispatchConfig",
    "SourceFlaggingUri",
    "SpanEvent",
    "SpanFilter",
    "SpanKind",
    "SpanLink",
    "SpanStatus",
    "SpcAlert",
    "SpcAlertConfig",
    "SpcAlertRule",
    "SpcAlertType",
    "SpcDriftConfig",
    "SpcDriftFeature",
    "SpcDriftMap",
    "SpcDriftProfile",
    "SpcFeatureDrift",
    "SpcFeatureDriftProfile",
    "SpcRecord",
    "SpeakerVoiceConfig",
    "SpeechConfig",
    "SquareRoot",
    "StdoutSpanExporter",
    "StopReason",
    "StreamOptions",
    "StringStats",
    "Sturges",
    "SystemPrompt",
    "TagRecord",
    "TagsResponse",
    "Task",
    "TaskEvent",
    "TaskList",
    "TaskStatus",
    "TerrellScott",
    "TestSpanExporter",
    "TextBlock",
    "TextBlockParam",
    "TextContentPart",
    "TextFormat",
    "ThinkingBlock",
    "ThinkingBlockParam",
    "ThinkingLevel",
    "TimeInterval",
    "ToolCall",
    "ToolChoiceMode",
    "ToolConfig",
    "ToolDefinition",
    "ToolResultBlockParam",
    "ToolUseBlock",
    "ToolUseBlockParam",
    "TopCandidates",
    "TopLogProbs",
    "TraceAssertion",
    "TraceAssertionTask",
    "TraceBaggageRecord",
    "TraceBaggageResponse",
    "TraceFilters",
    "TraceListItem",
    "TraceMetricBucket",
    "TraceMetricsRequest",
    "TraceMetricsResponse",
    "TracePaginationResponse",
    "TraceRecord",
    "TraceSpan",
    "TraceSpanRecord",
    "TraceSpansResponse",
    "TrafficType",
    "UrlCitation",
    "UrlContext",
    "UrlContextMetadata",
    "UrlImageSource",
    "UrlMetadata",
    "UrlPDFSource",
    "UrlRetrievalStatus",
    "Usage",
    "UsageMetadata",
    "UsageObject",
    "VertexAISearch",
    "VertexGoogleSearch",
    "VertexRagStore",
    "VideoMetadata",
    "VoiceConfig",
    "Web",
    "WebSearchResultBlock",
    "WebSearchResultBlockParam",
    "WebSearchToolResultBlock",
    "WebSearchToolResultBlockParam",
    "WebSearchToolResultError",
    "WordStats",
    "Workflow",
    "WorkflowResult",
    "WorkflowTask",
    "WriteLevel",
    "flush_tracer",
    "init_tracer",
    "shutdown_tracer",
]
