# pylint: disable=redefined-builtin
from typing import Any, Dict, List, Optional, Union
from pathlib import Path

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
        **kwargs,
    ) -> None:
        """ChatPrompt for interacting with an LLM Chat API.


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

        Args:
            model (str):
                The model to use for the chat prompt.
            messages (List[Message | Dict[str, Any]]):
                The messages to use in the chat prompt.
            kwargs:
                Additional data to pass to the API data field.
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
