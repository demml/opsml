# pylint: disable=redefined-builtin, invalid-name, dangerous-default-value

from enum import IntEnum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

class PromptType:
    Image: "PromptType"
    Chat: "PromptType"
    Vision: "PromptType"
    Voice: "PromptType"
    Batch: "PromptType"
    Embedding: "PromptType"

class ChatPartText:
    text: str
    type: str

    def __init__(self, text: str, type: str = "text") -> None:
        """Text content for a chat prompt.

        Args:
            text (str):
                The text content.
            type (str):
                The type of the content
        """

class ImageUrl:
    url: str
    detail: str

    def __init__(self, url: str, detail: str = "auto") -> None:
        """Either a URL of the image or the base64 encoded image data.

        Args:
            url (str):
                The URL of the image.
            detail (str):
                Specifies the detail level of the image.
        """

class ChatPartImage:
    image_url: ImageUrl
    type: str

    def __init__(self, image_url: ImageUrl, type: str = "image_url") -> None:
        """Image content for a chat prompt.

        Args:
            image_url (ImageUrl):
                The image URL.
            type (str):
                The type of the content.
        """

class InputAudio:
    data: str
    format: str

    def __init__(self, data: str, format: str = "wav") -> None:
        """Base64 encoded audio data.

        Args:
            data (str):
                Base64 encoded audio data.
            format (str):
                The format of the encoded audio data. Currently supports "wav" and "mp3".
        """

class ChatPartAudio:
    input_audio: InputAudio
    type: str

    def __init__(self, input_audio: InputAudio, type: str = "input_audio") -> None:
        """Audio content for a chat prompt.

        Args:
            input_audio (InputAudio):
                The input audio data.
            type (str):
                The type of the content.
        """

ContentType = Union[
    str,
    Dict[str, Any],
    ChatPartAudio,
    ChatPartImage,
    ChatPartText,
    List[ChatPartText | ChatPartImage | ChatPartAudio],
]

class Message:
    def __init__(
        self,
        role: str,
        content: ContentType,
        name: Optional[str] = None,
    ) -> None:
        """Message class to represent a message in a chat prompt.
        Messages can be parameterized with numbered arguments in the form of
        $1, $2, $3, etc. These arguments will be replaced with the corresponding context
        when bound.

        Example:
        ```python
            message = Message("system", "Params: $1, $2")
            message.bind("world")
            message.bind("hello")



        ```

        Args:
            role (str)
                The role to assign the message. Refer to the
                specific model's documentation for possible roles.
            content (
                str |
                Dict |
                ChatPartAudio |
                ChatPartImage |
                ChatPartText |
                List[
                    ChatPartText |
                    ChatPartImage |
                    ChatPartAudio
                    ]
                    ):
                The content of the message.
            name (Optional[str]):
                An optional name for the participant.
        """

    @property
    def role(self) -> str:
        """The role of the message."""

    @property
    def content(self) -> str:
        """The content of the message."""

class ChatPrompt:
    def __init__(
        self,
        model: str,
        messages: List[Message | Dict[str, Any]],
        sanitization_config: Optional[SanitizationConfig] = None,
        **kwargs,
    ) -> None:
        """ChatPrompt for interacting with an LLM Chat API.

        Args:
            model (str):
                The model to use for the chat prompt.
            messages (List[Message | Dict[str, Any]]):
                The messages to use in the chat prompt.
            sanitization_config (Optional[SanitizationConfig]):
                The sanitization configuration to use for the chat prompt.
                Defaults to None which means no sanitization will be performed.
            **kwargs:
                Additional model-specific parameters passed to the API. Common options include:

                - temperature (float):
                    Sampling temperature (0.0-2.0). Lower values make responses more deterministic.
                - top_p (float):
                    Nucleus sampling parameter (0.0-1.0).
                - n (int):
                    Number of completions to generate.
                - stream (bool):
                    Whether to stream responses.
                - logprobs (bool):
                    Whether to return log probabilities.
                - top_logprobs (int):
                    Number of most likely tokens to return log probabilities for.
                - max_tokens (int):
                    Maximum number of tokens to generate.


        Example:
        ```python
            ChatPrompt(
                model="gpt-4o",
                messages=[
                    {"role": "developer", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Hello!"},
                ],
                logprobs=True,
                top_logprobs=2,
            )


            ChatPrompt(
                model="gpt-4o",
                messages=[
                    Message("developer", "You are a helpful assistant."),
                ],
                logprobs=True,
                top_logprobs=2,
            )
        ```

        """

    @property
    def model(self) -> str:
        """The model to use for the chat prompt."""

    @property
    def messages(self) -> List[Message]:
        """The messages to use in the chat prompt."""

    @property
    def prompt_type(self) -> PromptType:
        """The prompt type to use for the chat prompt."""

    @property
    def sanitization_config(self) -> Optional[SanitizationConfig]:
        """The sanitization configuration to use for the chat prompt."""

    @property
    def sanitized_results(self) -> List[SanitizationResult]:
        """The results of the sanitization attempt."""

    @property
    def has_sanitize_error(self) -> bool:
        """Whether the prompt has sanitization errors."""

    @property
    def additional_data(self) -> Optional[str]:
        """Additional data as it will be passed to the API data field."""

    def add_message(self, message: Message) -> None:
        """Add a message to the chat prompt.

        Args:
            message (Message):
                The message to add to the chat prompt.
        """

    def bind_context_at(self, context: str, index: int = 0) -> None:
        """Bind a context at a specific index in the chat prompt.
        If a `SanitizationConfig` is provided, the context will be sanitized
        prior to being bound. Any `SanitizationResult` will be stored in the
        sanitized_results property and if the risk threshold has been passed
        `has_sanitize_error` will be set to True.

            Example with ChatPrompt that contains two messages

            ```python
                chat_prompt = ChatPrompt("gpt-3.5-turbo", [
                    Message("system", "Hello, $1"),
                    Message("user", "World")
                ])
                chat_prompt.bind_context_at(0, "world") # we bind "world" to the first message
            ```

        Args:
            context (str):
                The context to bind.
            index (int):
                The index to bind the context at. Index refers
                to the index of the array in which the context will be bound.
                Defaults to 0.
        """

    def deep_copy(self) -> "ChatPrompt":
        """Return a copy of the chat prompt."""

    def reset(self) -> None:
        """Reset the chat prompt to its initial state."""

    def __str__(self) -> str:
        """Return a string representation of the chat prompt."""

    def open_ai_spec(self) -> str:
        """OpenAI spec for the chat prompt. How it will be sent to the API.
        This is intended for debugging purposes. There is a equivalent method in
        rust that will return the same spec when used with a `Tongue` for fast processing.
        """

    def to_open_ai_request(self) -> Dict[str, Any]:
        """Convert the chat prompt to an OpenAI request that can be passed to the
        OpenAI client sdk.
        """

    def model_dump_json(self) -> str:
        """Dump the model to a JSON string."""

    @staticmethod
    def model_validate_json(json_string: str) -> "ChatPrompt":
        """Load a `ChatPrompt` from a JSON string."""

    def save_prompt(self, path: Optional[Path] = None) -> Path:
        """Save the chat prompt to a file.

        Args:
            path (Optional[Path]):
                The path to save the chat prompt to. If not provided,
                defaults to "prompt_{utc_datetime}.json".
        """

    def load_from_path(self, path: Path) -> "ChatPrompt":
        """Load a `ChatPrompt` from a file.

        Args:
            path (Path):
                The path to the chat prompt file.
        """

class RiskLevel(IntEnum):
    """Risk level of a potential prompt injection attempt"""

    Safe = 0  # No risk detected
    Low = 1  # Low risk, minor concerns
    Medium = 2  # Medium risk, potential concerns
    High = 3  # High risk, likely prompt injection attempt
    Critical = 4  # Critical risk, almost certainly a prompt injection attempt

class SanitizationConfig:
    def __init__(
        self,
        risk_threshold: RiskLevel = RiskLevel.High,
        sanitize: bool = True,
        check_delimiters: bool = True,
        check_keywords: bool = True,
        check_control_chars: bool = True,
        custom_patterns: Optional[List[str]] = [],
        error_on_high_risk: bool = True,
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
            custom_patterns (List[str]):
                Custom patterns to use for the sanitization. These will be read as
                regular expressions.
            error_on_high_risk (bool):
                Whether to raise an error on high risk.
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

class SanitizationResult:
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
