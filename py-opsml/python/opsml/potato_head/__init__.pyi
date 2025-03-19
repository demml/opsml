# pylint: disable=redefined-builtin, invalid-name, dangerous-default-value

from enum import IntEnum
from typing import List, Optional, Literal, Sequence

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

class Message:
    @property
    def content(self) -> str | ImageUrl | AudioUrl | BinaryContent | DocumentUrl:
        """The content of the message"""

    @property
    def sanitized_output(self) -> Optional[SanitizedResult]:
        """The sanitized content of the message"""

    def bind(self, context: str) -> "Message":
        """Bind a context in the prompt. This is an immutable operation meaning that it
        will return a new Message object with the context bound.

            Example with ChatPrompt that contains two messages

            ```python
                chat_prompt = Prompt("gpt-3.5-turbo", [
                    Message("system", "Hello, $1"),
                    Message("user", "World")
                ])
                chat_prompt[0].bind("world") # we bind "world" to the first message
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

        Args:
            config (SanitizationConfig):
                The sanitization configuration to use.

        Returns:
            Message:
                The sanitized message.
        """

class ImageUrl:
    def __init__(self, url: str, kind: Literal["image-url"] = "image-url") -> None:
        """Create an ImageUrl object.

        Args:
            url (str):
                The URL of the image.
            kind (Literal["image-url"]):
                The kind of the content.
        """

    @property
    def media_type(self) -> str:
        """The media type of the image URL."""

    @property
    def format(self) -> str:
        """The format of the image URL."""

class AudioUrl:
    def __init__(self, url: str, kind: Literal["audio-url"] = "audio-url") -> None:
        """Create an AudioUrl object.

        Args:
            url (str):
                The URL of the audio.
            kind (Literal["audio-url"]):
                The kind of the content.
        """

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
    def media_type(self) -> str:
        """The media type of the document URL."""

    @property
    def format(self) -> str:
        """The format of the document URL."""

class Prompt:
    def __init__(
        self,
        model: str,
        prompt: str | Sequence[str | ImageUrl | AudioUrl | BinaryContent | DocumentUrl],
        system_prompt: Optional[str | List[str]] = None,
        sanitization_config: Optional[SanitizationConfig] = None,
    ) -> None:
        """Prompt for interacting with an LLM API.

        Args:
            model (str):
                The model to use for the prompt.
            prompt (Any):
                The prompt to use in the prompt.
            system_prompt (Optional[str, Sequence[str]]):
                The system prompt to use in the prompt.
            sanitization_config (None):
                The santization configuration to use for the prompt.
                Defaults to None which means no santization will be performed.
        """

    @property
    def model(self) -> str:
        """The model to use for the prompt."""

    @property
    def prompt(
        self,
    ) -> str | List[str | ImageUrl | AudioUrl | BinaryContent | DocumentUrl]:
        """The user prompt to use in the prompt."""

    @property
    def system_prompt(self) -> List[str]:
        """The system prompt to use in the prompt."""

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
