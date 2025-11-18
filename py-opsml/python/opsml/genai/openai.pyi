# pylint: disable=redefined-builtin
from typing import Any, Dict, List, Optional

class AudioParam:
    def __init__(self, format: str, voice: str) -> None: ...
    @property
    def format(self) -> str: ...
    @property
    def voice(self) -> str: ...

class ContentPart:
    def __init__(self, type: str, text: str) -> None: ...
    @property
    def type(self) -> str: ...
    @property
    def text(self) -> str: ...

class Content:
    def __init__(
        self,
        text: Optional[str] = None,
        parts: Optional[List[ContentPart]] = None,
    ) -> None: ...

class Prediction:
    def __init__(self, type: str, content: Content) -> None: ...
    @property
    def type(self) -> str: ...
    @property
    def content(self) -> Content: ...

class StreamOptions:
    def __init__(
        self,
        include_obfuscation: Optional[bool] = None,
        include_usage: Optional[bool] = None,
    ) -> None: ...
    @property
    def include_obfuscation(self) -> Optional[bool]: ...
    @property
    def include_usage(self) -> Optional[bool]: ...

class ToolChoiceMode:
    NA: "ToolChoiceMode"
    Auto: "ToolChoiceMode"
    Required: "ToolChoiceMode"

class FunctionChoice:
    def __init__(self, name: str) -> None: ...
    @property
    def name(self) -> str: ...

class FunctionToolChoice:
    def __init__(self, function: FunctionChoice) -> None: ...
    @property
    def function(self) -> FunctionChoice: ...
    @property
    def type(self) -> str: ...

class CustomChoice:
    def __init__(self, name: str) -> None: ...
    @property
    def name(self) -> str: ...

class CustomToolChoice:
    def __init__(self, custom: CustomChoice) -> None: ...
    @property
    def custom(self) -> CustomChoice: ...
    @property
    def type(self) -> str: ...

class ToolDefinition:
    def __init__(self, function_name: str) -> None: ...
    @property
    def function_name(self) -> str: ...
    @property
    def type(self) -> str: ...

class AllowedToolsMode:
    Auto: "AllowedToolsMode"
    Required: "AllowedToolsMode"

class InnerAllowedTools:
    @property
    def mode(self) -> AllowedToolsMode: ...
    @property
    def tools(self) -> List[ToolDefinition]: ...

class AllowedTools:
    def __init__(self, mode: AllowedToolsMode, tools: List[ToolDefinition]) -> None: ...
    @property
    def type(self) -> str: ...
    @property
    def allowed_tools(self) -> InnerAllowedTools: ...

class ToolChoice:
    Mode: "ToolChoice"
    Function: "ToolChoice"
    Custom: "ToolChoice"
    Allowed: "ToolChoice"

    @staticmethod
    def from_mode(mode: AllowedToolsMode) -> "ToolChoice": ...
    @staticmethod
    def from_function(function_name: str) -> "ToolChoice": ...
    @staticmethod
    def from_custom(custom_name: str) -> "ToolChoice": ...
    @staticmethod
    def from_allowed_tools(allowed_tools: AllowedTools) -> "ToolChoice": ...

class FunctionDefinition:
    def __init__(
        self,
        name: str,
        description: Optional[str] = None,
        parameters: Optional[dict] = None,
        strict: Optional[bool] = None,
    ) -> None: ...
    @property
    def name(self) -> str: ...
    @property
    def description(self) -> Optional[str]: ...
    @property
    def parameters(self) -> Optional[dict]: ...
    @property
    def strict(self) -> Optional[bool]: ...

class FunctionTool:
    def __init__(self, function: FunctionDefinition, type: str) -> None: ...
    @property
    def function(self) -> FunctionDefinition: ...
    @property
    def type(self) -> str: ...

class TextFormat:
    def __init__(self, type: str) -> None: ...
    @property
    def type(self) -> str: ...

class Grammar:
    def __init__(self, definition: str, syntax: str) -> None: ...
    @property
    def definition(self) -> str: ...
    @property
    def syntax(self) -> str: ...

class GrammarFormat:
    def __init__(self, grammar: Grammar, type: str) -> None: ...
    @property
    def type(self) -> str: ...
    @property
    def grammar(self) -> Grammar: ...

class CustomToolFormat:
    def __init__(
        self,
        type: Optional[str] = None,
        grammar: Optional[Grammar] = None,
    ) -> None: ...

class CustomDefinition:
    def __init__(
        self,
        name: str,
        description: Optional[str] = None,
        format: Optional[CustomToolFormat] = None,
    ) -> None: ...
    @property
    def name(self) -> str: ...
    @property
    def description(self) -> Optional[str]: ...
    @property
    def format(self) -> Optional[CustomToolFormat]: ...

class CustomTool:
    def __init__(self, custom: CustomDefinition, type: str) -> None: ...

class Tool:
    def __init__(
        self,
        function: Optional[FunctionTool] = None,
        custom: Optional[CustomTool] = None,
    ) -> None: ...

class OpenAIChatSettings:
    """OpenAI chat completion settings configuration.

    This class provides configuration options for OpenAI chat completions,
    including model parameters, tool usage, and request options.

    Examples:
        >>> settings = OpenAIChatSettings(
        ...     temperature=0.7,
        ...     max_completion_tokens=1000,
        ...     stream=True
        ... )
        >>> settings.temperature = 0.5
    """

    def __init__(
        self,
        *,
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
        tool_choice: Optional[ToolChoice] = None,
        tools: Optional[List[Tool]] = None,
        top_logprobs: Optional[int] = None,
        verbosity: Optional[str] = None,
        extra_body: Optional[Any] = None,
    ) -> None:
        """Initialize OpenAI chat settings.

        Args:
            max_completion_tokens (Optional[int]):
                Maximum number of tokens to generate
            temperature (Optional[float]):
                Sampling temperature (0.0 to 2.0)
            top_p (Optional[float]):
                Nucleus sampling parameter
            top_k (Optional[int]):
                Top-k sampling parameter
            frequency_penalty (Optional[float]):
                Frequency penalty (-2.0 to 2.0)
            timeout (Optional[float]):
                Request timeout in seconds
            parallel_tool_calls (Optional[bool]):
                Whether to enable parallel tool calls
            seed (Optional[int]):
                Random seed for deterministic outputs
            logit_bias (Optional[Dict[str, int]]):
                Token bias modifications
            stop_sequences (Optional[List[str]]):
                Sequences where generation should stop
            logprobs (Optional[bool]):
                Whether to return log probabilities
            audio (Optional[AudioParam]):
                Audio generation parameters
            metadata (Optional[Dict[str, str]]):
                Additional metadata for the request
            modalities (Optional[List[str]]):
                List of modalities to use
            n (Optional[int]):
                Number of completions to generate
            prediction (Optional[Prediction]):
                Prediction configuration
            presence_penalty (Optional[float]):
                Presence penalty (-2.0 to 2.0)
            prompt_cache_key (Optional[str]):
                Key for prompt caching
            reasoning_effort (Optional[str]):
                Reasoning effort level
            safety_identifier (Optional[str]):
                Safety configuration identifier
            service_tier (Optional[str]):
                Service tier to use
            store (Optional[bool]):
                Whether to store the conversation
            stream (Optional[bool]):
                Whether to stream the response
            stream_options (Optional[StreamOptions]):
                Streaming configuration options
            tool_choice (Optional[ToolChoice]):
                Tool choice configuration
            tools (Optional[List[Tool]]):
                Available tools for the model
            top_logprobs (Optional[int]):
                Number of top log probabilities to return
            verbosity (Optional[str]):
                Verbosity level for the response
            extra_body (Optional[Any]):
                Additional request body parameters
        """

    def __str__(self) -> str:
        """Return string representation of the settings."""
