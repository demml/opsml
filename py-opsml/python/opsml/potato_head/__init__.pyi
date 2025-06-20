# pylint: disable=redefined-builtin, invalid-name, dangerous-default-value

from enum import IntEnum
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Sequence

class RiskLevel(IntEnum):
    """Risk level of a potential prompt injection attempt"""

    Safe = 0  # No risk detected
    Low = 1  # Low risk, minor concerns
    Medium = 2  # Medium risk, potential concerns
    High = 3  # High risk, likely prompt injection attempt
    Critical = 4  # Critical risk, almost certainly a prompt injection attempt

class PIIConfig:
    def __init__(
        self,
        check_email: bool = True,
        check_phone: bool = True,
        check_credit_card: bool = True,
        check_ssn: bool = True,
        check_ip: bool = True,
        check_password: bool = True,
        check_address: bool = True,
        check_name: bool = True,
        check_dob: bool = True,
        custom_pii_patterns: List[str] = [],
    ) -> None:
        """PIIConfig for configuring the sanitization of a chat prompt.

        Args:
            check_email (bool):
                Whether to check for email addresses in the chat prompt.
            check_phone (bool):
                Whether to check for phone numbers in the chat prompt.
            check_credit_card (bool):
                Whether to check for credit card numbers in the chat prompt.
            check_ssn (bool):
                Whether to check for social security numbers in the chat prompt.
            check_ip (bool):
                Whether to check for IP addresses in the chat prompt.
            check_password (bool):
                Whether to check for passwords in the chat prompt.
            check_address (bool):
                Whether to check for addresses in the chat prompt.
            check_name (bool):
                Whether to check for names in the chat prompt.
            check_dob (bool):
                Whether to check for dates of birth in the chat prompt.
            custom_pii_patterns (List[str]):
                Custom patterns to use for the PII checks. These will be read as
                regular expressions.
        """

class SanitizationConfig:
    def __init__(
        self,
        risk_threshold: RiskLevel = RiskLevel.High,
        sanitize: bool = True,
        check_delimiters: bool = True,
        check_keywords: bool = True,
        check_control_chars: bool = True,
        check_pii: bool = True,
        custom_patterns: Optional[List[str]] = [],
        error_on_high_risk: bool = True,
        pii_config: Optional[PIIConfig] = None,
    ) -> None:
        """SanitizationConfig for configuring the sanitization of a chat prompt.

        Args:
            risk_threshold (RiskLevel):
                The risk threshold to use for the sanitization.
            sanitize (bool):
                Whether to sanitize the chat prompt or just assess risk. Both
                will return a sanitization result. Sanitize will return the input text
                with identified risks masked.
            check_delimiters (bool):
                Whether to check for delimiters in the chat prompt.
            check_keywords (bool):
                Whether to check for keywords in the chat prompt.
            check_control_chars (bool):
                Whether to check for control characters in the chat prompt.
            check_pii (bool):
                Whether to check for PII in the chat prompt
            custom_patterns (List[str]):
                Custom patterns to use for the sanitization. These will be read as
                regular expressions.
            error_on_high_risk (bool):
                Whether to raise an error on high risk.
            pii_config (Optional[PIIConfig]):
                The PII configuration to use for the sanitization.
        """

    @property
    def risk_threshold(self) -> RiskLevel:
        """The risk threshold to use for the sanitization."""

    @property
    def check_delimiters(self) -> bool:
        """Whether to check for delimiters in the chat prompt."""

    @property
    def check_keywords(self) -> bool:
        """Whether to check for keywords in the chat prompt."""

    @property
    def check_control_chars(self) -> bool:
        """Whether to check for control characters in the chat prompt."""

    @property
    def custom_patterns(self) -> List[str]:
        """Custom patterns to use for the sanitization."""

    @property
    def sanitize(self) -> bool:
        """Whether to sanitize the chat prompt or just assess risk."""

    @property
    def error_on_high_risk(self) -> bool:
        """Whether to raise an error on high risk."""

    @error_on_high_risk.setter
    def error_on_high_risk(self, value: bool) -> None:
        """Set the error_on_high_risk property."""

    @staticmethod
    def strict() -> "SanitizationConfig":
        """A strict sanitization (sanitize=True) configuration with all checks enabled
        and a risk_threshold of Low."""

    @staticmethod
    def standard() -> "SanitizationConfig":
        """A standard sanitization (sanitize=True) configuration with all checks enabled
        and a risk_threshold of High."""

    @staticmethod
    def permissive() -> "SanitizationConfig":
        """A permissive sanitization (sanitize=True) configuration with keyword and
        control_chars enabled and a Critical risk threshold set"""

class SanitizedResult:
    """Class to represent the result of a sanitization attempt"""

    @property
    def sanitized_text(self) -> str:
        """The sanitized text"""

    @property
    def risk_level(self) -> RiskLevel:
        """The risk level of the sanitization attempt"""

    @property
    def detected_issues(self) -> List[str]:
        """The detected issues in the sanitization attempt"""

    def __str__(self): ...

class PromptSanitizer:
    def __init__(self, config: SanitizationConfig) -> None:
        """Create a PromptSanitizer object.

        Args:
            config (SanitizationConfig):
                The sanitization configuration to use.
        """

    def sanitize(self, text: str) -> SanitizedResult:
        """Sanitize the text.

        Args:
            text (str):
                The text to sanitize.

        Returns:
            SanitizedResult:
                The sanitized result.
        """

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

    @property
    def sanitized_output(self) -> Optional[SanitizedResult]:
        """The sanitized content of the message"""

    def bind(self, context: str) -> "Message":
        """Bind a context in the prompt. This is an immutable operation meaning that it
        will return a new Message object with the context bound.

            Example with Prompt that contains two messages

            ```python
                prompt = Prompt(
                    model="openai:gpt-4o",
                    user_message=[
                        "My prompt $1 is $2",
                        "My prompt $3 is $4",
                    ],
                    system_message="system_prompt",
                )
                bounded_prompt = prompt.user_message[0].bind("world").unwrap() # we bind "world" to the first message
            ```

        Args:
            context (str):
                The context to bind.

        Returns:
            Message:
                The message with the context bound.
        """

    def sanitize(self, sanitizer: PromptSanitizer) -> "Message":
        """Sanitize the message content.

        Example with Prompt that contains two messages

            ```python
                prompt = Prompt(
                    model="openai:gpt-4o",
                    user_message=[
                        "My prompt $1 is $2",
                        "My prompt $3 is $4",
                    ],
                    system_message="system_prompt",
                )

                # sanitize the first message
                # Note: sanitization will fail if no sanitizer is provided (either through prompt.sanitizer or standalone)

                # we bind "world" to the first message
                bounded_prompt = prompt.user_message[0].bind("world").sanitize(prompt.sanitizer).unwrap()
            ```

        Args:
            sanitizer (PromptSanitizer):
                The sanitizer to use for sanitizing the message

        Returns:
            Message:
                The sanitized message.
        """

    def unwrap(self) -> Any:
        """Unwrap the message content.

        Returns:
            str:
                The message content.
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
        model: str,
        provider: str,
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
        extra_body: Optional[dict[str, Any]] = None,
    ) -> None:
        """ModelSettings for configuring the model.

        Args:
            model (str):
                The model to use.
            provider (str):
                The provider to use.
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
        user_message: str | Sequence[str | ImageUrl | AudioUrl | BinaryContent | DocumentUrl] | Message | List[Message],
        model: Optional[str] = None,
        provider: Optional[str] = None,
        system_message: Optional[str | List[str]] = None,
        sanitization_config: Optional[SanitizationConfig] = None,
        model_settings: Optional[ModelSettings] = None,
    ) -> None:
        """Prompt for interacting with an LLM API.

        Args:
            user_message (str | Sequence[str | ImageUrl | AudioUrl | BinaryContent | DocumentUrl] | Message | List[Message]):
                The prompt to use.
            model (str | None):
                The model to use for the prompt. Required if model_settings is not provided.
            provider (str | None):
                The provider to use for the prompt. Required if model_settings is not provided.
            system_message (Optional[str | List[str]]):
                The system prompt to use in the prompt.
            sanitization_config (None):
                The santization configuration to use for the prompt.
                Defaults to None which means no sanitization will be done
            model_settings (None):
                The model settings to use for the prompt.
                Defaults to None which means no model settings will be used
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
                    user_message="My prompt $1 is $2",
                    system_message="system_message",
                    provider="openai",
                )
                agent = Agent(
                    prompt.model_identifier, # "openai:gpt-4o"
                    system_messages=prompt.system_message[0].unwrap(),
                )
            ```
        """

    @property
    def model_settings(self) -> ModelSettings:
        """The model settings to use for the prompt."""

    @property
    def sanitizer(self) -> PromptSanitizer:
        """The prompt sanitizer to use for the prompt."""

    @property
    def user_message(
        self,
    ) -> List[Message]:
        """The user message to use in the prompt."""

    @property
    def system_message(self) -> List[Message]:
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

    def __str__(self): ...

class Provider:
    OpenAI: "Provider"

class TaskStatus:
    Pending: "TaskStatus"
    Running: "TaskStatus"
    Completed: "TaskStatus"
    Failed: "TaskStatus"

class AgentResponse:
    @property
    def id(self) -> str:
        """The ID of the agent response."""

    @property
    def output(self) -> str:
        """The output of the agent response."""

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
    def __init__(self, provider: Provider | str) -> None:
        """Create an Agent object.

        Args:
            provider (Provider | str):
                The provider to use for the agent. This can be a Provider enum or a string
                representing the provider.
        """

    def execute_task(
        self,
        task: Task,
        context_messages: Dict[str, List[Message]],
    ) -> AgentResponse:
        """Execute a task.

        Args:
            task (Task):
                The task to execute.
            context_messages (Dict[str, List[Message]]):
                The context messages to use for the task. This is a dictionary where the keys
                are the task IDs and the values are lists of messages that will be used as context
                for the task.

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
    def id(self) -> str:
        """The ID of the workflow. This is a random uuid7 that is generated when the workflow is created."""

    @property
    def name(self) -> str:
        """The name of the workflow."""

    @property
    def tasks(self) -> List[Task]:
        """The tasks in the workflow."""

    @property
    def agents(self) -> Dict[str, Agent]:
        """The agents in the workflow."""

    def add_task(self, task: Task) -> None:
        """Add a task to the workflow.

        Args:
            task (Task):
                The task to add to the workflow.
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
        return sum(1 for task in self.tasks if task.status == TaskStatus.Pending)

    def execution_plan(self) -> Dict[str, List[str]]:
        """Get the execution plan for the workflow.

        Returns:
            Dict[str, List[str]]:
                A dictionary where the keys are task IDs and the values are lists of task IDs
                that the task depends on.
        """

    def run(self) -> None:
        """Run the workflow. This will execute all tasks in the workflow and return when all tasks are complete."""
