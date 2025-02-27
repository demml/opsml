# type: ignore

from typing import Any, Iterator, Optional, overload
from ..openai import ChatCompletionChunk, OpenAIConfig
from ..prompts import ChatPrompt

class OpenAIResponse: ...
class AnthropicResponse: ...

class StreamResponse:
    def __iter__(self) -> Any: ...
    def __next__(self) -> Any: ...

class Mouth:
    def __init__(self, config: OpenAIConfig) -> None:
        """Mouth class to interact with API Clients

        Args:
            config (OpenAIConfig):
                The configuration to use for the mouth.
        """

    @overload
    def speak(
        self,
        request: ChatPrompt,
        response_format: Optional[Any] = None,
    ) -> OpenAIResponse: ...
    @overload
    def speak(
        self,
        request: ChatPrompt,
        response_format: Optional[Any] = None,
    ) -> AnthropicResponse: ...
    def speak(
        self,
        request: ChatPrompt,
        response_format: Optional[Any] = None,
    ) -> OpenAIResponse | AnthropicResponse:
        """Speak to the API.

        Args:
            request (ChatPrompt):
                The request to send to the API.
            response_format (Optional[Any]):
                The response format to use for the chat prompt. This
                is for structured responses and will be parsed accordingly.
                If provided, must be a subclass of pydantic
                `BaseModel`.

        Returns:
            The response from the API.
        """

    @overload
    def speak_stream(
        self,
        request: ChatPrompt,
    ) -> Iterator[ChatCompletionChunk]: ...
    @overload
    def speak_stream(
        self,
        request: ChatPrompt,
    ) -> Iterator[ChatCompletionChunk]: ...
    def speak_stream(
        self,
        request: ChatPrompt,
    ) -> Iterator[ChatCompletionChunk]:
        """Stream message from API.

        Args:
            request (ChatPrompt):
                The request to send to the API.

        Returns:
            `StreamResponse` object
        """
