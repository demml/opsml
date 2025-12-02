# python/opsml/_opsml.pyi
# pylint: disable=dangerous-default-value,redefined-builtin,missing-param-doc
# type: ignore

# to search for a specific module, search for __<module_name>__ like __opsml.card__
from datetime import datetime, timedelta
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
    TypeAlias,
    TypeVar,
    Union,
    overload,
)

CardInterfaceType: TypeAlias = Union["DataInterface", "ModelInterface"]
ServiceCardInterfaceType: TypeAlias = Dict[
    str, Union["DataInterface", "ModelInterface"]
]
LoadInterfaceType: TypeAlias = Union[ServiceCardInterfaceType, ServiceCardInterfaceType]

P = ParamSpec("P")
R = TypeVar("R")

########################################################################################
#  This section contains the type definitions for opsml.mock module
# __opsml.genai__
# ######################################################################################

class Modality:
    """Represents different modalities for content generation."""

    ModalityUnspecified: "Modality"
    Text: "Modality"
    Image: "Modality"
    Audio: "Modality"

class ThinkingConfig:
    """Configuration for thinking/reasoning capabilities."""

    def __init__(
        self,
        include_thoughts: Optional[bool] = None,
        thinking_budget: Optional[int] = None,
    ) -> None: ...

class MediaResolution:
    """Media resolution settings for content generation."""

    MediaResolutionUnspecified: "MediaResolution"
    MediaResolutionLow: "MediaResolution"
    MediaResolutionMedium: "MediaResolution"
    MediaResolutionHigh: "MediaResolution"

class SpeechConfig:
    """Configuration for speech generation."""

    def __init__(
        self,
        voice_config: Optional["VoiceConfig"] = None,
        language_code: Optional[str] = None,
    ) -> None: ...

class PrebuiltVoiceConfig:
    """Configuration for prebuilt voice models."""

    def __init__(
        self,
        voice_name: str,
    ) -> None: ...

class VoiceConfigMode:
    PrebuiltVoiceConfig: "VoiceConfigMode"

class VoiceConfig:
    """Configuration for voice generation."""

    def __init__(self, voice_config: VoiceConfigMode) -> None: ...

class GenerationConfig:
    """Configuration for content generation with comprehensive parameter control.

    This class provides fine-grained control over the generation process including
    sampling parameters, output format, modalities, and various specialized features.

    Examples:
        Basic usage with temperature control:

        ```python
        GenerationConfig(temperature=0.7, max_output_tokens=1000)
        ```

        Multi-modal configuration:
        ```python
        config = GenerationConfig(
            response_modalities=[Modality.TEXT, Modality.AUDIO],
            speech_config=SpeechConfig(language_code="en-US")
        )
        ```

        Advanced sampling with penalties:
        ```python
        config = GenerationConfig(
            temperature=0.8,
            top_p=0.9,
            top_k=40,
            presence_penalty=0.1,
            frequency_penalty=0.2
        )
        ```
    """

    def __init__(
        self,
        stop_sequences: Optional[List[str]] = None,
        response_mime_type: Optional[str] = None,
        response_modalities: Optional[List[Modality]] = None,
        thinking_config: Optional[ThinkingConfig] = None,
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
    ) -> None:
        """Initialize GenerationConfig with optional parameters.

        Args:
            stop_sequences (Optional[List[str]]):
                List of strings that will stop generation when encountered
            response_mime_type (Optional[str]):
                MIME type for the response format
            response_modalities (Optional[List[Modality]]):
                List of modalities to include in the response
            thinking_config (Optional[ThinkingConfig]):
                Configuration for reasoning/thinking capabilities
            temperature (Optional[float]):
                Controls randomness in generation (0.0-1.0)
            top_p (Optional[float]):
                Nucleus sampling parameter (0.0-1.0)
            top_k (Optional[int]):
                Top-k sampling parameter
            candidate_count (Optional[int]):
                Number of response candidates to generate
            max_output_tokens (Optional[int]):
                Maximum number of tokens to generate
            response_logprobs (Optional[bool]):
                Whether to return log probabilities
            logprobs (Optional[int]):
                Number of log probabilities to return per token
            presence_penalty (Optional[float]):
                Penalty for token presence (-2.0 to 2.0)
            frequency_penalty (Optional[float]):
                Penalty for token frequency (-2.0 to 2.0)
            seed (Optional[int]):
                Random seed for deterministic generation
            audio_timestamp (Optional[bool]):
                Whether to include timestamps in audio responses
            media_resolution (Optional[MediaResolution]):
                Resolution setting for media content
            speech_config (Optional[SpeechConfig]):
                Configuration for speech synthesis
            enable_affective_dialog (Optional[bool]):
                Whether to enable emotional dialog features
        """

    def __str__(self) -> str: ...

class HarmCategory:
    HarmCategoryUnspecified: "HarmCategory"
    HarmCategoryHateSpeech: "HarmCategory"
    HarmCategoryDangerousContent: "HarmCategory"
    HarmCategoryHarassment: "HarmCategory"
    HarmCategorySexuallyExplicit: "HarmCategory"
    HarmCategoryImageHate: "HarmCategory"
    HarmCategoryImageDangerousContent: "HarmCategory"
    HarmCategoryImageHarassment: "HarmCategory"
    HarmCategoryImageSexuallyExplicit: "HarmCategory"

class HarmBlockThreshold:
    HarmBlockThresholdUnspecified: "HarmBlockThreshold"
    BlockLowAndAbove: "HarmBlockThreshold"
    BlockMediumAndAbove: "HarmBlockThreshold"
    BlockOnlyHigh: "HarmBlockThreshold"
    BlockNone: "HarmBlockThreshold"
    Off: "HarmBlockThreshold"

class HarmBlockMethod:
    HarmBlockMethodUnspecified: "HarmBlockMethod"
    Severity: "HarmBlockMethod"
    Probability: "HarmBlockMethod"

class ModelArmorConfig:
    def __init__(
        self,
        prompt_template_name: Optional[str],
        response_template_name: Optional[str],
    ) -> None:
        """
        Args:
            prompt_template_name (Optional[str]):
                The name of the prompt template to use.
            response_template_name (Optional[str]):
                The name of the response template to use.
        """

    @property
    def prompt_template_name(self) -> Optional[str]: ...
    @property
    def response_template_name(self) -> Optional[str]: ...

class SafetySetting:
    category: HarmCategory
    threshold: HarmBlockThreshold
    method: Optional[HarmBlockMethod]

    def __init__(
        self,
        category: HarmCategory,
        threshold: HarmBlockThreshold,
        method: Optional[HarmBlockMethod] = None,
    ) -> None:
        """Initialize SafetySetting with required and optional parameters.

        Args:
            category (HarmCategory):
                The category of harm to protect against.
            threshold (HarmBlockThreshold):
                The threshold for blocking content.
            method (Optional[HarmBlockMethod]):
                The method used for blocking (if any).
        """

class Mode:
    ModeUnspecified: "Mode"
    Any: "Mode"
    Auto: "Mode"
    None_Mode: "Mode"  # type: ignore

class FunctionCallingConfig:
    @property
    def mode(self) -> Optional[Mode]: ...
    @property
    def allowed_function_names(self) -> Optional[list[str]]: ...
    def __init__(
        self, mode: Optional[Mode], allowed_function_names: Optional[list[str]]
    ) -> None: ...

class LatLng:
    @property
    def latitude(self) -> float: ...
    @property
    def longitude(self) -> float: ...
    def __init__(self, latitude: float, longitude: float) -> None:
        """Initialize LatLng with latitude and longitude.

        Args:
            latitude (float):
                The latitude value.
            longitude (float):
                The longitude value.
        """

class RetrievalConfig:
    @property
    def lat_lng(self) -> LatLng: ...
    @property
    def language_code(self) -> str: ...
    def __init__(self, lat_lng: LatLng, language_code: str) -> None:
        """Initialize RetrievalConfig with latitude/longitude and language code.

        Args:
            lat_lng (LatLng):
                The latitude and longitude configuration.
            language_code (str):
                The language code for the retrieval.
        """

class ToolConfig:
    @property
    def function_calling_config(self) -> Optional[FunctionCallingConfig]: ...
    @property
    def retrieval_config(self) -> Optional[RetrievalConfig]: ...
    def __init__(
        self,
        function_calling_config: Optional[FunctionCallingConfig],
        retrieval_config: Optional[RetrievalConfig],
    ) -> None: ...

class GeminiSettings:
    def __init__(
        self,
        labels: Optional[dict[str, str]] = None,
        tool_config: Optional[ToolConfig] = None,
        generation_config: Optional[GenerationConfig] = None,
        safety_settings: Optional[list[SafetySetting]] = None,
        model_armor_config: Optional[ModelArmorConfig] = None,
        extra_body: Optional[dict] = None,
    ) -> None:
        """Settings to pass to the Gemini API when creating a request

        Reference:
            https://cloud.google.com/vertex-ai/generative-ai/docs/reference/rest/v1beta1/projects.locations.endpoints/generateContent

        Args:
            labels (Optional[dict[str, str]]):
                An optional dictionary of labels for the settings.
            tool_config (Optional[ToolConfig]):
                Configuration for tools like function calling and retrieval.
            generation_config (Optional[GenerationConfig]):
                Configuration for content generation parameters.
            safety_settings (Optional[list[SafetySetting]]):
                List of safety settings to apply.
            model_armor_config (Optional[ModelArmorConfig]):
                Configuration for model armor templates.
            extra_body (Optional[dict]):
                Additional configuration as a dictionary.
        """

    @property
    def labels(self) -> Optional[dict[str, str]]: ...
    @property
    def tool_config(self) -> Optional[ToolConfig]: ...
    @property
    def generation_config(self) -> Optional[GenerationConfig]: ...
    @property
    def safety_settings(self) -> Optional[list[SafetySetting]]: ...
    @property
    def model_armor_config(self) -> Optional[ModelArmorConfig]: ...
    @property
    def extra_body(self) -> Optional[dict]: ...
    def __str__(self) -> str: ...

class EmbeddingTaskType:
    TaskTypeUnspecified = "EmbeddingTaskType"
    RetrievalQuery = "EmbeddingTaskType"
    RetrievalDocument = "EmbeddingTaskType"
    SemanticSimilarity = "EmbeddingTaskType"
    Classification = "EmbeddingTaskType"
    Clustering = "EmbeddingTaskType"
    QuestionAnswering = "EmbeddingTaskType"
    FactVerification = "EmbeddingTaskType"
    CodeRetrievalQuery = "EmbeddingTaskType"

class GeminiEmbeddingConfig:
    def __init__(
        self,
        model: Optional[str] = None,
        output_dimensionality: Optional[int] = None,
        task_type: Optional[EmbeddingTaskType | str] = None,
    ) -> None:
        """Configuration to pass to the Gemini Embedding API when creating a request


        Args:
            model (Optional[str]):
                The embedding model to use. If not specified, the default gemini model will be used.
            output_dimensionality (Optional[int]):
                The output dimensionality of the embeddings. If not specified, a default value will be used.
            task_type (Optional[EmbeddingTaskType]):
                The type of embedding task to perform. If not specified, the default gemini task type will be used.
        """

class ContentEmbedding:
    @property
    def values(self) -> List[float]: ...

class GeminiEmbeddingResponse:
    @property
    def embedding(self) -> ContentEmbedding: ...

class PredictResponse:
    @property
    def predictions(self) -> List[dict]: ...
    @property
    def metadata(self) -> Any: ...
    @property
    def deployed_model_id(self) -> str: ...
    @property
    def model(self) -> str: ...
    @property
    def model_version_id(self) -> str: ...
    @property
    def model_display_name(self) -> str: ...
    def __str__(self): ...

class PredictRequest:
    def __init__(
        self, instances: List[dict], parameters: Optional[dict] = None
    ) -> None:
        """Request to pass to the Vertex Predict API when creating a request

        Args:
            instances (List[dict]):
                A list of instances to be sent in the request.
            parameters (Optional[dict]):
                Optional parameters for the request.
        """

    @property
    def instances(self) -> List[dict]: ...
    @property
    def parameters(self) -> dict: ...
    def __str__(self): ...

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

class OpenAIEmbeddingConfig:
    """OpenAI embedding configuration settings."""

    def __init__(
        self,
        model: str,
        dimensions: Optional[int] = None,
        encoding_format: Optional[str] = None,
        user: Optional[str] = None,
    ) -> None:
        """Initialize OpenAI embedding configuration.

        Args:
            model (str):
                The embedding model to use.
            dimensions (Optional[int]):
                The output dimensionality of the embeddings.
            encoding_format (Optional[str]):
                The encoding format to use for the embeddings.
                Can be either "float" or "base64".
            user (Optional[str]):
                The user ID for the embedding request.
        """

    @property
    def model(self) -> str: ...
    @property
    def dimensions(self) -> Optional[int]: ...
    @property
    def encoding_format(self) -> Optional[str]: ...
    @property
    def user(self) -> Optional[str]: ...

class EmbeddingObject:
    @property
    def object(self) -> str: ...
    @property
    def embedding(self) -> List[float]: ...
    @property
    def index(self) -> int: ...

class UsageObject:
    @property
    def prompt_tokens(self) -> int: ...
    @property
    def total_tokens(self) -> int: ...

class OpenAIEmbeddingResponse:
    @property
    def object(self) -> str: ...
    @property
    def data(self) -> List[EmbeddingObject]: ...
    @property
    def usage(self) -> UsageObject: ...

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
    def __init__(
        self, content: str | ImageUrl | AudioUrl | BinaryContent | DocumentUrl
    ) -> None:
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
    def __init__(self, settings: OpenAIChatSettings | GeminiSettings) -> None:
        """ModelSettings for configuring the model.

        Args:
            settings (OpenAIChatSettings | GeminiSettings):
                The settings to use for the model. Currently supports OpenAI and Gemini settings.
        """

    @property
    def settings(self) -> OpenAIChatSettings | GeminiSettings:
        """The settings to use for the model."""

    def model_dump_json(self) -> str:
        """The JSON representation of the model settings."""

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
        model: str,
        provider: Provider | str,
        system_instruction: Optional[str | List[str]] = None,
        model_settings: Optional[
            ModelSettings | OpenAIChatSettings | GeminiSettings
        ] = None,
        response_format: Optional[Any] = None,
    ) -> None:
        """Prompt for interacting with an LLM API.

        Args:
            message (str | Sequence[str | ImageUrl | AudioUrl | BinaryContent | DocumentUrl] | Message | List[Message]):
                The prompt to use.
            model (str):
                The model to use for the prompt
            provider (Provider | str):
                The provider to use for the prompt.
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
    Vertex: "Provider"
    Google: "Provider"

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
        """The result of the agent response. This can be a Pydantic BaseModel class or a supported potato_head response
        type such as `Score`. If neither is provided, the response json will be returned as a dictionary.
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

ConfigT = TypeVar("ConfigT", OpenAIEmbeddingConfig, GeminiEmbeddingConfig, None)

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
    ) -> "WorkflowResult":
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
    def model_validate_json(
        json_string: str, output_types: Optional[Dict[str, Any]]
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
    def duration(self) -> Optional[timedelta]:
        """The duration of the task execution."""

    @property
    def start_time(self) -> Optional[datetime]:
        """The start time of the task execution."""

    @property
    def end_time(self) -> Optional[datetime]:
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
    def timestamp(self) -> datetime:
        """The timestamp of the event. This is the time when the event occurred."""

    @property
    def updated_at(self) -> datetime:
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

########################################################################################
#  This section contains the type definitions for opsml.mock module
# __opsml.mock__
# ######################################################################################

class RegistryTestHelper:
    """Helper class for testing the registry"""

    def __init__(self) -> None: ...
    def setup(self) -> None: ...
    def cleanup(self) -> None: ...

class OpsmlTestServer:
    def __init__(self, cleanup: bool = True, base_path: Optional[Path] = None) -> None:
        """Instantiates the test server.

        When the test server is used as a context manager, it will start the server
        in a background thread and set the appropriate env vars so that the client
        can connect to the server. The server will be stopped when the context manager
        exits and the env vars will be reset.

        Args:
            cleanup (bool, optional):
                Whether to cleanup the server after the test. Defaults to True.
            base_path (Optional[Path], optional):
                The base path for the server. Defaults to None. This is primarily
                used for testing loading attributes from a pyproject.toml file.
        """

    def start_server(self) -> None:
        """Starts the test server."""

    def stop_server(self) -> None:
        """Stops the test server."""

    def __enter__(self) -> "OpsmlTestServer":
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

class OpsmlServerContext:
    def __init__(self) -> None:
        """Instantiates the server context.
        This is helpful when you are running tests in server mode to
        aid in background cleanup of resources
        """

    def __enter__(self) -> "OpsmlServerContext":
        """Starts the server context."""

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """Stops the server context."""

    @property
    def server_uri(self) -> str:
        """Returns the server URI."""

class MockConfig:
    def __init__(self, **kwargs) -> None:
        """Mock configuration for the ScouterQueue

        Args:
            **kwargs: Arbitrary keyword arguments to set as attributes.
        """

class LLMTestServer:
    """
    Mock server for OpenAI API.
    This class is used to simulate the OpenAI API for testing purposes.
    """

    def __init__(self): ...
    def __enter__(self):
        """
        Start the mock server.
        """

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Stop the mock server.
        """

########################################################################################
#  This section contains the type definitions for opsml.logging module
# __opsml.logging__
# ######################################################################################
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

########################################################################################
#  This section contains the type definitions for opsml.scouter module
# __opsml.scouter__

def get_function_type(func: Callable[..., Any]) -> "FunctionType":
    """Determine the function type (sync, async, generator, async generator).

    Args:
        func (Callable[..., Any]):
            The function to analyze.
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

class CompressionType:
    NA: "CompressionType"
    Gzip: "CompressionType"
    Snappy: "CompressionType"
    Lz4: "CompressionType"
    Zstd: "CompressionType"

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
    transport_config: Optional[
        HttpConfig | KafkaConfig | RabbitMQConfig | RedisConfig
    ] = None,
    exporter: HttpSpanExporter
    | StdoutSpanExporter
    | TestSpanExporter = StdoutSpanExporter(),  # noqa: F821
    batch_config: Optional[BatchConfig] = None,
    profile_space: Optional[str] = None,
    profile_name: Optional[str] = None,
    profile_version: Optional[str] = None,
) -> None:
    """Initialize the tracer for a service with specific transport and exporter configurations.

    This function configures a service tracer, allowing for the specification of
    the service name, the transport mechanism for exporting spans, and the chosen
    span exporter.

    Args:
        service_name (str):
            The **required** name of the service this tracer is associated with.
            This is typically a logical identifier for the application or component.
        transport_config (HttpConfig | KafkaConfig | RabbitMQConfig | RedisConfig | None):
            The configuration detailing how spans should be sent out.
            If **None**, a default `HttpConfig` will be used.

            The supported configuration types are:
            * `HttpConfig`: Configuration for exporting via HTTP/gRPC.
            * `KafkaConfig`: Configuration for exporting to a Kafka topic.
            * `RabbitMQConfig`: Configuration for exporting to a RabbitMQ queue.
            * `RedisConfig`: Configuration for exporting to a Redis stream or channel.
        exporter (HttpSpanExporter | StdoutSpanExporter | TestSpanExporter | None):
            The span exporter implementation to use.
            If **None**, a default `StdoutSpanExporter` is used.

            Available exporters:
            * `HttpSpanExporter`: Sends spans to an HTTP endpoint (e.g., an OpenTelemetry collector).
            * `StdoutSpanExporter`: Writes spans directly to standard output for debugging.
            * `TestSpanExporter`: Collects spans in memory, primarily for unit testing.
        batch_config (BatchConfig | None):
            Configuration for the batching process. If provided, spans will be queued
            and exported in batches according to these settings. If `None`, and the
            exporter supports batching, default batch settings will be applied.

    Drift Profile Association (Optional):
        Use these parameters to associate the tracer with a specific drift profile.

        profile_space (str | None):
            The space for the drift profile.
        profile_name (str | None):
            A name of the associated drift profile or service.
        profile_version (str | None):
            The version of the drift profile.
    """

class ActiveSpan:
    """Represents an active tracing span."""

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

    def add_event(self, name: str, attributes: Any) -> None:
        """Add an event to the active span.

        Args:
            name (str):
                The name of the event.
            attributes (Any):
                Optional attributes for the event.
                Can be any serializable type or pydantic `BaseModel`.
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

    def start_as_current_span(
        self,
        name: str,
        kind: Optional[SpanKind] = SpanKind.Internal,
        label: Optional[str] = None,
        attributes: Optional[dict[str, str]] = None,
        baggage: Optional[dict[str, str]] = None,
        tags: Optional[dict[str, str]] = None,
        parent_context_id: Optional[str] = None,
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

class ExportConfig:
    """Configuration for exporting spans."""

    def __init__(
        self,
        endpoint: Optional[str],
        protocol: OtelProtocol = OtelProtocol.HttpBinary,
        timeout: Optional[int] = None,
    ) -> None:
        """Initialize the ExportConfig.

        Args:
            endpoint (Optional[str]):
                The HTTP endpoint for exporting spans.
            protocol (Protocol):
                The protocol to use for exporting spans. Defaults to HttpBinary.
            timeout (Optional[int]):
                The timeout for HTTP requests in seconds.
        """

    @property
    def endpoint(self) -> Optional[str]:
        """Get the HTTP endpoint for exporting spans."""

    @property
    def protocol(self) -> OtelProtocol:
        """Get the protocol used for exporting spans."""

    @property
    def timeout(self) -> Optional[int]:
        """Get the timeout for HTTP requests in seconds."""

class OtelHttpConfig:
    """Configuration for HTTP span exporting."""

    def __init__(
        self,
        headers: Optional[dict[str, str]] = None,
        compression: Optional[CompressionType] = None,
    ) -> None:
        """Initialize the HttpConfig.

        Args:
            headers (Optional[dict[str, str]]):
                Optional HTTP headers to include in requests.
            compression (Optional[CompressionType]):
                Optional compression type for HTTP requests.
        """

    @property
    def headers(self) -> Optional[dict[str, str]]:
        """Get the HTTP headers."""

    @property
    def compression(self) -> Optional[CompressionType]:
        """Get the compression type."""

class HttpSpanExporter:
    """Exporter that sends spans to an HTTP endpoint."""

    def __init__(
        self,
        batch_export: bool = True,
        export_config: Optional[ExportConfig] = None,
        http_config: Optional[OtelHttpConfig] = None,
        sample_ratio: Optional[float] = None,
    ) -> None:
        """Initialize the HttpSpanExporter.

        Args:
            batch_export (bool):
                Whether to use batch exporting. Defaults to True.
            export_config (Optional[ExportConfig]):
                Configuration for exporting spans.
            http_config (Optional[OtelHttpConfig]):
                Configuration for the HTTP exporter.
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

class GrpcConfig:
    """Configuration for gRPC exporting."""

    def __init__(self, compression: Optional[CompressionType] = None) -> None:
        """Initialize the GrpcConfig.

        Args:
            compression (Optional[CompressionType]):
                Optional compression type for gRPC requests.
        """

    @property
    def compression(self) -> Optional[CompressionType]:
        """Get the compression type."""

class GrpcSpanExporter:
    """Exporter that sends spans to a gRPC endpoint."""

    def __init__(
        self,
        batch_export: bool = True,
        export_config: Optional[ExportConfig] = None,
        grpc_config: Optional[GrpcConfig] = None,
        sample_ratio: Optional[float] = None,
    ) -> None:
        """Initialize the GrpcSpanExporter.

        Args:
            batch_export (bool):
                Whether to use batch exporting. Defaults to True.
            export_config (Optional[ExportConfig]):
                Configuration for exporting spans.
            grpc_config (Optional[GrpcConfig]):
                Configuration for the gRPC exporter.
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
    created_at: datetime
    trace_id: str
    space: str
    name: str
    version: str
    scope: str
    trace_state: str
    start_time: datetime
    end_time: datetime
    duration_ms: int
    status: str
    root_span_id: str
    attributes: Optional[dict]

    def get_attributes(self) -> Dict[str, Any]: ...

class TraceSpanRecord:
    created_at: datetime
    span_id: str
    trace_id: str
    parent_span_id: Optional[str]
    space: str
    name: str
    version: str
    scope: str
    span_name: str
    span_kind: str
    start_time: datetime
    end_time: datetime
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

class TagRecord:
    """Represents a single tag record associated with an entity."""

    created_at: datetime
    entity_type: str
    entity_id: str
    key: str
    value: str

class Attribute:
    """Represents a key-value attribute associated with a span."""

    key: str
    value: str

class SpanEvent:
    """Represents an event within a span."""

    timestamp: datetime
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

    created_at: datetime
    trace_id: str
    scope: str
    key: str
    value: str

class TracePaginationResponse:
    """Response structure for paginated trace list requests."""

    items: List["TraceListItem"]

class TraceSpansResponse:
    """Response structure containing a list of spans for a trace."""

    spans: List["TraceSpan"]

class TraceBaggageResponse:
    """Response structure containing trace baggage records."""

    baggage: List[TraceBaggageRecord]

class TraceMetricsRequest:
    """Request payload for fetching trace metrics."""

    space: Optional[str]
    name: Optional[str]
    version: Optional[str]
    start_time: datetime
    end_time: datetime
    bucket_interval: str

    def __init__(
        self,
        start_time: datetime,
        end_time: datetime,
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

class TraceFilters:
    """A struct for filtering traces, generated from Rust pyclass."""

    space: Optional[str]
    name: Optional[str]
    version: Optional[str]
    service_name: Optional[str]
    has_errors: Optional[bool]
    status_code: Optional[int]
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    limit: Optional[int]
    cursor_created_at: Optional[datetime]
    cursor_trace_id: Optional[str]

    def __init__(
        self,
        space: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
        service_name: Optional[str] = None,
        has_errors: Optional[bool] = None,
        status_code: Optional[int] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: Optional[int] = None,
        cursor_created_at: Optional[datetime] = None,
        cursor_trace_id: Optional[str] = None,
    ) -> None:
        """Initialize trace filters.

        Args:
            space:
                Model space filter
            name:
                Model name filter
            version:
                Model version filter
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

    bucket_start: datetime
    trace_count: int
    avg_duration_ms: float
    p50_duration_ms: Optional[float]
    p95_duration_ms: Optional[float]
    p99_duration_ms: Optional[float]
    error_rate: float

class TraceListItem:
    """Represents a summary item for a trace in a list view."""

    trace_id: str
    space: str
    name: str
    version: str
    scope: str
    service_name: Optional[str]
    root_operation: Optional[str]
    start_time: datetime
    end_time: Optional[datetime]
    duration_ms: Optional[int]
    status_code: int
    status_message: Optional[str]
    span_count: Optional[int]
    has_errors: bool
    error_count: int
    created_at: datetime

class TraceSpan:
    """Detailed information for a single span within a trace."""

    trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    span_name: str
    span_kind: Optional[str]
    start_time: datetime
    end_time: Optional[datetime]
    duration_ms: Optional[int]
    status_code: str
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

class TraceMetricsResponse:
    """Response structure containing aggregated trace metrics."""

    metrics: List[TraceMetricBucket]

class TagsResponse:
    """Response structure containing a list of tag records."""

    tags: List[TagRecord]

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

EqualWidthMethods = (
    Manual
    | SquareRoot
    | Sturges
    | Rice
    | Doane
    | Scott
    | TerrellScott
    | FreedmanDiaconis
)

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

class DriftType:
    Spc: "DriftType"
    Psi: "DriftType"
    Custom: "DriftType"
    LLM: "DriftType"

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

DispatchConfigType = (
    ConsoleDispatchConfig | SlackDispatchConfig | OpsGenieDispatchConfig
)

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
        rule: SpcAlertRule = SpcAlertRule(),
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

class CustomMetricAlertCondition:
    def __init__(
        self,
        alert_threshold: AlertThreshold,
        alert_threshold_value: Optional[float],
    ):
        """Initialize a CustomMetricAlertCondition instance.
        Args:
            alert_threshold (AlertThreshold): The condition that determines when an alert
                should be triggered. This could be comparisons like 'greater than',
                'less than', 'equal to', etc.
            alert_threshold_value (Optional[float], optional): A numerical boundary used in
                conjunction with the alert_threshold. This can be None for certain
                types of comparisons that don't require a fixed boundary.
        Example:
            alert_threshold = CustomMetricAlertCondition(AlertCondition.BELOW, 2.0)
        """

    @property
    def alert_threshold(self) -> AlertThreshold:
        """Return the alert_threshold"""

    @alert_threshold.setter
    def alert_threshold(self, alert_threshold: AlertThreshold) -> None:
        """Set the alert_threshold"""

    @property
    def alert_threshold_value(self) -> float:
        """Return the alert_threshold_value"""

    @alert_threshold_value.setter
    def alert_threshold_value(self, alert_threshold_value: float) -> None:
        """Set the alert_threshold_value"""

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
    def alert_conditions(self) -> dict[str, CustomMetricAlertCondition]:
        """Return the alert_condition that were set during metric definition"""

    @alert_conditions.setter
    def alert_conditions(
        self, alert_conditions: dict[str, CustomMetricAlertCondition]
    ) -> None:
        """Update the alert_condition that were set during metric definition"""

class LLMAlertConfig:
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
    def alert_conditions(self) -> Optional[Dict[str, "LLMMetricAlertCondition"]]:
        """Return the alert conditions"""

class LLMMetricAlertCondition:
    def __init__(
        self,
        alert_threshold: AlertThreshold,
        alert_threshold_value: Optional[float],
    ):
        """Initialize a LLMMetricAlertCondition instance.
        Args:
            alert_threshold (AlertThreshold):
                The condition that determines when an alert should be triggered.
                Must be one of the AlertThreshold enum members like Below, Above, or Outside.
            alert_threshold_value (Optional[float], optional):
                A numerical boundary used in conjunction with the alert_threshold.
                This can be None for certain types of comparisons that don't require a fixed boundary.
        Example:
            alert_threshold = LLMMetricAlertCondition(AlertCondition.BELOW, 2.0)
        """

    def __str__(self) -> str:
        """Return the string representation of LLMMetricAlertCondition."""

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

class TimeInterval:
    FiveMinutes: "TimeInterval"
    FifteenMinutes: "TimeInterval"
    ThirtyMinutes: "TimeInterval"
    OneHour: "TimeInterval"
    ThreeHours: "TimeInterval"
    SixHours: "TimeInterval"
    TwelveHours: "TimeInterval"
    TwentyFourHours: "TimeInterval"
    TwoDays: "TimeInterval"
    FiveDays: "TimeInterval"

class DriftRequest:
    def __init__(
        self,
        name: str,
        space: str,
        version: str,
        time_interval: TimeInterval,
        max_data_points: int,
        drift_type: DriftType,
    ) -> None:
        """Initialize drift request

        Args:
            name:
                Model name
            space:
                Model space
            version:
                Model version
            time_interval:
                Time window for drift request
            max_data_points:
                Maximum data points to return
            drift_type:
                Drift type for request
        """

class ProfileStatusRequest:
    def __init__(
        self, name: str, space: str, version: str, drift_type: DriftType, active: bool
    ) -> None:
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
    def __init__(
        self, name: str, space: str, version: str, drift_type: DriftType
    ) -> None:
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
    created_at: datetime
    name: str
    space: str
    version: str
    feature: str
    alert: str
    id: int
    status: str

class DriftAlertRequest:
    def __init__(
        self,
        name: str,
        space: str,
        version: str,
        active: bool = False,
        limit_datetime: Optional[datetime] = None,
        limit: Optional[int] = None,
    ) -> None:
        """Initialize drift alert request

        Args:
            name:
                Name
            space:
                Space
            version:
                Version
            active:
                Whether to get active alerts only
            limit_datetime:
                Limit datetime for alerts
            limit:
                Limit for number of alerts to return
        """

# Client
class ScouterClient:
    """Helper client for interacting with Scouter Server"""

    def __init__(self, config: Optional[HttpConfig] = None) -> None:
        """Initialize ScouterClient

        Args:
            config:
                HTTP configuration for interacting with the server.
        """

    def get_binned_drift(self, drift_request: DriftRequest) -> Any:
        """Get drift map from server

        Args:
            drift_request:
                DriftRequest object

        Returns:
            Drift map of type BinnedMetrics | BinnedPsiFeatureMetrics | BinnedSpcFeatureMetrics
        """

    def register_profile(self, profile: Any, set_active: bool = False) -> bool:
        """Registers a drift profile with the server

        Args:
            profile:
                Drift profile
            set_active:
                Whether to set the profile as active or inactive

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

    def get_alerts(self, request: DriftAlertRequest) -> List[Alert]:
        """Get alerts

        Args:
            request:
                DriftAlertRequest

        Returns:
            List[Alert]
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

class BinnedMetricStats:
    avg: float
    lower_bound: float
    upper_bound: float

    def __str__(self) -> str: ...

class BinnedMetric:
    metric: str
    created_at: List[datetime]
    stats: List[BinnedMetricStats]

    def __str__(self) -> str: ...

class BinnedMetrics:
    @property
    def metrics(self) -> Dict[str, BinnedMetric]: ...
    def __str__(self) -> str: ...

class BinnedPsiMetric:
    created_at: List[datetime]
    psi: List[float]
    overall_psi: float
    bins: Dict[int, float]

    def __str__(self) -> str: ...

class BinnedPsiFeatureMetrics:
    features: Dict[str, BinnedMetric]

    def __str__(self) -> str: ...

class SpcDriftFeature:
    created_at: List[datetime]
    values: List[float]

    def __str__(self) -> str: ...

class BinnedSpcFeatureMetrics:
    features: Dict[str, SpcDriftFeature]

    def __str__(self) -> str: ...

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

class PsiDriftConfig:
    def __init__(
        self,
        space: str = "__missing__",
        name: str = "__missing__",
        version: str = "0.1.0",
        alert_config: PsiAlertConfig = PsiAlertConfig(),
        config_path: Optional[Path] = None,
        categorical_features: Optional[list[str]] = None,
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
        """

class PsiDriftProfile:
    @property
    def scouter_version(self) -> str:
        """Return scouter version used to create DriftProfile"""

    @property
    def features(self) -> Dict[str, "PsiFeatureDriftProfile"]:
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

class LLMDriftMap:
    @property
    def records(self) -> List["LLMMetricRecord"]:
        """Return the list of LLM records."""

    def __str__(self): ...

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
        value: float,
        alert_threshold: AlertThreshold,
        alert_threshold_value: Optional[float] = None,
    ):
        """
        Initialize a custom metric for alerting.

        This class represents a custom metric that uses comparison-based alerting. It applies
        an alert condition to a single metric value.

        Args:
            name (str): The name of the metric being monitored. This should be a
                descriptive identifier for the metric.
            value (float): The current value of the metric.
            alert_threshold (AlertThreshold):
                The condition used to determine when an alert should be triggered.
            alert_threshold_value (Optional[float]):
                The threshold or boundary value used in conjunction with the alert_threshold.
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
    def value(self) -> float:
        """Return the metric value"""

    @value.setter
    def value(self, value: float) -> None:
        """Set the metric value"""

    @property
    def alert_condition(self) -> CustomMetricAlertCondition:
        """Return the alert_condition"""

    @alert_condition.setter
    def alert_condition(self, alert_condition: CustomMetricAlertCondition) -> None:
        """Set the alert_condition"""

    @property
    def alert_threshold(self) -> AlertThreshold:
        """Return the alert_threshold"""

    @property
    def alert_threshold_value(self) -> Optional[float]:
        """Return the alert_threshold_value"""

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

class LLMDriftMetric:
    """Metric for monitoring LLM performance."""

    def __init__(
        self,
        name: str,
        value: float,
        alert_threshold: AlertThreshold,
        alert_threshold_value: Optional[float] = None,
        prompt: Optional[Prompt] = None,
    ):
        """
        Initialize a metric for monitoring LLM performance.

        Args:
            name (str):
                The name of the metric being monitored. This should be a
                descriptive identifier for the metric.
            value (float):
                The current value of the metric.
            alert_threshold (AlertThreshold):
                The condition used to determine when an alert should be triggered.
            alert_threshold_value (Optional[float]):
                The threshold or boundary value used in conjunction with the alert_threshold.
                If supplied, this value will be added or subtracted from the provided metric value to
                determine if an alert should be triggered.
            prompt (Optional[Prompt]):
                Optional prompt associated with the metric. This can be used to provide context or
                additional information about the metric being monitored. If creating an LLM drift profile
                from a pre-defined workflow, this can be none.
        """

    @property
    def name(self) -> str:
        """Return the metric name"""

    @property
    def value(self) -> float:
        """Return the metric value"""

    @property
    def prompt(self) -> Optional[Prompt]:
        """Return the prompt associated with the metric"""

    @property
    def alert_threshold(self) -> AlertThreshold:
        """Return the alert_threshold"""

    @property
    def alert_threshold_value(self) -> Optional[float]:
        """Return the alert_threshold_value"""

class LLMMetricRecord:
    @property
    def record_uid(self) -> str:
        """Return the record id"""

    @property
    def created_at(self) -> datetime:
        """Return the timestamp when the record was created"""

    @property
    def space(self) -> str:
        """Return the space associated with the record"""

    @property
    def name(self) -> str:
        """Return the name associated with the record"""

    @property
    def version(self) -> str:
        """Return the version associated with the record"""

    @property
    def metric(self) -> str:
        """Return the name of the metric associated with the record"""

    @property
    def value(self) -> float:
        """Return the value of the metric associated with the record"""

    def __str__(self) -> str:
        """Return the string representation of the record"""

class LLMDriftConfig:
    def __init__(
        self,
        space: str = "__missing__",
        name: str = "__missing__",
        version: str = "0.1.0",
        sample_rate: int = 5,
        alert_config: LLMAlertConfig = LLMAlertConfig(),
    ):
        """Initialize drift config
        Args:
            space:
                Space to associate with the config
            name:
                Name to associate with the config
            version:
                Version to associate with the config. Defaults to 0.1.0
            sample_rate:
                Sample rate for LLM drift detection. Defaults to 5.
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
    def drift_type(self) -> DriftType:
        """Drift type"""

    @property
    def alert_config(self) -> LLMAlertConfig:
        """get alert_config"""

    @alert_config.setter
    def alert_config(self, alert_config: LLMAlertConfig) -> None:
        """Set alert_config"""

    @staticmethod
    def load_from_json_file(path: Path) -> "LLMDriftConfig":
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
        alert_config: Optional[LLMAlertConfig] = None,
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

class LLMDriftProfile:
    def __init__(
        self,
        config: LLMDriftConfig,
        metrics: list[LLMDriftMetric],
        workflow: Optional[Workflow] = None,
    ) -> None:
        """Initialize a LLMDriftProfile for LLM evaluation and drift detection.

        LLM evaluations are run asynchronously on the scouter server.

        Logic flow:
            1. If only metrics are provided, a workflow will be created automatically
               from the metrics. In this case a prompt is required for each metric.
            2. If a workflow is provided, it will be parsed and validated for compatibility:
               - A list of metrics to evaluate workflow output must be provided
               - Metric names must correspond to the final task names in the workflow

        Baseline metrics and thresholds will be extracted from the LLMDriftMetric objects.

        Args:
            config (LLMDriftConfig):
                The configuration for the LLM drift profile containing space, name,
                version, and alert settings.
            metrics (list[LLMDriftMetric]):
                A list of LLMDriftMetric objects representing the metrics to be monitored.
                Each metric defines evaluation criteria and alert thresholds.
            workflow (Optional[Workflow]):
                Optional custom workflow for advanced evaluation scenarios. If provided,
                the workflow will be validated to ensure proper parameter and response
                type configuration.

        Returns:
            LLMDriftProfile: Configured profile ready for LLM drift monitoring.

        Raises:
            ProfileError: If workflow validation fails, metrics are empty when no
                workflow is provided, or if workflow tasks don't match metric names.

        Examples:
            Basic usage with metrics only:

            >>> config = LLMDriftConfig("my_space", "my_model", "1.0")
            >>> metrics = [
            ...     LLMDriftMetric("accuracy", 0.95, AlertThreshold.Above, 0.1, prompt),
            ...     LLMDriftMetric("relevance", 0.85, AlertThreshold.Below, 0.2, prompt2)
            ... ]
            >>> profile = LLMDriftProfile(config, metrics)

            Advanced usage with custom workflow:

            >>> workflow = create_custom_workflow()  # Your custom workflow
            >>> metrics = [LLMDriftMetric("final_task", 0.9, AlertThreshold.Above)]
            >>> profile = LLMDriftProfile(config, metrics, workflow)

        Note:
            - When using custom workflows, ensure final tasks have Score response types
            - Initial workflow tasks must include "input" and/or "response" parameters
            - All metric names must match corresponding workflow task names
        """

    @property
    def config(self) -> LLMDriftConfig:
        """Return the drift config"""

    @property
    def metrics(self) -> List[LLMDriftMetric]:
        """Return LLM metrics and their corresponding values"""

    @property
    def scouter_version(self) -> str:
        """Return scouter version used to create DriftProfile"""

    def __str__(self) -> str:
        """String representation of LLMDriftProfile"""

    def model_dump_json(self) -> str:
        """Return json representation of drift profile"""

    def model_dump(self) -> Dict[str, Any]:
        """Return dictionary representation of drift profile"""

    def save_to_json(self, path: Optional[Path] = None) -> Path:
        """Save drift profile to json file

        Args:
            path: Optional path to save the json file. If not provided, a default path will be used.

        Returns:
            Path to the saved json file.
        """

    @staticmethod
    def model_validate(data: Dict[str, Any]) -> "LLMDriftProfile":
        """Load drift profile from dictionary

        Args:
            data:
                DriftProfile dictionary
        """

    @staticmethod
    def model_validate_json(json_string: str) -> "LLMDriftProfile":
        """Load drift profile from json

        Args:
            json_string:
                JSON string representation of the drift profile
        """

    @staticmethod
    def from_file(path: Path) -> "LLMDriftProfile":
        """Load drift profile from file

        Args:
            path: Path to the json file

        Returns:
            LLMDriftProfile
        """

    def update_config_args(
        self,
        space: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
        sample_size: Optional[int] = None,
        alert_config: Optional[LLMAlertConfig] = None,
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
        config: Optional[
            Union[SpcDriftConfig, PsiDriftConfig, CustomMetricDriftConfig]
        ] = None,
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

    def create_llm_drift_profile(
        self,
        config: LLMDriftConfig,
        metrics: List[LLMDriftMetric],
        workflow: Optional[Workflow] = None,
    ) -> LLMDriftProfile:
        """Initialize a LLMDriftProfile for LLM evaluation and drift detection.

        LLM evaluations are run asynchronously on the scouter server.

        Logic flow:
            1. If only metrics are provided, a workflow will be created automatically
               from the metrics. In this case a prompt is required for each metric.
            2. If a workflow is provided, it will be parsed and validated for compatibility:
               - A list of metrics to evaluate workflow output must be provided
               - Metric names must correspond to the final task names in the workflow

        Baseline metrics and thresholds will be extracted from the LLMDriftMetric objects.

        Args:
            config (LLMDriftConfig):
                The configuration for the LLM drift profile containing space, name,
                version, and alert settings.
            metrics (list[LLMDriftMetric]):
                A list of LLMDriftMetric objects representing the metrics to be monitored.
                Each metric defines evaluation criteria and alert thresholds.
            workflow (Optional[Workflow]):
                Optional custom workflow for advanced evaluation scenarios. If provided,
                the workflow will be validated to ensure proper parameter and response
                type configuration.

        Returns:
            LLMDriftProfile: Configured profile ready for LLM drift monitoring.

        Raises:
            ProfileError: If workflow validation fails, metrics are empty when no
                workflow is provided, or if workflow tasks don't match metric names.

        Examples:
            Basic usage with metrics only:

            >>> config = LLMDriftConfig("my_space", "my_model", "1.0")
            >>> metrics = [
            ...     LLMDriftMetric("accuracy", 0.95, AlertThreshold.Above, 0.1, prompt),
            ...     LLMDriftMetric("relevance", 0.85, AlertThreshold.Below, 0.2, prompt2)
            ... ]
            >>> profile = Drifter().create_llm_drift_profile(config, metrics)

            Advanced usage with custom workflow:

            >>> workflow = create_custom_workflow()  # Your custom workflow
            >>> metrics = [LLMDriftMetric("final_task", 0.9, AlertThreshold.Above)]
            >>> profile = Drifter().create_llm_drift_profile(config, metrics, workflow)

        Note:
            - When using custom workflows, ensure final tasks have Score response types
            - Initial workflow tasks must include "input" and/or "response" parameters
            - All metric names must match corresponding workflow task names
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
        data: Union[LLMRecord, List[LLMRecord]],
        drift_profile: LLMDriftProfile,
        data_type: Optional[ScouterDataType] = None,
    ) -> LLMDriftMap:
        """Create a drift map from data.

        Args:
            data:

            drift_profile:
                Drift profile to use to compute drift map
            data_type:
                Optional data type. Inferred from data if not provided.

        Returns:
            LLMDriftMap
        """

    def compute_drift(  # type: ignore
        self,
        data: Any,
        drift_profile: Union[SpcDriftProfile, PsiDriftProfile, LLMDriftProfile],
        data_type: Optional[ScouterDataType] = None,
    ) -> Union[SpcDriftMap, PsiDriftMap, LLMDriftMap]:
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
            SpcDriftMap, PsiDriftMap or LLMDriftMap
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
    def __init__(self, space: str, name: str, version: str) -> None:
        """Initializes an api metric observer

        Args:
            space:
                Model space
            name:
                Model name
            version:
                Model version
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

class TransportType:
    Kafka = "TransportType"
    RabbitMQ = "TransportType"
    Redis = "TransportType"
    HTTP = "TransportType"

class EntityType:
    Feature = "EntityType"
    Metric = "EntityType"

class RecordType:
    Spc = "RecordType"
    Psi = "RecordType"
    Observability = "RecordType"
    Custom = "RecordType"

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
                Redis address. If not provided, the value of the REDIS_ADDR environment
                variable is used and defaults to "redis://localhost:6379".

            channel (str):
                Redis channel to publish messages to.

                If not provided, the value of the REDIS_CHANNEL environment variable is used and defaults to "scouter_monitoring".
        """

    def __str__(self): ...

class ServerRecord:
    Spc: "ServerRecord"
    Psi: "ServerRecord"
    Custom: "ServerRecord"
    Observability: "ServerRecord"

    def __init__(self, record: Any) -> None:
        """Initialize server record

        Args:
            record:
                Server record to initialize
        """

    @property
    def record(
        self,
    ) -> Union[
        "SpcServerRecord",
        "PsiServerRecord",
        "CustomMetricServerRecord",
        "ObservabilityMetrics",
    ]:
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

class SpcServerRecord:
    def __init__(
        self,
        space: str,
        name: str,
        version: str,
        feature: str,
        value: float,
    ):
        """Initialize spc drift server record

        Args:
            space:
                Model space
            name:
                Model name
            version:
                Model version
            feature:
                Feature name
            value:
                Feature value
        """

    @property
    def created_at(self) -> datetime:
        """Return the created at timestamp."""

    @property
    def space(self) -> str:
        """Return the space."""

    @property
    def name(self) -> str:
        """Return the name."""

    @property
    def version(self) -> str:
        """Return the version."""

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

class PsiServerRecord:
    def __init__(
        self,
        space: str,
        name: str,
        version: str,
        feature: str,
        bin_id: int,
        bin_count: int,
    ):
        """Initialize spc drift server record

        Args:
            space:
                Model space
            name:
                Model name
            version:
                Model version
            feature:
                Feature name
            bin_id:
                Bundle ID
            bin_count:
                Bundle ID
        """

    @property
    def created_at(self) -> datetime:
        """Return the created at timestamp."""

    @property
    def space(self) -> str:
        """Return the space."""

    @property
    def name(self) -> str:
        """Return the name."""

    @property
    def version(self) -> str:
        """Return the version."""

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

class CustomMetricServerRecord:
    def __init__(
        self,
        space: str,
        name: str,
        version: str,
        metric: str,
        value: float,
    ):
        """Initialize spc drift server record

        Args:
            space:
                Model space
            name:
                Model name
            version:
                Model version
            metric:
                Metric name
            value:
                Metric value
        """

    @property
    def created_at(self) -> datetime:
        """Return the created at timestamp."""

    @property
    def space(self) -> str:
        """Return the space."""

    @property
    def name(self) -> str:
        """Return the name."""

    @property
    def version(self) -> str:
        """Return the version."""

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
    def int(name: str, value: int) -> "Feature":
        """Create an integer feature

        Args:
            name:
                Name of the feature
            value:
                Value of the feature
        """

    @staticmethod
    def float(name: str, value: float) -> "Feature":
        """Create a float feature

        Args:
            name:
                Name of the feature
            value:
                Value of the feature
        """

    @staticmethod
    def string(name: str, value: str) -> "Feature":
        """Create a string feature

        Args:
            name:
                Name of the feature
            value:
                Value of the feature
        """

    @staticmethod
    def categorical(name: str, value: str) -> "Feature":
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
        features: List[Feature] | Dict[str, Union[int, float, str]],
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
    def features(self) -> List[Feature]:
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

    def insert(self, entity: Union[Features, Metrics, "LLMRecord"]) -> None:
        """Insert a record into the queue

        Args:
            entity:
                Entity to insert into the queue.
                Can be an instance for Features, Metrics, or LLMRecord.

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
        ],
    ) -> "ScouterQueue":
        """Initializes Scouter queue from one or more drift profile paths

        Args:
            path (Dict[str, Path]):
                Dictionary of drift profile paths.
                Each key is a user-defined alias for accessing a queue
            transport_config (Union[KafkaConfig, RabbitMQConfig, RedisConfig, HttpConfig]):
                Transport configuration for the queue publisher
                Can be KafkaConfig, RabbitMQConfig RedisConfig, or HttpConfig

        Example:
            ```python
            queue = ScouterQueue(
                path={
                    "spc": Path("spc_profile.json"),
                    "psi": Path("psi_profile.json"),
                },
                transport_config=KafkaConfig(
                    brokers="localhost:9092",
                    topic="scouter_topic",
                ),
            )

            queue["psi"].insert(
                Features(
                    features=[
                        Feature("feature_1", 1),
                        Feature("feature_2", 2.0),
                        Feature("feature_3", "value"),
                    ]
                )
            )
            ```
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

class BaseModel(Protocol):
    """Protocol for pydantic BaseModel to ensure compatibility with context"""

    def model_dump(self) -> Dict[str, Any]:
        """Dump the model as a dictionary"""

    def model_dump_json(self) -> str:
        """Dump the model as a JSON string"""

    def __str__(self) -> str:
        """String representation of the model"""

SerializedType: TypeAlias = Union[str, int, float, dict, list]
Context: TypeAlias = Union[Dict[str, Any], BaseModel]

class LLMRecord:
    """LLM record containing context tied to a Large Language Model interaction
    that is used to evaluate drift in LLM responses.


    Examples:
        >>> record = LLMRecord(
        ...     context={
        ...         "input": "What is the capital of France?",
        ...         "response": "Paris is the capital of France."
        ...     },
        ... )
        >>> print(record.context["input"])
        "What is the capital of France?"
    """

    prompt: Optional[Prompt]
    """Optional prompt configuration associated with this record."""

    entity_type: EntityType
    """Type of entity, always EntityType.LLM for LLMRecord instances."""

    def __init__(
        self,
        context: Context,
        prompt: Optional[Prompt | SerializedType] = None,
    ) -> None:
        """Creates a new LLM record to associate with an `LLMDriftProfile`.
        The record is sent to the `Scouter` server via the `ScouterQueue` and is
        then used to inject context into the evaluation prompts.

        Args:
            context:
                Additional context information as a dictionary or a pydantic BaseModel. During evaluation,
                this will be merged with the input and response data and passed to the assigned
                evaluation prompts. So if you're evaluation prompts expect additional context via
                bound variables (e.g., `${foo}`), you can pass that here as key value pairs.
                {"foo": "bar"}
            prompt:
                Optional prompt configuration associated with this record. Can be a Potatohead Prompt or
                a JSON-serializable type.

        Raises:
            TypeError: If context is not a dict or a pydantic BaseModel.

        """

    @property
    def context(self) -> Dict[str, Any]:
        """Get the contextual information.

        Returns:
            The context data as a Python object (deserialized from JSON).

        Raises:
            TypeError: If the stored JSON cannot be converted to a Python object.
        """

########################################################################################
#  This section contains the type definitions for opsml.types module
# __opsml.types__
# ######################################################################################

class DriftConfig:
    def __init__(
        self,
        active: bool = False,
        deactivate_others: bool = False,
        drift_type: List[str] = [],
    ):
        """Initialize drift detection configuration for model and prompt cards.

        Args:
            active:
                Whether drift detection is active. Defaults to False
            deactivate_others:
                Whether to deactivate previous drift config versions. Defaults to False
            drift_type:
                Types of drift detection to enable (e.g., 'psi', 'custom'). Defaults to empty list
        """

    @property
    def active(self) -> bool:
        """Whether drift detection is currently active."""

    @property
    def deactivate_others(self) -> bool:
        """Whether to deactivate other drift configurations."""

    @property
    def drift_type(self) -> List[str]:
        """List of drift detection types enabled."""

# shared
class CommonKwargs:
    IsPipeline: "CommonKwargs"
    ModelType: "CommonKwargs"
    ModelClass: "CommonKwargs"
    ModelArch: "CommonKwargs"
    PreprocessorName: "CommonKwargs"
    Preprocessor: "CommonKwargs"
    TaskType: "CommonKwargs"
    Model: "CommonKwargs"
    Undefined: "CommonKwargs"
    Backend: "CommonKwargs"
    Pytorch: "CommonKwargs"
    Tensorflow: "CommonKwargs"
    SampleData: "CommonKwargs"
    Onnx: "CommonKwargs"
    LoadType: "CommonKwargs"
    DataType: "CommonKwargs"
    Tokenizer: "CommonKwargs"
    TokenizerName: "CommonKwargs"
    FeatureExtractor: "CommonKwargs"
    FeatureExtractorName: "CommonKwargs"
    Image: "CommonKwargs"
    Text: "CommonKwargs"
    VowpalArgs: "CommonKwargs"
    BaseVersion: "CommonKwargs"
    SampleDataInterfaceType: "CommonKwargs"

    @staticmethod
    def from_string(s: str) -> Optional["CommonKwargs"]:
        """Return the CommonKwargs enum from a string.

        Args:
            s:
                The string representation of the CommonKwargs.

        Returns:
            The CommonKwargs enum.
        """

    def as_string(self) -> str:
        """Return the string representation of the CommonKwargs.

        Returns:
            String representation of the CommonKwargs.
        """

class DataType:
    Pandas: "DataType"
    Arrow: "DataType"
    Polars: "DataType"
    Numpy: "DataType"
    Image: "DataType"
    Text: "DataType"
    Dict: "DataType"
    Sql: "DataType"
    Profile: "DataType"
    TransformerBatch: "DataType"
    String: "DataType"
    TorchTensor: "DataType"
    TorchDataset: "DataType"
    TensorFlowTensor: "DataType"
    Tuple: "DataType"
    List: "DataType"
    Str: "DataType"
    OrderedDict: "DataType"
    Joblib: "DataType"
    Base: "DataType"
    Dataset: "DataType"
    NotProvided: "DataType"

class SaveName:
    Card: "SaveName"
    Audit: "SaveName"
    ModelMetadata: "SaveName"
    Model: "SaveName"
    Preprocessor: "SaveName"
    OnnxModel: "SaveName"
    SampleModelData: "SaveName"
    DataProfile: "SaveName"
    Data: "SaveName"
    Profile: "SaveName"
    Artifacts: "SaveName"
    QuantizedModel: "SaveName"
    Tokenizer: "SaveName"
    FeatureExtractor: "SaveName"
    Metadata: "SaveName"
    Graphs: "SaveName"
    OnnxConfig: "SaveName"
    Dataset: "SaveName"
    DriftProfile: "SaveName"

    @staticmethod
    def from_string(s: str) -> Optional["SaveName"]:
        """Return the SaveName enum from a string.

        Args:
            s:
                The string representation of the SaveName.

        Returns:
            The SaveName enum.
        """

    def as_string(self) -> str:
        """Return the string representation of the SaveName.

        Returns:
            String representation of the SaveName.
        """

    def __str__(self):
        """Return a string representation of the SaveName.

        Returns:
            String representation of the SaveName.
        """

class Suffix:
    Onnx: "Suffix"
    Parquet: "Suffix"
    Zarr: "Suffix"
    Joblib: "Suffix"
    Html: "Suffix"
    Json: "Suffix"
    Ckpt: "Suffix"
    Pt: "Suffix"
    Text: "Suffix"
    Catboost: "Suffix"
    Jsonl: "Suffix"
    Empty: "Suffix"
    Dmatrix: "Suffix"
    Model: "Suffix"

    @staticmethod
    def from_string(s: str) -> Optional["Suffix"]:
        """Return the Suffix enum from a string.

        Args:
            s:
                The string representation of the Suffix.

        Returns:
            The Suffix enum.
        """

    def as_string(self) -> str:
        """Return the string representation of the Suffix.

        Returns:
            String representation of the Suffix.
        """

    def __str__(self):
        """Return a string representation of the Suffix.

        Returns:
            String representation of the Suffix.
        """

class SaverPath:
    path: Path

    def __init__(
        self,
        parent: Path,
        child: Optional[Path],
        filename: Optional[SaveName],
        extension: Optional[Suffix],
    ) -> None:
        """Helper for creating paths for saving artifacts.

        Args:
            parent (Path):
                The parent path.
            child (Path | None):
                The child path.
            filename (SaveName | None):
                The filename.
            extension (Suffix | None):
                The extension.
        """

class VersionType:
    Major: "VersionType"
    Minor: "VersionType"
    Patch: "VersionType"
    Pre: "VersionType"
    Build: "VersionType"
    PreBuild: "VersionType"

    def __init__(self, version_type: str) -> None: ...
    def __eq__(self, other: object) -> bool: ...

class DriftProfileUri:
    root_dir: Path
    uri: Path
    drift_type: DriftType

class DriftArgs:
    def __init__(self, active: bool = True, deactivate_others: bool = False) -> None:
        """Define a drift config

        Args:
            active (bool):
                Whether to set the drift profile to active
            deactivate_others (bool):
                Whether to deactivate all other drift profiles of the same space and name
        """

    @property
    def active(self) -> bool:
        """Return the active status of the drift profile."""

    @property
    def deactivate_others(self) -> bool:
        """Return the deactivate_others status of the drift profile."""

class DriftProfileMap:
    def __init__(self) -> None:
        """Creates an empty drift profile map"""

    def add_profile(self, alias: str, profile: Any) -> None:
        """Add a drift profile to the map

        Args:
            alias:
                Alias to use for the drift profile
            profile:
                Drift profile to add
        """

    def __getitem__(self, key: str) -> Any:
        """Returns the drift profile at the given key"""

    def is_empty(self) -> bool:
        """Returns whether the drift profile map is empty

        Returns:
            True if the drift profile map is empty, False otherwise
        """

class ExtraMetadata:
    metadata: Dict[str, Any]

class Feature:
    feature_type: str
    shape: List[int]
    extra_args: Dict[str, str]

    def __init__(
        self,
        feature_type: str,
        shape: List[int],
        extra_args: Optional[Dict[str, str]] = None,
    ) -> None:
        """Define a feature

        Args:
            feature_type:
                The type of the feature
            shape:
                The shape of the feature
            extra_args:
                Extra arguments to pass to the feature
        """

    def __str__(self) -> str:
        """Return a string representation of the Feature.

        Returns:
            String representation of the Feature.
        """

class FeatureSchema:
    def __init__(self, items: Optional[dict[str, Feature]] = None) -> None:
        """Define a feature map

        Args:
            features:
                The features to use in the feature map
        """

    def __str__(self) -> str:
        """Return a string representation of the FeatureSchema."""

    def __getitem__(self, key: str) -> Feature:
        """Returns the feature at the given key."""

########################################################################################
#  This section contains the type definitions for opsml.data module
# __opsml.data__
# ######################################################################################

class DataInterfaceType:
    Base: "DataInterfaceType"
    Arrow: "DataInterfaceType"
    Numpy: "DataInterfaceType"
    Pandas: "DataInterfaceType"
    Polars: "DataInterfaceType"
    Sql: "DataInterfaceType"
    Torch: "DataInterfaceType"

class DataSaveKwargs:
    def __init__(
        self,
        data: Optional[Dict] = None,
    ) -> None:
        """Optional arguments to pass to save_model

        Args:
            data (Dict):
                Optional data arguments to use when saving model to onnx format
        """

    def __str__(self): ...
    def model_dump_json(self) -> str: ...
    @staticmethod
    def model_validate_json(json_string: str) -> "DataSaveKwargs": ...

class DataLoadKwargs:
    data: Optional[Dict]

    def __init__(
        self,
        data: Optional[Dict] = None,
    ) -> None:
        """Optional arguments to pass to load_model

        Args:
            data (Dict):
                Optional data arguments to use when loading

        """

class Inequality:
    Equal: "Inequality"
    GreaterThan: "Inequality"
    GreaterThanEqual: "Inequality"
    LesserThan: "Inequality"
    LesserThanEqual: "Inequality"

class ColValType:
    String: "ColValType"
    Float: "ColValType"
    Int: "ColValType"
    Timestamp: "ColValType"

class ColType:
    Builtin: "ColType"
    Timestamp: "ColType"

class ColumnSplit:
    column_name: str
    column_value: ColValType
    column_type: ColType
    inequality: Inequality

    def __init__(
        self,
        column_name: str,
        column_value: Union[str, float, int],
        column_type: ColType = ColType.Builtin,
        inequality: Optional[Union[str, Inequality]] = None,
    ) -> None:
        """Define a column split

        Args:
            column_name:
                The name of the column
            column_value:
                The value of the column. Can be a string, float, or int. If
                timestamp, convert to isoformat (str) and specify timestamp coltype
            column_type:
                The type of the column. Defaults to ColType.Builtin. If providing ColtType.Timestamp, the
                column_value should be a float
            inequality:
                The inequality of the column
        """

class StartStopSplit:
    start: int
    stop: int

    def __init__(self, start: int, stop: int) -> None:
        """Define a start stop split

        Args:
            start:
                The start of the split
            stop:
                The stop of the split
        """

class IndiceSplit:
    indices: List[int]

    def __init__(self, indices: List[int]) -> None:
        """Define an indice split

        Args:
            indices:
                The indices of the split
        """

class DataSplit:
    label: str
    column_split: Optional[ColumnSplit]
    start_stop_split: Optional[StartStopSplit]
    indice_split: Optional[IndiceSplit]

    def __init__(
        self,
        label: str,
        column_split: Optional[ColumnSplit] = None,
        start_stop_split: Optional[StartStopSplit] = None,
        indice_split: Optional[IndiceSplit] = None,
    ) -> None:
        """Define a data split

        Args:
            label:
                The label of the split
            column_split:
                The column split
            start_stop_split:
                The start stop split
            indice_split:
                The indice split
        """

class DependentVars:
    def __init__(
        self,
        column_names: Optional[List[str]] = None,
        column_indices: Optional[List[int]] = None,
    ) -> None:
        """Define dependent variables for the data interface. User
        can specify either column names or column indices.

        Args:
            column_names:
                The column names of the dependent variables
            column_indices:
                The column indices of the dependent variables
        """

    def __str__(self) -> str:
        """String representation of the dependent variables"""

    @property
    def column_names(self) -> List[str]:
        """Return the column names"""

    @column_names.setter
    def column_names(self, column_names: List[str]) -> None:
        """Set the column names"""

    @property
    def column_indices(self) -> List[int]:
        """Return the column indices"""

    @column_indices.setter
    def column_indices(self, column_indices: List[int]) -> None:
        """Set the column indices"""

class DataSplits:
    def __init__(self, splits: List[DataSplit]) -> None:
        """Define data splits

        Args:
            splits:
                The data splits
        """

    def __str__(self) -> str:
        """String representation of the data splits"""

    @property
    def splits(self) -> List[DataSplit]:
        """Return the splits"""

    @splits.setter
    def splits(self, splits: List[DataSplit]) -> None:
        """Set the splits"""

    def split_data(
        self,
        data: Any,
        data_type: DataType,
        dependent_vars: DependentVars,
    ) -> Dict[str, "Data"]:
        """Split the data

        Args:
            data:
                The data to split
            data_type:
                The data type
            dependent_vars:
                Dependent variables to associate with the data

        Returns:
            A dictionary of data splits
        """

class Data:
    x: Any
    y: Any

class DataSplitter:
    @staticmethod
    def split_data(
        split: DataSplit,
        data: Any,
        data_type: DataType,
        dependent_vars: DependentVars,
    ) -> Data:
        """Create a split

        Args:
            split:
                The data split to use to split the data
            data:
                The data to split
            data_type:
                The data type
            dependent_vars:
                Dependent variables to associate with the data

        Returns:
            A Data object
        """

class DataInterfaceSaveMetadata:
    data_uri: Path
    data_profile_uri: Optional[Path]
    sql_uri: Optional[Path]
    extra: Optional[ExtraMetadata]
    save_kwargs: DataSaveKwargs

    def __init__(
        self,
        data_uri: Path,
        data_profile_uri: Optional[Path] = None,
        sql_uri: Optional[Path] = None,
        extra: Optional[ExtraMetadata] = None,
        save_kwargs: Optional[DataSaveKwargs] = None,
    ) -> None:
        """Define interface save metadata

        Args:
            data_uri:
                The data uri
            data_profile_uri:
                The data profile uri
            sql_uri:
                The sql uri
            extra:
                Extra metadata
            save_kwargs:
                Save kwargs
        """

class DataInterfaceMetadata:
    save_metadata: DataInterfaceSaveMetadata
    schema: FeatureSchema
    extra_metadata: dict[str, str]
    sql_logic: "SqlLogic"  # pylint: disable=used-before-assignment
    interface_type: DataInterfaceType
    data_splits: DataSplits
    dependent_vars: DependentVars
    data_type: DataType

    def __init__(
        self,
        save_metadata: DataInterfaceSaveMetadata,
        schema: FeatureSchema,
        extra_metadata: dict[str, str],
        sql_logic: "SqlLogic",
        interface_type: DataInterfaceType,
        data_splits: DataSplits,
        dependent_vars: DependentVars,
        data_type: DataType,
    ) -> None:
        """Instantiate DataInterfaceMetadata object

        Args:
            save_metadata:
                The save metadata
            schema:
                The schema
            extra_metadata:
                Extra metadata
            sql_logic:
                Sql logic
            interface_type:
                The interface type
            data_splits:
                The data splits
            dependent_vars:
                Dependent variables
            data_type:
                The data type
        """

    def __str__(self) -> str:
        """Return the string representation of the model interface metadata"""

    def model_dump_json(self) -> str:
        """Dump the model interface metadata to json"""

    @staticmethod
    def model_validate_json(json_string: str) -> "DataInterfaceMetadata":
        """Validate the model interface metadata json"""

class DataInterface:
    def __init__(
        self,
        data: Optional[Any] = None,
        data_splits: Optional[Union[DataSplits, List[DataSplit]]] = None,
        dependent_vars: Optional[Union[DependentVars, List[str], List[int]]] = None,
        sql_logic: Optional["SqlLogic"] = None,
        data_profile: Optional[DataProfile] = None,
    ) -> None:
        """Define a data interface

        Args:
            data (Any):
                Data. Can be a pyarrow table, pandas dataframe, polars dataframe
                or numpy array
            dependent_vars (DependentVars):
                List of dependent variables to associate with data
            data_splits (DataSplits):
                Optional list of `DataSplit`
            sql_logic (SqlLogic):
                SqlLogic class used to generate data.
            data_profile (DataProfile):
                Data profile
        """

    @property
    def data(self) -> Optional[Any]:
        """Returns the data"""

    @data.setter
    def data(self, data: Any) -> None:
        """Sets the data"""

    @property
    def data_splits(self) -> DataSplits:
        """Returns the data splits."""

    @data_splits.setter
    def data_splits(self, data_splits: Union[DataSplits, List[DataSplit]]) -> None:
        """Sets the data splits"""

    @property
    def dependent_vars(self) -> DependentVars:
        """Returns the dependent variables."""

    @dependent_vars.setter
    def dependent_vars(
        self,
        dependent_vars: Union[DependentVars, List[str], List[int]],
    ) -> None:
        """Sets the dependent variables"""

    @property
    def schema(self) -> FeatureSchema:
        """Returns the feature map."""

    @schema.setter
    def schema(self, schema: FeatureSchema) -> None:
        """Sets the feature map"""

    @property
    def sql_logic(self) -> "SqlLogic":
        """Returns the sql logic."""

    @property
    def data_type(self) -> DataType:
        """Return the data type."""

    def add_sql_logic(
        self,
        name: str,
        query: Optional[str] = None,
        filepath: Optional[str] = None,
    ) -> None:
        """Add sql logic to the data interface

        Args:
            name:
                The name of the sql logic
            query:
                The optional query to use
            filepath:
                The optional filepath to open the query from
        """

    def save(
        self,
        path: Path,
        save_kwargs: Optional[DataSaveKwargs] = None,
    ) -> DataInterfaceMetadata:
        """Saves all data interface component to the given path. This used as part of saving a
        DataCard

        Methods called in save:
            - save_sql: Saves all sql logic to files(s)
            - create_schema: Creates a FeatureSchema from the associated data
            - save_data: Saves the data to a file

        Args:
            path (Path):
                The path to save the data interface components to.
            save_kwargs (DataSaveKwargs):
                The save kwargs to use.

        """

    def load(
        self,
        path: Path,
        metadata: DataInterfaceSaveMetadata,
        load_kwargs: Optional[DataLoadKwargs] = None,
    ) -> None:
        """Load the data from a file

        Args:
            path (Path):
                Base path to load the data from
            metadata (DataInterfaceSaveMetadata):
                Metadata associated with the data
            load_kwargs (DataLoadKwargs):
                Additional kwargs to pass in.
        """

    def split_data(self) -> Dict[str, Data]:
        """Split the data

        Returns:
            A dictionary of data splits
        """

    def create_data_profile(
        self,
        bin_size: Optional[int] = 20,
        compute_correlations: Optional[bool] = False,
    ) -> DataProfile:
        """Create a data profile


        Args:
            bin_size (int):
                The bin size for the data profile
            compute_correlations (bool):
                Whether to compute correlations
        """

    @property
    def data_profile(self) -> Optional[DataProfile]:
        """Return the data profile

        Returns:
            The data profile
        """

    @data_profile.setter
    def data_profile(self, data_profile: Optional[DataProfile]) -> None:
        """Set the data profile

        Args:
            data_profile (DataProfile | None):
                The data profile to set
        """

class SqlLogic:
    def __init__(self, queries: Dict[str, str]) -> None:
        """Define sql logic

        Args:
            queries:
                Sql logic used to generate data represented as a dictionary.
                Key is the name to assign to the sql logic and value is either a sql query
                or a path to a .sql file.
        """

    def __str__(self) -> str:
        """String representation of the sql logic"""

    def add_sql_logic(
        self,
        name: str,
        query: Optional[str] = None,
        filepath: Optional[str] = None,
    ) -> None:
        """Add sql logic to existing queries

        Args:
            name:
                The name to associate with the sql logic
            query:
                SQL query
            filepath:
                Filepath to SQL query

        """

    @property
    def queries(self) -> Dict[str, str]:
        """Return the queries"""

    @queries.setter
    def queries(self, queries: Dict[str, str]) -> None:
        """Set the queries"""

    def __getitem__(self, key: str) -> str:
        """Get the query by key

        Args:
            key:
                The key to get the query by

        Returns:
            The query
        """

class NumpyData(DataInterface):
    def __init__(
        self,
        data: Optional[Any] = None,
        data_splits: Optional[Union[DataSplits, List[DataSplit]]] = None,
        dependent_vars: Optional[Union[DependentVars, List[str], List[int]]] = None,
        sql_logic: Optional[SqlLogic] = None,
        data_profile: Optional[DataProfile] = None,
    ) -> None:
        """Define a data interface

        Args:
            data (np.NDArray | None):
                Numpy array
            dependent_vars (DependentVars | List[str] | List[int] | None):
                List of dependent variables to associate with data
            data_splits (DataSplits | List[DataSplit]):
                Optional list of `DataSplit`
            sql_logic (SqlLogic | None):
                Sql logic used to generate data represented as a dictionary.
            data_profile (DataProfile | None):
                Data profile
        """

    def save(
        self,
        path: Path,
        save_kwargs: Optional[DataSaveKwargs] = None,
    ) -> DataInterfaceMetadata:
        """Save data using numpy save format

        Args:
            path (Path):
                Base path to save the data to.
            save_kwargs (DataSaveKwargs):
                Additional kwargs to pass in.

        Acceptable save kwargs:

            see: https://numpy.org/doc/stable/reference/generated/numpy.save.html

            allow_pickle (bool):
                Allow saving object arrays using Python pickles.
            fix_imports (bool):
                The fix_imports flag is deprecated and has no effect

        """

    def load(
        self,
        path: Path,
        metadata: DataInterfaceSaveMetadata,
        load_kwargs: Optional[DataLoadKwargs] = None,
    ) -> None:
        """Load the data via numpy.load

        Args:
            path (Path):
                Base path to load the data from.
            metadata (DataInterfaceSaveMetadata):
                Metadata associated with the data
            load_kwargs (DataLoadKwargs):
                Additional kwargs to use when loading

        Acceptable load kwargs:

            see: https://numpy.org/doc/stable/reference/generated/numpy.load.html

            mmap_mode:
                If not None, then memory-map the file, using the given mode
            allow_pickle (bool):
                Allow loading pickled object arrays stored in npy files
            fix_imports (bool):
                If fix_imports is True, pickle will try to map the old Python 2 names to the new names used in Python 3.
            encoding (str):
                What encoding to use when reading Python 2 strings. Only useful when py3k is True.
            max_header_size (int):
                The maximum size of the file header
        """

class PolarsData(DataInterface):
    def __init__(
        self,
        data: Optional[Any] = None,
        data_splits: Optional[Union[DataSplits, List[DataSplit]]] = None,
        dependent_vars: Optional[Union[DependentVars, List[str], List[int]]] = None,
        sql_logic: Optional[SqlLogic] = None,
        data_profile: Optional[DataProfile] = None,
    ) -> None:
        """Define a data interface

        Args:
            data (pl.DataFrame | None):
                Pandas dataframe
            dependent_vars (DependentVars | List[str] | List[int] | None):
                List of dependent variables to associate with data
            data_splits (DataSplits | List[DataSplit]):
                Optional list of `DataSplit`
            sql_logic (SqlLogic | None):
                Sql logic used to generate data represented as a dictionary.
            data_profile (DataProfile | None):
                Data profile

        """

    def save(
        self, path: Path, save_kwargs: Optional[DataSaveKwargs] = None
    ) -> DataInterfaceMetadata:
        """Saves polars dataframe to parquet dataset via write_parquet

        Args:
            path (Path):
                Base path to save the data to.
            save_kwargs (DataSaveKwargs):
                Additional kwargs to pass in.

        Acceptable save kwargs:
            compression (ParquetCompression):
                Compression codec to use for writing.
            compression_level (int | None):
                Compression level to use. Default is None.
            statistics (bool | str | dict[str, bool]):
                Whether to write statistics. Default is True.
            row_group_size (int | None):
                Number of rows per row group. Default is None.
            data_page_size (int | None):
                Size of data pages. Default is None.
            use_pyarrow (bool):
                Whether to use PyArrow for writing. Default is False.
            pyarrow_options (dict[str, Any] | None):
                Additional options for PyArrow. Default is None.
            partition_by (str | Sequence[str] | None):
                Columns to partition by. Default is None.
            partition_chunk_size_bytes (int):
                Size of partition chunks in bytes. Default is 4294967296.
            storage_options (dict[str, Any] | None):
                Additional storage options. Default is None.
            credential_provider (CredentialProviderFunction | Literal['auto'] | None):
                Credential provider function. Default is 'auto'.
            retries (int):
                Number of retries for writing. Default is 2.

        See Also:
            https://docs.pola.rs/api/python/dev/reference/api/polars.DataFrame.write_parquet.html

        """

    def load(
        self,
        path: Path,
        metadata: DataInterfaceSaveMetadata,
        load_kwargs: Optional[DataLoadKwargs] = None,
    ) -> None:
        """Load the data from a file

        Args:
            path (Path):
                Base path to load the data from.
            metadata (DataInterfaceSaveMetadata):
                Metadata associated with the data
            load_kwargs (DataLoadKwargs):
                Additional kwargs to pass in.

        Acceptable load kwargs:
            columns (list[int] | list[str] | None):
                Columns to load. Default is None.
            n_rows (int | None):
                Number of rows to load. Default is None.
            row_index_name (str | None):
                Name of the row index. Default is None.
            row_index_offset (int):
                Offset for the row index. Default is 0.
            parallel (ParallelStrategy):
                Parallel strategy to use. Default is 'auto'.
            use_statistics (bool):
                Whether to use statistics. Default is True.
            hive_partitioning (bool | None):
                Whether to use hive partitioning. Default is None.
            glob (bool):
                Whether to use glob pattern matching. Default is True.
            schema (SchemaDict | None):
                Schema to use. Default is None.
            hive_schema (SchemaDict | None):
                Hive schema to use. Default is None.
            try_parse_hive_dates (bool):
                Whether to try parsing hive dates. Default is True.
            rechunk (bool):
                Whether to rechunk the data. Default is False.
            low_memory (bool):
                Whether to use low memory mode. Default is False.
            storage_options (dict[str, Any] | None):
                Additional storage options. Default is None.
            credential_provider (CredentialProviderFunction | Literal['auto'] | None):
                Credential provider function. Default is 'auto'.
            retries (int):
                Number of retries for loading. Default is 2.
            use_pyarrow (bool):
                Whether to use PyArrow for loading. Default is False.
            pyarrow_options (dict[str, Any] | None):
                Additional options for PyArrow. Default is None.
            memory_map (bool):
                Whether to use memory mapping. Default is True.
            include_file_paths (str | None):
                File paths to include. Default is None.
            allow_missing_columns (bool):
                Whether to allow missing columns. Default is False.

        See Also:
            https://docs.pola.rs/api/python/dev/reference/api/polars.read_parquet.html
        """

class PandasData(DataInterface):
    def __init__(
        self,
        data: Optional[Any] = None,
        data_splits: Optional[Union[DataSplits, List[DataSplit]]] = None,
        dependent_vars: Optional[Union[DependentVars, List[str], List[int]]] = None,
        sql_logic: Optional[SqlLogic] = None,
        data_profile: Optional[DataProfile] = None,
    ) -> None:
        """Define a data interface

        Args:
            data (pd.DataFrame | None):
                Pandas dataframe
            dependent_vars (DependentVars | List[str] | List[int] | None):
                List of dependent variables to associate with data
            data_splits (DataSplits | List[DataSplit]):
                Optional list of `DataSplit`
            sql_logic (SqlLogic | None):
                Sql logic used to generate data represented as a dictionary.
            data_profile (DataProfile | None):
                Data profile
        """

    def save(
        self, path: Path, save_kwargs: Optional[DataSaveKwargs] = None
    ) -> DataInterfaceMetadata:
        """Saves pandas dataframe as parquet file via to_parquet

        Args:
            path (Path):
                Base path to save the data to.
            save_kwargs (DataSaveKwargs):
                Additional kwargs to pass in.

        Acceptable save kwargs:
            engine ({'auto', 'pyarrow', 'fastparquet'}):
                Parquet library to use. If 'auto', then the option io.parquet.engine is used.
                The default io.parquet.engine behavior is to try 'pyarrow',
                falling back to 'fastparquet' if 'pyarrow' is unavailable. Default is 'auto'.
            compression (str | None):
                Name of the compression to use. Use None for no compression.
                Supported options: 'snappy', 'gzip', 'brotli', 'lz4', 'zstd'. Default is 'snappy'.
            index (bool | None):
                If True, include the dataframe's index(es) in the file output.
                If False, they will not be written to the file. If None, similar to True the dataframe's index(es) will be saved.
                However, instead of being saved as values, the RangeIndex will be stored as a range in the metadata so it doesn't
                require much space and is faster.
                Other indexes will be included as columns in the file output. Default is None.
            partition_cols (list | None):
                Column names by which to partition the dataset. Columns are partitioned in the order they are given.
                Must be None if path is not a string. Default is None.
            storage_options (dict | None):
                Extra options that make sense for a particular storage connection, e.g. host, port, username, password, etc.
                For HTTP(S) URLs the key-value pairs are forwarded to urllib.request.Request as header options.
                For other URLs (e.g. starting with “s3://”, and “gcs://”) the key-value pairs are forwarded to fsspec.open.
                Default is None.
            **kwargs:
                Any additional kwargs are passed to the engine

        Additional Information:
            https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_parquet.html
        """

    def load(
        self,
        path: Path,
        metadata: DataInterfaceSaveMetadata,
        load_kwargs: Optional[DataLoadKwargs] = None,
    ) -> None:
        """Load the pandas dataframe from a parquet dataset via read_parquet

        Args:
            path (Path):
                Base path to load the data from.
            metadata (DataInterfaceSaveMetadata):
                Metadata associated with the data
            load_kwargs (DataLoadKwargs):
                Additional kwargs to pass in.

        Acceptable load kwargs:
            engine ({'auto', 'pyarrow', 'fastparquet'}):
                Parquet library to use. If 'auto', then the option io.parquet.engine is used.
                The default io.parquet.engine behavior is to try 'pyarrow',
                falling back to 'fastparquet' if 'pyarrow' is unavailable. Default is 'auto'.
            columns (list | None):
                If not None, only these columns will be read from the file. Default is None.
            storage_options (dict | None):
                Extra options that make sense for a particular storage connection, e.g. host, port, username, password, etc.
                For HTTP(S) URLs the key-value pairs are forwarded to urllib.request.Request as header options.
                For other URLs (e.g. starting with “s3://”, and “gcs://”) the key-value pairs are forwarded to fsspec.open.
                Default is None.
            use_nullable_dtypes (bool):
                If True, use dtypes that use pd.NA as missing value indicator for the resulting DataFrame.
                (only applicable for the pyarrow engine) As new dtypes are added that support pd.NA in the future,
                the output with this option will change to use those dtypes.
                Note: this is an experimental option, and behaviour (e.g. additional support dtypes) may change without notice.
                Default is False. Deprecated since version 2.0.
            dtype_backend ({'numpy_nullable', 'pyarrow'}):
                Back-end data type applied to the resultant DataFrame (still experimental).
                Behaviour is as follows:
                    - "numpy_nullable": returns nullable-dtype-backed DataFrame (default).
                    - "pyarrow": returns pyarrow-backed nullable ArrowDtype DataFrame. Default is 'numpy_nullable'.
            filesystem (fsspec | pyarrow filesystem | None):
                Filesystem object to use when reading the parquet file. Only implemented for engine="pyarrow". Default is None.
            filters (list[tuple] | list[list[tuple]] | None):
                To filter out data.
                Filter syntax:
                    [[(column, op, val), …],…] where op is [==, =, >, >=, <, <=, !=, in, not in]
                The innermost tuples are transposed into a set of filters applied through an AND operation.
                The outer list combines these sets of filters through an OR operation. A single list of tuples can also be used,
                meaning that no OR operation between set of filters is to be conducted.
                Using this argument will NOT result in row-wise filtering of the final partitions unless engine="pyarrow"
                is also specified.
                For other engines, filtering is only performed at the partition level, that is,
                to prevent the loading of some row-groups and/or files. Default is None.
            **kwargs:
                Any additional kwargs are passed to the engine.

        Additional Information:
            https://pandas.pydata.org/docs/reference/api/pandas.read_parquet.html
        """

class ArrowData(DataInterface):
    def __init__(
        self,
        data: Optional[Any] = None,
        data_splits: Optional[Union[DataSplits, List[DataSplit]]] = None,
        dependent_vars: Optional[Union[DependentVars, List[str], List[int]]] = None,
        sql_logic: Optional[SqlLogic] = None,
        data_profile: Optional[DataProfile] = None,
    ) -> None:
        """Define a data interface

        Args:
             data (pa.Table | None):
                PyArrow Table
            dependent_vars (DependentVars | List[str] | List[int] | None):
                List of dependent variables to associate with data
            data_splits (DataSplits | List[DataSplit]):
                Optional list of `DataSplit`
            sql_logic (SqlLogic | None):
                Sql logic used to generate data represented as a dictionary.
            data_profile (DataProfile | None):
                Data profile
        """

    def save(
        self, path: Path, save_kwargs: Optional[DataSaveKwargs] = None
    ) -> DataInterfaceMetadata:
        """Saves pyarrow table to parquet via write_table

        Args:
            path (Path):
                Base path to save the data to.
            save_kwargs (DataSaveKwargs):
                Additional kwargs to pass in.

        Acceptable save kwargs:
            row_group_size (int | None):
                Maximum number of rows in each written row group. If None, the row group size will be the minimum of the
                Table size and 1024 * 1024. Default is None.
            version ({'1.0', '2.4', '2.6'}):
                Determine which Parquet logical types are available for use. Default is '2.6'.
            use_dictionary (bool | list):
                Specify if dictionary encoding should be used in general or only for some columns. Default is True.
            compression (str | dict):
                Specify the compression codec, either on a general basis or per-column.
                Valid values: {'NONE', 'SNAPPY', 'GZIP', 'BROTLI', 'LZ4', 'ZSTD'}. Default is 'snappy'.
            write_statistics (bool | list):
                Specify if statistics should be written in general or only for some columns. Default is True.
            use_deprecated_int96_timestamps (bool | None):
                Write timestamps to INT96 Parquet format. Default is None.
            coerce_timestamps (str | None):
                Cast timestamps to a particular resolution. Valid values: {None, 'ms', 'us'}. Default is None.
            allow_truncated_timestamps (bool):
                Allow loss of data when coercing timestamps to a particular resolution. Default is False.
            data_page_size (int | None):
                Set a target threshold for the approximate encoded size of data pages within a column chunk (in bytes).
                Default is None.
            flavor ({'spark'} | None):
                Sanitize schema or set other compatibility options to work with various target systems. Default is None.
            filesystem (FileSystem | None):
                Filesystem object to use when reading the parquet file. Default is None.
            compression_level (int | dict | None):
                Specify the compression level for a codec, either on a general basis or per-column. Default is None.
            use_byte_stream_split (bool | list):
                Specify if the byte_stream_split encoding should be used in general or only for some columns. Default is False.
            column_encoding (str | dict | None):
                Specify the encoding scheme on a per column basis. Default is None.
            data_page_version ({'1.0', '2.0'}):
                The serialized Parquet data page format version to write. Default is '1.0'.
            use_compliant_nested_type (bool):
                Whether to write compliant Parquet nested type (lists). Default is True.
            encryption_properties (FileEncryptionProperties | None):
                File encryption properties for Parquet Modular Encryption. Default is None.
            write_batch_size (int | None):
                Number of values to write to a page at a time. Default is None.
            dictionary_pagesize_limit (int | None):
                Specify the dictionary page size limit per row group. Default is None.
            store_schema (bool):
                By default, the Arrow schema is serialized and stored in the Parquet file metadata. Default is True.
            write_page_index (bool):
                Whether to write a page index in general for all columns. Default is False.
            write_page_checksum (bool):
                Whether to write page checksums in general for all columns. Default is False.
            sorting_columns (Sequence[SortingColumn] | None):
                Specify the sort order of the data being written. Default is None.
            store_decimal_as_integer (bool):
                Allow decimals with 1 <= precision <= 18 to be stored as integers. Default is False.
            **kwargs:
                Additional options for ParquetWriter.

        Additional Information:
            https://arrow.apache.org/docs/python/generated/pyarrow.parquet.write_table.html
        """

    def load(
        self,
        path: Path,
        metadata: DataInterfaceSaveMetadata,
        load_kwargs: Optional[DataLoadKwargs] = None,
    ) -> None:
        """Load the data from a file

        Args:
            path (Path):
                Base path to load the data from.
            metadata (DataInterfaceSaveMetadata):
                Metadata associated with the data
            load_kwargs (DataLoadKwargs):
                Additional kwargs to pass in.

        Acceptable load kwargs:
            columns (list | None):
                If not None, only these columns will be read from the file. A column name may be a prefix of a nested field,
                e.g. 'a' will select 'a.b', 'a.c', and 'a.d.e'. If empty, no columns will be read. Default is None.
            use_threads (bool):
                Perform multi-threaded column reads. Default is True.
            schema (Schema | None):
                Optionally provide the Schema for the parquet dataset, in which case it will not be inferred from the source.
                Default is None.
            use_pandas_metadata (bool):
                If True and file has custom pandas schema metadata, ensure that index columns are also loaded. Default is False.
            read_dictionary (list | None):
                List of names or column paths (for nested types) to read directly as DictionaryArray.
                Only supported for BYTE_ARRAY storage. Default is None.
            memory_map (bool):
                If the source is a file path, use a memory map to read file, which can improve performance in some environments.
                Default is False.
            buffer_size (int):
                If positive, perform read buffering when deserializing individual column chunks.
                Otherwise IO calls are unbuffered. Default is 0.
            partitioning (pyarrow.dataset.Partitioning | str | list of str):
                The partitioning scheme for a partitioned dataset. Default is 'hive'.
            filesystem (FileSystem | None):
                If nothing passed, will be inferred based on path. Default is None.
            filters (pyarrow.compute.Expression | list[tuple] | list[list[tuple]] | None):
                Rows which do not match the filter predicate will be removed from scanned data. Default is None.
            use_legacy_dataset (bool | None):
                Deprecated and has no effect from PyArrow version 15.0.0. Default is None.
            ignore_prefixes (list | None):
                Files matching any of these prefixes will be ignored by the discovery process. Default is ['.', '_'].
            pre_buffer (bool):
                Coalesce and issue file reads in parallel to improve performance on high-latency filesystems (e.g. S3).
                Default is True.
            coerce_int96_timestamp_unit (str | None):
                Cast timestamps that are stored in INT96 format to a particular resolution (e.g. 'ms'). Default is None.
            decryption_properties (FileDecryptionProperties | None):
                File-level decryption properties. Default is None.
            thrift_string_size_limit (int | None):
                If not None, override the maximum total string size allocated when decoding Thrift structures. Default is None.
            thrift_container_size_limit (int | None):
                If not None, override the maximum total size of containers allocated when decoding Thrift structures.
                Default is None.
            page_checksum_verification (bool):
                If True, verify the checksum for each page read from the file. Default is False.

        Additional Information:
            https://arrow.apache.org/docs/python/generated/pyarrow.parquet.read_table.html
        """

class TorchData(DataInterface):
    def __init__(
        self,
        data: Optional[Any] = None,
        data_splits: Optional[Union[DataSplits, List[DataSplit]]] = None,
        dependent_vars: Optional[Union[DependentVars, List[str], List[int]]] = None,
        sql_logic: Optional[SqlLogic] = None,
        data_profile: Optional[DataProfile] = None,
    ) -> None:
        """Define a data interface

        Args:
            data (torch.Tensor | None):
                Torch tensor
            dependent_vars (DependentVars | List[str] | List[int] | None):
                List of dependent variables to associate with data
            data_splits (DataSplits | List[DataSplit]):
                Optional list of `DataSplit`
            sql_logic (SqlLogic | None):
                Sql logic used to generate data represented as a dictionary.
            data_profile (DataProfile | None):
                Data profile
        """

    def save(
        self, path: Path, save_kwargs: Optional[DataSaveKwargs] = None
    ) -> DataInterfaceMetadata:
        """Saves torch tensor to a file

        Args:
            path (Path):
                Base path to save the data to.
            save_kwargs (DataSaveKwargs):
                Additional kwargs to pass in.

        Acceptable save kwargs:
            pickle_module (Any):
                Module used for pickling metadata and objects.
            pickle_protocol (int):
                Can be specified to override the default protocol.


        Additional Information:
           https://pytorch.org/docs/main/generated/torch.save.html
        """

    def load(
        self,
        path: Path,
        metadata: DataInterfaceSaveMetadata,
        load_kwargs: Optional[DataLoadKwargs] = None,
    ) -> None:
        """Load the torch tensor from file

        Args:
            path (Path):
                Base path to load the data from.
            metadata (DataInterfaceSaveMetadata):
                Metadata associated with the data
            load_kwargs (DataLoadKwargs):
                Additional kwargs to pass in.

        Acceptable load kwargs:
            map_location:
                A function, torch.device, string or a dict specifying how to remap storage locations.
            pickle_module:
                Module used for unpickling metadata and objects (has to match the pickle_module used to serialize file).
            weights_only:
                Indicates whether unpickler should be restricted to loading only tensors, primitive types,
                dictionaries and any types added via torch.serialization.add_safe_globals().
            mmap:
                Indicates whether the file should be mmaped rather than loading all the storages into memory.
                Typically, tensor storages in the file will first be moved from disk to CPU memory,
                after which they are moved to the location that they were tagged with when saving, or specified by map_location.
                This second step is a no-op if the final location is CPU. When the mmap flag is set,
                instead of copying the tensor storages from disk to CPU memory in the first step, f is mmaped.
            pickle_load_args:
                (Python 3 only) optional keyword arguments passed over to pickle_module.load() and pickle_module.Unpickler(),
                e.g., errors=....


        Additional Information:
            https://pytorch.org/docs/stable/generated/torch.load.html
        """

class SqlData:
    data_type: DataType

    def __init__(
        self,
        sql_logic: SqlLogic,
        data_profile: Optional[DataProfile] = None,
    ) -> None:
        """Define a sql data interface

        Args:
            sql (SqlLogic):
                Sql logic used to generate data represented as a dictionary.
            data_profile (DataProfile | None):
                Data profile
        """

    def save(
        self,
        path: Path,
        save_kwargs: Optional[DataSaveKwargs] = None,
    ) -> DataInterfaceMetadata:
        """Save the sql logic to a file

        Args:
            path (Path):
                The path to save the sql logic to.
            save_kwargs (DataSaveKwargs):
                Additional kwargs to pass in.
        """

def generate_feature_schema(data: Any, data_type: DataType) -> FeatureSchema:
    """Generate a feature schema

    Args:
        data:
            Data to generate the feature schema from
        data_type:
            The data type

    Returns:
        A feature map
    """

########################################################################################
#  This section contains the type definitions for opsml.model module
# __opsml.model__
# ######################################################################################
DriftProfileType = Dict[
    str, Union[SpcDriftProfile | PsiDriftProfile | CustomDriftProfile]
]

class ProcessorType:
    Preprocessor: "ProcessorType"
    Tokenizer: "ProcessorType"
    FeatureExtractor: "ProcessorType"
    ImageProcessor: "ProcessorType"

# Utils

class OnnxSchema:
    def __init__(
        self,
        input_features: FeatureSchema,
        output_features: FeatureSchema,
        onnx_version: str,
        feature_names: Optional[List[str]] = None,
    ) -> None:
        """Define an onnx schema

        Args:
            input_features (FeatureSchema):
                The input features of the onnx schema
            output_features (FeatureSchema):
                The output features of the onnx schema
            onnx_version (str):
                The onnx version of the schema
            feature_names (List[str] | None):
                The feature names and order for onnx.

        """

    def __str__(self) -> str:
        """Return a string representation of the OnnxSchema.

        Returns:
            String representation of the OnnxSchema.
        """

    @property
    def input_features(self) -> FeatureSchema:
        """Return the input features of the OnnxSchema."""

    @property
    def output_features(self) -> FeatureSchema:
        """Return the output features of the OnnxSchema."""

    @property
    def onnx_version(self) -> str:
        """Return the onnx version of the OnnxSchema."""

    @property
    def feature_names(self) -> List[str]:
        """Return the feature names and order for onnx."""

class ModelSaveKwargs:
    def __init__(
        self,
        onnx: Optional[Dict | "HuggingFaceOnnxArgs"] = None,
        model: Optional[Dict] = None,
        preprocessor: Optional[Dict] = None,
        save_onnx: bool = False,
        drift: Optional[DriftArgs] = None,
    ) -> None:
        """Optional arguments to pass to save_model

        Args:
            onnx (Dict or HuggingFaceOnnxArgs):
                Optional onnx arguments to use when saving model to onnx format
            model (Dict):
                Optional model arguments to use when saving. This is a pass-through that will
                be directly injected as kwargs to the underlying library's save method. For instance,
                pytorch models are saved with `torch.save` so any kwargs that torch.save supports can be
                used here.
            preprocessor (Dict):
                Optional preprocessor arguments to use when saving
            save_onnx (bool):
                Whether to save the onnx model. Defaults to false. This is independent of the
                onnx argument since it's possible to convert a model to onnx without additional kwargs.
                If onnx args are provided, this will be set to true.
            drift (DriftArgs):
                Optional drift args to use when saving and registering a model.
        """

    def __str__(self): ...
    def model_dump_json(self) -> str: ...
    @staticmethod
    def model_validate_json(json_string: str) -> "ModelSaveKwargs": ...

class ModelLoadKwargs:
    onnx: Optional[Dict]
    model: Optional[Dict]
    preprocessor: Optional[Dict]
    load_onnx: bool

    def __init__(
        self,
        onnx: Optional[Dict] = None,
        model: Optional[Dict] = None,
        preprocessor: Optional[Dict] = None,
        load_onnx: bool = False,
    ) -> None:
        """Optional arguments to pass to load_model

        Args:
            onnx (Dict):
                Optional onnx arguments to use when loading
            model (Dict):
                Optional model arguments to use when loading
            preprocessor (Dict):
                Optional preprocessor arguments to use when loading
            load_onnx (bool):
                Whether to load the onnx model. Defaults to false unless onnx args are
                provided. If true, the onnx model will be loaded.

        """

class ModelType:
    Transformers: "ModelType"
    SklearnPipeline: "ModelType"
    SklearnEstimator: "ModelType"
    StackingRegressor: "ModelType"
    StackingClassifier: "ModelType"
    StackingEstimator: "ModelType"
    CalibratedClassifier: "ModelType"
    LgbmRegressor: "ModelType"
    LgbmClassifier: "ModelType"
    XgbRegressor: "ModelType"
    XgbClassifier: "ModelType"
    XgbBooster: "ModelType"
    LgbmBooster: "ModelType"
    TfKeras: "ModelType"
    Pytorch: "ModelType"
    PytorchLightning: "ModelType"
    Catboost: "ModelType"
    Vowpal: "ModelType"
    Unknown: "ModelType"

class HuggingFaceORTModel:
    OrtAudioClassification: "HuggingFaceORTModel"
    OrtAudioFrameClassification: "HuggingFaceORTModel"
    OrtAudioXVector: "HuggingFaceORTModel"
    OrtCustomTasks: "HuggingFaceORTModel"
    OrtCtc: "HuggingFaceORTModel"
    OrtFeatureExtraction: "HuggingFaceORTModel"
    OrtImageClassification: "HuggingFaceORTModel"
    OrtMaskedLm: "HuggingFaceORTModel"
    OrtMultipleChoice: "HuggingFaceORTModel"
    OrtQuestionAnswering: "HuggingFaceORTModel"
    OrtSemanticSegmentation: "HuggingFaceORTModel"
    OrtSequenceClassification: "HuggingFaceORTModel"
    OrtTokenClassification: "HuggingFaceORTModel"
    OrtSeq2SeqLm: "HuggingFaceORTModel"
    OrtSpeechSeq2Seq: "HuggingFaceORTModel"
    OrtVision2Seq: "HuggingFaceORTModel"
    OrtPix2Struct: "HuggingFaceORTModel"
    OrtCausalLm: "HuggingFaceORTModel"
    OrtOptimizer: "HuggingFaceORTModel"
    OrtQuantizer: "HuggingFaceORTModel"
    OrtTrainer: "HuggingFaceORTModel"
    OrtSeq2SeqTrainer: "HuggingFaceORTModel"
    OrtTrainingArguments: "HuggingFaceORTModel"
    OrtSeq2SeqTrainingArguments: "HuggingFaceORTModel"
    OrtStableDiffusionPipeline: "HuggingFaceORTModel"
    OrtStableDiffusionInpaintPipeline: "HuggingFaceORTModel"
    OrtStableDiffusionXlPipeline: "HuggingFaceORTModel"
    OrtStableDiffusionXlImg2ImgPipeline: "HuggingFaceORTModel"
    OrtStableDiffusionImg2ImgPipeline: "HuggingFaceORTModel"

class HuggingFaceTask:
    AudioClassification: "HuggingFaceTask"
    AutomaticSpeechRecognition: "HuggingFaceTask"
    Conversational: "HuggingFaceTask"
    DepthEstimation: "HuggingFaceTask"
    DocumentQuestionAnswering: "HuggingFaceTask"
    FeatureExtraction: "HuggingFaceTask"
    FillMask: "HuggingFaceTask"
    ImageClassification: "HuggingFaceTask"
    ImageSegmentation: "HuggingFaceTask"
    ImageToImage: "HuggingFaceTask"
    ImageToText: "HuggingFaceTask"
    MaskGeneration: "HuggingFaceTask"
    ObjectDetection: "HuggingFaceTask"
    QuestionAnswering: "HuggingFaceTask"
    Summarization: "HuggingFaceTask"
    TableQuestionAnswering: "HuggingFaceTask"
    Text2TextGeneration: "HuggingFaceTask"
    TextClassification: "HuggingFaceTask"
    TextGeneration: "HuggingFaceTask"
    TextToAudio: "HuggingFaceTask"
    TokenClassification: "HuggingFaceTask"
    Translation: "HuggingFaceTask"
    TranslationXxToYy: "HuggingFaceTask"
    VideoClassification: "HuggingFaceTask"
    VisualQuestionAnswering: "HuggingFaceTask"
    ZeroShotClassification: "HuggingFaceTask"
    ZeroShotImageClassification: "HuggingFaceTask"
    ZeroShotAudioClassification: "HuggingFaceTask"
    ZeroShotObjectDetection: "HuggingFaceTask"
    Undefined: "HuggingFaceTask"

class HuggingFaceOnnxArgs:
    ort_type: HuggingFaceORTModel
    provider: str
    quantize: bool
    export: bool
    config: Optional[Any]
    extra_kwargs: Optional[Dict[str, Any]]

    def __init__(
        self,
        ort_type: HuggingFaceORTModel,
        provider: str,
        quantize: bool = False,
        config: Optional[Any] = None,
        extra_kwargs: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Optional Args to use with a huggingface model

        Args:
            ort_type:
                Optimum onnx class name
            provider:
                Onnx runtime provider to use
            config:
                Optional optimum config to use
            quantize:
                Whether to quantize the model
            extra_kwargs:
                Extra kwargs to pass to the onnx conversion (save_pretrained method for ort models)

        """

class DataProcessor:
    """Generic class that holds uri information for data preprocessors and postprocessors"""

    name: str
    uri: Path
    type: ProcessorType

    def __init__(self, name: str, uri: Path) -> None:
        """Define a data processor

        Args:
            name:
                Name of the data processor
            uri:
                Path to the data processor
        """

    def __str__(self): ...

# Define interface save and metadata arguments
class ModelInterfaceSaveMetadata:
    model_uri: Path
    data_processor_map: Dict[str, DataProcessor]
    sample_data_uri: Path
    onnx_model_uri: Optional[Path]
    drift_profile_uri_map: Optional[Dict[str, DriftProfileUri]]
    extra: Optional[ExtraMetadata]
    save_kwargs: Optional[ModelSaveKwargs]

    def __init__(
        self,
        model_uri: Path,
        data_processor_map: Optional[Dict[str, DataProcessor]] = {},  # type: ignore
        sample_data_uri: Optional[Path] = None,
        onnx_model_uri: Optional[Path] = None,
        drift_profile_uri_map: Optional[Dict[str, DriftProfileUri]] = None,
        extra: Optional[ExtraMetadata] = None,
        save_kwargs: Optional[ModelSaveKwargs] = None,
    ) -> None:
        """Define model interface save arguments

        Args:
            model_uri:
                Path to the model
            data_processor_map:
                Dictionary of data processors
            sample_data_uri:
                Path to the sample data
            onnx_model_uri:
                Path to the onnx model
            drift_profile_uri_map:
                Dictionary of drift profiles
            extra_metadata:
                Extra metadata
            save_kwargs:
                Optional save args
        """

    def __str__(self): ...
    def model_dump_json(self) -> str: ...

class ModelInterfaceType:
    Base: "ModelInterfaceType"
    Sklearn: "ModelInterfaceType"
    CatBoost: "ModelInterfaceType"
    HuggingFace: "ModelInterfaceType"
    LightGBM: "ModelInterfaceType"
    Lightning: "ModelInterfaceType"
    Torch: "ModelInterfaceType"
    TensorFlow: "ModelInterfaceType"
    VowpalWabbit: "ModelInterfaceType"
    XGBoost: "ModelInterfaceType"

class TaskType:
    Classification: "TaskType"
    Regression: "TaskType"
    Clustering: "TaskType"
    AnomalyDetection: "TaskType"
    TimeSeries: "TaskType"
    Forecasting: "TaskType"
    Recommendation: "TaskType"
    Ranking: "TaskType"
    NLP: "TaskType"
    Image: "TaskType"
    Audio: "TaskType"
    Video: "TaskType"
    Graph: "TaskType"
    Tabular: "TaskType"
    TimeSeriesForecasting: "TaskType"
    TimeSeriesAnomalyDetection: "TaskType"
    TimeSeriesClassification: "TaskType"
    TimeSeriesRegression: "TaskType"
    TimeSeriesClustering: "TaskType"
    TimeSeriesRecommendation: "TaskType"
    TimeSeriesRanking: "TaskType"
    TimeSeriesNLP: "TaskType"
    TimeSeriesImage: "TaskType"
    TimeSeriesAudio: "TaskType"
    TimeSeriesVideo: "TaskType"
    TimeSeriesGraph: "TaskType"
    TimeSeriesTabular: "TaskType"
    Undefined: "TaskType"

class OnnxSession:
    @property
    def schema(self) -> OnnxSchema:
        """Returns the onnx schema"""

    @property
    def session(self) -> Any:
        """Returns the onnx session"""

    @session.setter
    def session(self, session: Any) -> None:
        """Sets the onnx session

        Args:
            session:
                Onnx session
        """

    def run(
        self,
        input_feed: Dict[str, Any],
        output_names: Optional[list[str]] = None,
        run_options: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Run the onnx session

        Args:
            input_feed:
                Dictionary of input data
            output_names:
                List of output names
            run_options:
                Optional run options

        Returns:
            Output data
        """

    def model_dump_json(self) -> str:
        """Dump the onnx model to json"""

    @staticmethod
    def model_validate_json(json_string: str) -> "OnnxSession":
        """Validate the onnx model json"""

class ModelInterfaceMetadata:
    task_type: TaskType
    model_type: ModelType
    data_type: DataType
    onnx_session: Optional[OnnxSession]
    schema: FeatureSchema
    save_metadata: ModelInterfaceSaveMetadata
    extra_metadata: dict[str, str]
    version: str

    def __init__(
        self,
        save_metadata: ModelInterfaceSaveMetadata,
        task_type: TaskType = TaskType.Undefined,
        model_type: ModelType = ModelType.Unknown,
        data_type: DataType = DataType.NotProvided,
        schema: FeatureSchema = FeatureSchema(),
        onnx_session: Optional[OnnxSession] = None,
        extra_metadata: dict[str, str] = {},  # type: ignore
        version: str = "undefined",
    ) -> None:
        """Define a model interface

        Args:
            task_type:
                Task type
            model_type:
                Model type
            data_type:
                Data type
            onnx_session:
                Onnx session
            schema:
                Feature schema
            data_type:
                Sample data type
            save_metadata:
                Save metadata
            extra_metadata:
                Extra metadata. Must be a dictionary of strings
            version:
                Package version of the model being used (sklearn.__version__, torch.__version__, etc)
        """

    def __str__(self) -> str:
        """Return the string representation of the model interface metadata"""

    def model_dump_json(self) -> str:
        """Dump the model interface metadata to json"""

    @staticmethod
    def model_validate_json(json_string: str) -> "ModelInterfaceMetadata":
        """Validate the model interface metadata json"""

class ModelInterface:
    def __init__(
        self,
        model: Any = None,
        sample_data: Any = None,
        task_type: Optional[TaskType] = None,
        drift_profile: Optional[DriftProfileType] = None,
    ) -> None:
        """Base class for ModelInterface

        Args:
            model:
                Model to associate with interface.
            sample_data:
                Sample data to use to make predictions
            task_type:
                The type of task the model performs
            drift_profile:
                Drift profile(s) to associate with the model. Must be a dictionary of
                alias and drift profile.
        """

    @property
    def model(self) -> None | Any:
        """Returns the model"""

    @model.setter
    def model(self, model: Any) -> None:
        """Sets the model"""

    @property
    def sample_data(self) -> None | Any:
        """Returns the sample data"""

    @sample_data.setter
    def sample_data(self, sample_data: Any) -> None:
        """Sets the sample data"""

    @property
    def data_type(self) -> DataType:
        """Returns the task type"""

    @property
    def task_type(self) -> TaskType:
        """Returns the task type"""

    @property
    def schema(self) -> FeatureSchema:
        """Returns the feature schema"""

    @property
    def model_type(self) -> ModelType:
        """Returns the model type"""

    @property
    def interface_type(self) -> ModelInterfaceType:
        """Returns the model type"""

    @property
    def drift_profile(
        self,
    ) -> DriftProfileMap:
        """Returns the drift profile mapping"""

    @property
    def onnx_session(self) -> None | OnnxSession:
        """Returns the onnx session if it exists"""

    @onnx_session.setter
    def onnx_session(self, session: None | OnnxSession) -> None:
        """Sets the onnx session


        Args:
            session:
                Onnx session
        """

    @overload
    def create_drift_profile(
        self,
        alias: str,
        data: CustomMetric | List[CustomMetric],
        config: CustomMetricDriftConfig,
        data_type: Optional[DataType] = None,
    ) -> CustomDriftProfile: ...
    @overload
    def create_drift_profile(
        self,
        alias: str,
        data: Any,
        config: SpcDriftConfig,
        data_type: Optional[DataType] = None,
    ) -> SpcDriftProfile: ...
    @overload
    def create_drift_profile(
        self,
        alias: str,
        data: Any,
        config: PsiDriftConfig,
        data_type: Optional[DataType] = None,
    ) -> PsiDriftProfile: ...
    @overload
    def create_drift_profile(
        self,
        alias: str,
        data: Any,
        data_type: Optional[DataType] = None,
    ) -> SpcDriftProfile: ...
    def create_drift_profile(  # type: ignore
        self,
        alias: str,
        data: Any,
        config: None | SpcDriftConfig | PsiDriftConfig | CustomMetricDriftConfig = None,
        data_type: None | DataType = None,
    ) -> Any:
        """Create a drift profile and append it to the drift profile list

        Args:
            alias:
                Alias to use for the drift profile
            data:
                Data to use to create the drift profile. Can be a pandas dataframe,
                polars dataframe, pyarrow table or numpy array.
            config:
                Drift config to use. If None, defaults to SpcDriftConfig.
            data_type:
                Data type to use. If None, data_type will be inferred from the data.

        Returns:
            Drift profile SPcDriftProfile, PsiDriftProfile or CustomDriftProfile
        """

    def save(
        self,
        path: Path,
        save_kwargs: None | ModelSaveKwargs = None,
    ) -> ModelInterfaceMetadata:
        """Save the model interface

        Args:
            path (Path):
                Path to save the model
            save_kwargs (ModelSaveKwargs):
                Optional kwargs to pass to the various underlying methods. This is a passthrough object meaning
                that the kwargs will be passed to the underlying methods as is and are expected to be supported by
                the underlying library.

                - model: Kwargs that will be passed to save_model. See save_model for more details.
                - preprocessor: Kwargs that will be passed to save_preprocessor
                - onnx: Library specific kwargs to pass to the onnx conversion. Independent of save_onnx.
                - save_onnx: Whether to save the onnx model. Defaults to false.
        """

    def load(
        self,
        path: Path,
        metadata: ModelInterfaceSaveMetadata,
        load_kwargs: None | ModelLoadKwargs = None,
    ) -> None:
        """Load ModelInterface components

        Args:
            path (Path):
                Path to load the model
            metadata (ModelInterfaceSaveMetadata):
                Metadata to use to load the model
            load_kwargs (ModelLoadKwargs):
                Optional load kwargs to pass to the different load methods
        """

    @staticmethod
    def from_metadata(metadata: ModelInterfaceMetadata) -> "ModelInterface":
        """Create a ModelInterface from metadata

        Args:
            metadata:
                Model interface metadata

        Returns:
            Model interface
        """

class SklearnModel(ModelInterface):
    """OpsML interface for scikit-learn models"""

    def __init__(
        self,
        model: Optional[Any] = None,
        preprocessor: Optional[Any] = None,
        sample_data: Optional[Any] = None,
        task_type: Optional[TaskType] = None,
        drift_profile: Optional[DriftProfileType] = None,
    ) -> None:
        """Instantiate an SklearnModel interface

        Args:
            model:
                Model to associate with interface. This model must be from the
                scikit-learn ecosystem
            preprocessor:
                Preprocessor to associate with the model. This preprocessor must be from the
                scikit-learn ecosystem
            sample_data:
                Sample data to use to make predictions
            task_type:
                The type of task the model performs
            drift_profile:
                Drift profile(s) to associate with the model. Must be a dictionary of
                alias and drift profile.
        """

    @property
    def preprocessor(self) -> Optional[Any]:
        """Returns the preprocessor"""

    @preprocessor.setter
    def preprocessor(self, preprocessor: Any) -> None:
        """Sets the preprocessor

        Args:
            preprocessor:
                Preprocessor to associate with the model. This preprocessor must be from the
                scikit-learn ecosystem
        """

    @property
    def preprocessor_name(self) -> Optional[str]:
        """Returns the preprocessor name"""

class LightGBMModel(ModelInterface):
    def __init__(
        self,
        model: Optional[Any] = None,
        preprocessor: Optional[Any] = None,
        sample_data: Optional[Any] = None,
        task_type: Optional[TaskType] = None,
        drift_profile: Optional[DriftProfileType] = None,
    ) -> None:
        """Instantiate a LightGBMModel interface

        Args:
            model:
                Model to associate with interface. This model must be a lightgbm booster.
            preprocessor:
                Preprocessor to associate with the model.
            sample_data:
                Sample data to use to make predictions
            task_type:
                The type of task the model performs
            drift_profile:
                Drift profile(s) to associate with the model. Must be a dictionary of
                alias and drift profile.
        """

    @property
    def preprocessor(self) -> Optional[Any]:
        """Returns the preprocessor"""

    @preprocessor.setter
    def preprocessor(self, preprocessor: Any) -> None:
        """Sets the preprocessor

        Args:
            preprocessor:
                Preprocessor to associate with the model. This preprocessor must be from the
                scikit-learn ecosystem
        """

    @property
    def preprocessor_name(self) -> Optional[str]:
        """Returns the preprocessor name"""

class XGBoostModel(ModelInterface):
    def __init__(
        self,
        model: Optional[Any] = None,
        preprocessor: Optional[Any] = None,
        sample_data: Optional[Any] = None,
        task_type: Optional[TaskType] = None,
        drift_profile: Optional[DriftProfileType] = None,
    ) -> None:
        """Interface for saving XGBoost Booster models

        Args:
            model:
                Model to associate with interface. This model must be an xgboost booster.
            preprocessor:
                Preprocessor to associate with the model.
            sample_data:
                Sample data to use to make predictions.
            task_type:
                The type of task the model performs
            drift_profile:
                Drift profile(s) to associate with the model. Must be a dictionary of
                alias and drift profile.
        """

    @property
    def preprocessor(self) -> Optional[Any]:
        """Returns the preprocessor"""

    @preprocessor.setter
    def preprocessor(self, preprocessor: Any) -> None:
        """Sets the preprocessor

        Args:
            preprocessor:
                Preprocessor to associate with the model. This preprocessor must be from the
                scikit-learn ecosystem
        """

    @property
    def preprocessor_name(self) -> Optional[str]:
        """Returns the preprocessor name"""

class TorchModel(ModelInterface):
    def __init__(
        self,
        model: Optional[Any] = None,
        preprocessor: Optional[Any] = None,
        sample_data: Optional[Any] = None,
        task_type: Optional[TaskType] = None,
        drift_profile: Optional[DriftProfileType] = None,
    ) -> None:
        """Interface for saving PyTorch models

        Args:
            model:
                Model to associate with interface. This model must inherit from torch.nn.Module.
            preprocessor:
                Preprocessor to associate with model.
            sample_data:
                Sample data to use to convert to ONNX and make sample predictions. This data must be a
                pytorch-supported type. TorchData interface, torch tensor, torch dataset, Dict[str, torch.Tensor],
                List[torch.Tensor], Tuple[torch.Tensor].
            task_type:
                The intended task type of the model.
            drift_profile:
                Drift profile(s) to associate with the model. Must be a dictionary of
                alias and drift profile.
        """

    @property
    def preprocessor(self) -> Optional[Any]:
        """Returns the preprocessor"""

    @preprocessor.setter
    def preprocessor(self, preprocessor: Any) -> None:
        """Sets the preprocessor

        Args:
            preprocessor:
                Preprocessor to associate with the model. This preprocessor must be from the
                scikit-learn ecosystem
        """

    @property
    def preprocessor_name(self) -> Optional[str]:
        """Returns the preprocessor name"""

    def save(
        self,
        path: Path,
        save_kwargs: None | ModelSaveKwargs = None,
    ) -> ModelInterfaceMetadata:
        """Save the TorchModel interface. Torch models are saved
        as state_dicts as is the standard for PyTorch.

        Args:
            path (Path):
                Base path to save artifacts
            save_kwargs (ModelSaveKwargs):
                Optional kwargs to pass to the various underlying methods. This is a passthrough object meaning
                that the kwargs will be passed to the underlying methods as is and are expected to be supported by
                the underlying library.
        """

class LightningModel(ModelInterface):
    def __init__(
        self,
        trainer: Optional[Any] = None,
        preprocessor: Optional[Any] = None,
        sample_data: Optional[Any] = None,
        task_type: Optional[TaskType] = None,
        drift_profile: Optional[DriftProfileType] = None,
    ) -> None:
        """Interface for saving PyTorch Lightning models

        Args:
            trainer:
                Pytorch lightning trainer to associate with interface.
            preprocessor:
                Preprocessor to associate with model.
            sample_data:
                Sample data to use to convert to ONNX and make sample predictions. This data must be a
                pytorch-supported type. TorchData interface, torch tensor, torch dataset, Dict[str, torch.Tensor],
                List[torch.Tensor], Tuple[torch.Tensor].
            task_type:
                The intended task type of the model.
            drift_profile:
                Drift profile(s) to associate with the model. Must be a dictionary of
                alias and drift profile.
        """

    @property
    def trainer(self) -> None:
        """Returns the trainer"""

    @trainer.setter
    def trainer(self, trainer: Any) -> None:
        """Sets the trainer"""

    @property
    def preprocessor(self) -> Optional[Any]:
        """Returns the preprocessor"""

    @preprocessor.setter
    def preprocessor(self, preprocessor: Any) -> None:
        """Sets the preprocessor

        Args:
            preprocessor:
                Preprocessor to associate with the model. This preprocessor must be from the
                scikit-learn ecosystem
        """

    @property
    def preprocessor_name(self) -> Optional[str]:
        """Returns the preprocessor name"""

    def save(
        self,
        path: Path,
        save_kwargs: None | ModelSaveKwargs = None,
    ) -> ModelInterfaceMetadata:
        """Save the LightningModel interface. Lightning models are saved via checkpoints.

        Args:
            path (Path):
                Base path to save artifacts
            save_kwargs (ModelSaveKwargs):
                Optional kwargs to pass to the various underlying methods. This is a passthrough object meaning
                that the kwargs will be passed to the underlying methods as is and are expected to be supported by
                the underlying library.

                - model: Kwargs that will be passed to save_model. See save_model for more details.
                - preprocessor: Kwargs that will be passed to save_preprocessor
                - onnx: Library specific kwargs to pass to the onnx conversion. Independent of save_onnx.
                - save_onnx: Whether to save the onnx model. Defaults to false.
        """

class HuggingFaceModel(ModelInterface):
    def __init__(
        self,
        model: Optional[Any] = None,
        tokenizer: Optional[Any] = None,
        feature_extractor: Optional[Any] = None,
        image_processor: Optional[Any] = None,
        sample_data: Optional[Any] = None,
        hf_task: Optional[HuggingFaceTask] = None,
        task_type: Optional[TaskType] = None,
        drift_profile: Optional[DriftProfileType] = None,
    ) -> None:
        """Interface for saving HuggingFace models and pipelines

        Args:
            model:
                Model to associate with interface. This can be a HuggingFace pipeline (inherits from Pipeline),
                or a HuggingFace model (inherits from PreTrainedModel or TFPreTrainedModel).
            tokenizer:
                Tokenizer to associate with the model. This must be a HuggingFace tokenizer (PreTrainedTokenizerBase).
                If using a pipeline that already has a tokenizer, this can be None.
            feature_extractor:
                Feature extractor to associate with the model. This must be a HuggingFace feature extractor
                (PreTrainedFeatureExtractor). If using a pipeline that already has a feature extractor,
                this can be None.
            image_processor:
                Image processor to associate with the model. This must be a HuggingFace image processor
                (BaseImageProcessor). If using a pipeline that already has an image processor,
                this can be None.
            sample_data:
                Sample data to use to convert to ONNX and make sample predictions. This data must be a
                HuggingFace-supported type.
            hf_task:
                HuggingFace task to associate with the model. Defaults to Undefined.
                Accepted tasks are as follows (taken from HuggingFace pipeline docs):
                    - `"audio-classification"`: will return a [`AudioClassificationPipeline`].
                    - `"automatic-speech-recognition"`: will return a [`AutomaticSpeechRecognitionPipeline`].
                    - `"depth-estimation"`: will return a [`DepthEstimationPipeline`].
                    - `"document-question-answering"`: will return a [`DocumentQuestionAnsweringPipeline`].
                    - `"feature-extraction"`: will return a [`FeatureExtractionPipeline`].
                    - `"fill-mask"`: will return a [`FillMaskPipeline`]:.
                    - `"image-classification"`: will return a [`ImageClassificationPipeline`].
                    - `"image-feature-extraction"`: will return an [`ImageFeatureExtractionPipeline`].
                    - `"image-segmentation"`: will return a [`ImageSegmentationPipeline`].
                    - `"image-text-to-text"`: will return a [`ImageTextToTextPipeline`].
                    - `"image-to-image"`: will return a [`ImageToImagePipeline`].
                    - `"image-to-text"`: will return a [`ImageToTextPipeline`].
                    - `"mask-generation"`: will return a [`MaskGenerationPipeline`].
                    - `"object-detection"`: will return a [`ObjectDetectionPipeline`].
                    - `"question-answering"`: will return a [`QuestionAnsweringPipeline`].
                    - `"summarization"`: will return a [`SummarizationPipeline`].
                    - `"table-question-answering"`: will return a [`TableQuestionAnsweringPipeline`].
                    - `"text2text-generation"`: will return a [`Text2TextGenerationPipeline`].
                    - `"text-classification"` (alias `"sentiment-analysis"` available): will return a
                    [`TextClassificationPipeline`].
                    - `"text-generation"`: will return a [`TextGenerationPipeline`]:.
                    - `"text-to-audio"` (alias `"text-to-speech"` available): will return a [`TextToAudioPipeline`]:.
                    - `"token-classification"` (alias `"ner"` available): will return a [`TokenClassificationPipeline`].
                    - `"translation"`: will return a [`TranslationPipeline`].
                    - `"translation_xx_to_yy"`: will return a [`TranslationPipeline`].
                    - `"video-classification"`: will return a [`VideoClassificationPipeline`].
                    - `"visual-question-answering"`: will return a [`VisualQuestionAnsweringPipeline`].
                    - `"zero-shot-classification"`: will return a [`ZeroShotClassificationPipeline`].
                    - `"zero-shot-image-classification"`: will return a [`ZeroShotImageClassificationPipeline`].
                    - `"zero-shot-audio-classification"`: will return a [`ZeroShotAudioClassificationPipeline`].
                    - `"zero-shot-object-detection"`: will return a [`ZeroShotObjectDetectionPipeline`].
            task_type:
                The intended task type for the model. Note: This is the OpsML task type, not the HuggingFace task type.
            drift_profile:
                Drift profile(s) to associate with the model. Must be a dictionary of
                alias and drift profile.
        """

    def save(
        self,
        path: Path,
        save_kwargs: None | ModelSaveKwargs = None,
    ) -> ModelInterfaceMetadata:
        """Save the HuggingFaceModel interface

        Args:
            path (Path):
                Base path to save artifacts
            save_kwargs (ModelSaveKwargs):
                Optional kwargs to pass to the various underlying methods. This is a passthrough object meaning
                that the kwargs will be passed to the underlying methods as is and are expected to be supported by
                the underlying library.

                - model: Kwargs that will be passed to save_model. See save_model for more details.
                - preprocessor: Kwargs that will be passed to save_preprocessor
                - onnx: Kwargs that will be passed when saving the onnx model
                    - For the HuggingFaceModel, this should be an instance of HuggingFaceOnnxArgs
                - save_onnx: Whether to save the onnx model. Defaults to false.
        """

    @property
    def model(self) -> Optional[Any]:
        """Returns as HuggingFace model (PreTrainedModel, TFPreTrainedModel).
        Can be None if the model is a pipeline.
        """

    @model.setter
    def model(self, model: Any) -> None:
        """Sets the model

        Args:
            model:
                Model to associate with the interface. This must be a HuggingFace model (PreTrainedModel, TFPreTrainedModel).
                If using a pipeline that already has a model, this can be None.
        """

    @property
    def tokenizer(self) -> Optional[Any]:
        """Returns the tokenizer. Can be None if the model is a pipeline.
        If present, will be of type PreTrainedTokenizerBase
        """

    @tokenizer.setter
    def tokenizer(self, tokenizer: Any) -> None:
        """Sets the tokenizer

        Args:
            tokenizer:
                Tokenizer to associate with the model. This must be a HuggingFace tokenizer (PreTrainedTokenizerBase).
                If using a pipeline that already has a tokenizer, this can be None.
        """

    @property
    def image_processor(self) -> Optional[Any]:
        """Returns the image processor. Can be None if the model is a pipeline.
        If present, will be of type BaseImageProcessor
        """

    @image_processor.setter
    def image_processor(self, image_processor: Any) -> None:
        """Sets the image processor

        Args:
            image_processor:
                Image processor to associate with the model. This must be a HuggingFace image processor
                (BaseImageProcessor). If using a pipeline that already has an image processor,
                this can be None.
        """

    @property
    def feature_extractor(self) -> Optional[Any]:
        """Returns the feature extractor. Can be None if the model is a pipeline.
        If present, will be of type PreTrainedFeatureExtractor
        """

    @feature_extractor.setter
    def feature_extractor(self, feature_extractor: Any) -> None:
        """Sets the feature extractor

        Args:
            feature_extractor:
                Feature extractor to associate with the model. This must be a HuggingFace feature extractor
                (PreTrainedFeatureExtractor). If using a pipeline that already has a feature extractor,
                this can be None.
        """

class CatBoostModel(ModelInterface):
    def __init__(
        self,
        model: Optional[Any] = None,
        preprocessor: Optional[Any] = None,
        sample_data: Optional[Any] = None,
        task_type: Optional[TaskType] = None,
        drift_profile: Optional[DriftProfileType] = None,
    ) -> None:
        """Interface for saving CatBoost models

        Args:
            model:
                Model to associate with the interface. This model must be a CatBoost model.
            preprocessor:
                Preprocessor to associate with the model.
            sample_data:
                Sample data to use to make predictions.
            task_type:
                The type of task the model performs
            drift_profile:
                Drift profile(s) to associate with the model. Must be a dictionary of
                alias and drift profile.
        """

    @property
    def preprocessor(self) -> Optional[Any]:
        """Returns the preprocessor"""

    @preprocessor.setter
    def preprocessor(self, preprocessor: Any) -> None:
        """Sets the preprocessor

        Args:
            preprocessor:
                Preprocessor to associate with the model. This preprocessor must be from the
                scikit-learn ecosystem
        """

    @property
    def preprocessor_name(self) -> Optional[str]:
        """Returns the preprocessor name"""

class TensorFlowModel(ModelInterface):
    def __init__(
        self,
        model: Optional[Any] = None,
        preprocessor: Optional[Any] = None,
        sample_data: Optional[Any] = None,
        task_type: Optional[TaskType] = None,
        drift_profile: Optional[DriftProfileType] = None,
    ) -> None:
        """Interface for saving PyTorch models

        Args:
            model:
                Model to associate with interface. This model must inherit from tensorflow.keras.Model
            preprocessor:
                Preprocessor to associate with model.
            sample_data:
                Sample data to use to convert to ONNX and make sample predictions. This data must be a
                tensorflow-supported type. numpy array, tf.Tensor, torch dataset, Dict[str, tf.Tensor],
                List[tf.Tensor], Tuple[tf.Tensor].
            task_type:
                The intended task type of the model.
            drift_profile:
                Drift profile(s) to associate with the model. Must be a dictionary of
                alias and drift profile.
        """

    @property
    def preprocessor(self) -> Optional[Any]:
        """Returns the preprocessor"""

    @preprocessor.setter
    def preprocessor(self, preprocessor: Any) -> None:
        """Sets the preprocessor

        Args:
            preprocessor:
                Preprocessor to associate with the model
        """

    @property
    def preprocessor_name(self) -> Optional[str]:
        """Returns the preprocessor name"""

class OnnxModel(ModelInterface):
    def __init__(
        self,
        model: Optional[Any] = None,
        sample_data: Optional[Any] = None,
        task_type: Optional[TaskType] = None,
        drift_profile: Optional[DriftProfileType] = None,
    ) -> None:
        """Interface for saving an OnnxModel

        Args:
            model:
                Onnx model to associate with the interface. This model must be an Onnx ModelProto
            sample_data:
                Sample data to use to make predictions
            task_type:
                The type of task the model performs
            drift_profile:
                Drift profile(s) to associate with the model. Must be a dictionary of
                alias and drift profile.

        Example:
            ```python
            from sklearn.datasets import load_iris  # type: ignore
            from sklearn.model_selection import train_test_split  # type: ignore
            from sklearn.ensemble import RandomForestClassifier  # type: ignore
            from skl2onnx import to_onnx  # type: ignore
            import onnxruntime as rt  # type: ignore

            iris = load_iris()

            X, y = iris.data, iris.target
            X = X.astype(np.float32)
            X_train, X_test, y_train, y_test = train_test_split(X, y)
            clr = RandomForestClassifier()
            clr.fit(X_train, y_train)

            onx = to_onnx(clr, X[:1])

            interface = OnnxModel(model=onx, sample_data=X_train)
            ```
        """

    @property
    def session(self) -> OnnxSession:
        """Returns the onnx session. This will error if the OnnxSession is not set"""

########################################################################################
#  This section contains the type definitions for opsml.card module
# __opsml.card__
# ######################################################################################

class ServiceType:
    """
    Enum representing the type of service.

    Attributes:
        Api: REST API service
        Mcp: Model Context Protocol service
        Agent: Agentic workflow service
    """

    Api: "ServiceType"
    Mcp: "ServiceType"
    Agent: "ServiceType"

class RegistryType:
    Data: "RegistryType"
    Model: "RegistryType"
    Experiment: "RegistryType"
    Audit: "RegistryType"
    Prompt: "RegistryType"
    Service: "RegistryType"

class RegistryMode:
    Client: "RegistryMode"
    Server: "RegistryMode"

class CardRecord:
    uid: Optional[str]
    created_at: Optional[str]
    app_env: Optional[str]
    name: str
    space: str
    version: str
    tags: Dict[str, str]
    datacard_uids: Optional[List[str]]
    modelcard_uids: Optional[List[str]]
    experimentcard_uids: Optional[List[str]]
    auditcard_uid: Optional[str]
    interface_type: Optional[str]
    data_type: Optional[str]
    model_type: Optional[str]
    task_type: Optional[str]

    def __str__(self) -> str:
        """Return a string representation of the Card.

        Returns:
            String representation of the Card.
        """

class CardList:
    cards: List[CardRecord]

    def __getitem__(self, key: int) -> Optional[CardRecord]:
        """Return the card at the specified index"""

    def __iter__(self) -> CardRecord:
        """Return an iterator for the card list"""

    def as_table(self) -> None:
        """Print cards as a table"""

    def __len__(self) -> int:
        """Return the length of the card list"""

# Registry

class DataCard:
    def __init__(  # pylint: disable=dangerous-default-value
        self,
        interface: Optional[DataInterface] = None,
        space: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
        uid: Optional[str] = None,
        tags: List[str] = [],
    ) -> None:
        """Define a data card

        Args:
            interface (DataInterface | None):
                The data interface
            space (str | None):
                The space of the card
            name (str | None):
                The name of the card
            version (str | None):
                The version of the card
            uid (str | None):
                The uid of the card
            tags (List[str]):
                The tags of the card

        Example:
        ```python
        from opsml import DataCard, CardRegistry, RegistryType, PandasData

        # for testing purposes
        from opsml.helpers.data import create_fake_data

        # pandas data
        X, _ = create_fake_data(n_samples=1200)

        interface = PandasData(data=X)
        datacard = DataCard(
            interface=interface,
            space="my-repo",
            name="my-name",
            tags=["foo:bar", "baz:qux"],
        )

        # register card
        registry = CardRegistry(RegistryType.Data)
        registry.register_card(datacard)
        ```
        """

    @property
    def data(self) -> Any:
        """Return the data. This is a special property that is used to
        access the data from the interface. It is not settable. It will also
        raise an error if the interface is not set or if the data
        has not been loaded.
        """

    @property
    def experimentcard_uid(self) -> Optional[str]:
        """Return the experimentcard uid"""

    @experimentcard_uid.setter
    def experimentcard_uid(self, experimentcard_uid: Optional[str]) -> None:
        """Set the experimentcard uid"""

    @property
    def interface(self) -> Optional[DataInterface]:
        """Return the data interface"""

    @interface.setter
    def interface(self, interface: Any) -> None:
        """Set the data interface

        Args:
            interface (DataInterface):
                The data interface to set. Must inherit from DataInterface
        """

    @property
    def app_env(self) -> str:
        """Returns the app env"""

    @property
    def created_at(self) -> datetime:
        """Returns the created at timestamp"""

    @property
    def name(self) -> str:
        """Return the name of the data card"""

    @name.setter
    def name(self, name: str) -> None:
        """Set the name of the data card

        Args:
            name (str):
                The name of the data card
        """

    @property
    def space(self) -> str:
        """Return the space of the data card"""

    @space.setter
    def space(self, space: str) -> None:
        """Set the space of the data card

        Args:
            space (str):
                The space of the data card
        """

    @property
    def version(self) -> str:
        """Return the version of the data card"""

    @version.setter
    def version(self, version: str) -> None:
        """Set the version of the data card

        Args:
            version (str):
                The version of the data card
        """

    @property
    def uid(self) -> str:
        """Return the uid of the data card"""

    @property
    def tags(self) -> List[str]:
        """Return the tags of the data card"""

    @tags.setter
    def tags(self, tags: List[str]) -> None:
        """Set the tags of the data card

        Args:
            tags (List[str]):
                The tags of the data card
        """

    @property
    def metadata(self) -> "DataCardMetadata":  # pylint: disable=used-before-assignment
        """Return the metadata of the data card"""

    @property
    def registry_type(self) -> RegistryType:
        """Return the card type of the data card"""

    @property
    def data_type(self) -> DataType:
        """Return the data type"""

    def save(
        self,
        path: Path,
        save_kwargs: Optional[DataSaveKwargs] = None,
    ) -> None:
        """Save the data card

        Args:
            path (Path):
                The path to save the data card to
            save_kwargs (DataSaveKwargs | None):
                Optional save kwargs to that will be passed to the
                data interface save method

        Acceptable save kwargs:
            Kwargs are passed to the underlying data interface for saving.
            For a complete list of options see the save method of the data interface and
            their associated libraries.
        """

    def load(
        self,
        path: Optional[Path] = None,
        load_kwargs: Optional[DataLoadKwargs] = None,
    ) -> None:
        """Load the data card

        Args:
            path (Path | None):
                The path to load the data card from. If no path is provided,
                the data interface will be loaded from the server.
            load_kwargs (DataLoadKwargs | None):
                Optional load kwargs to that will be passed to the
                data interface load method
        """

    def download_artifacts(self, path: Optional[Path] = None) -> None:
        """Download artifacts associated with the DataCard

        Args:
            path (Path):
                Path to save the artifacts. If not provided, the artifacts will be saved
                to a directory called "card_artifacts"
        """

    def model_dump_json(self) -> str:
        """Return the model dump as a json string"""

    @staticmethod
    def model_validate_json(
        json_string: str, interface: Optional[DataInterface] = None
    ) -> "ModelCard":
        """Validate the model json string

        Args:
            json_string (str):
                The json string to validate
            interface (DataInterface):
                By default, the interface will be inferred and instantiated
                from the interface metadata. If an interface is provided
                (as in the case of custom interfaces), it will be used.
        """

    def create_data_profile(
        self,
        bin_size: Optional[int] = 20,
        compute_correlations: Optional[bool] = False,
    ) -> DataProfile:
        """Create a data profile


        Args:
            bin_size (int):
                The bin size for the data profile
            compute_correlations (bool):
                Whether to compute correlations
        """

    def split_data(self) -> Dict[str, Data]:
        """Split the data according to the data splits defined in the interface

        Returns:
            Dict[str, Any]:
                A dictionary containing the split data
        """

class DataCardMetadata:
    @property
    def schema(self) -> FeatureSchema:
        """Return the feature map"""

    @property
    def experimentcard_uid(self) -> Optional[str]:
        """Return the experimentcard uid"""

    @property
    def auditcard_uid(self) -> Optional[str]:
        """Return the experimentcard uid"""

class ModelCardMetadata:
    def __init__(
        self,
        datacard_uid: Optional[str] = None,
        experimentcard_uid: Optional[str] = None,
        auditcard_uid: Optional[str] = None,
    ) -> None:
        """Create a ModelCardMetadata object

        Args:
            datacard_uid (str | None):
                The datacard uid
            experimentcard_uid (str | None):
                The experimentcard uid
            auditcard_uid (str | None):
                The auditcard uid
        """

    @property
    def datacard_uid(self) -> str:
        """Returns the datacard uid"""

    @datacard_uid.setter
    def datacard_uid(self, datacard_uid: str) -> None:
        """Set the datacard uid"""

    @property
    def experimentcard_uid(self) -> str:
        """Returns the experimentcard uid"""

    @experimentcard_uid.setter
    def experimentcard_uid(self, experimentcard_uid: str) -> None:
        """Set the experimentcard uid"""

    @property
    def auditcard_uid(self) -> str:
        """Returns the experimentcard uid"""

    @auditcard_uid.setter
    def auditcard_uid(self, auditcard_uid: str) -> None:
        """Set the experimentcard uid"""

class ModelCard:
    def __init__(
        self,
        interface: Optional[ModelInterface] = None,
        space: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
        uid: Optional[str] = None,
        tags: List[str] = [],
        datacard_uid: Optional[str] = None,
        metadata: ModelCardMetadata = ModelCardMetadata(),
    ) -> None:
        """Create a ModelCard from a machine learning model.

        Cards are stored in the ModelCardRegistry and follow the naming convention of:
        {registry}/{space}/{name}/v{version}

        Args:
            interface (ModelInterface | None):
                `ModelInterface` class containing trained model
            space (str | None):
                space to associate with `ModelCard`
            name (str | None):
                Name to associate with `ModelCard`
            version (str | None):
                Current version (assigned if card has been registered). Follows
                semantic versioning.
            uid (str | None):
                Unique id (assigned if card has been registered)
            tags (List[str]):
                Tags to associate with `ModelCard`. Can be a dictionary of strings or
                a `Tags` object.
            datacard_uid (str | None):
                The datacard uid to associate with the model card. This is used to link the
                model card to the data card. Datacard uid can also be set in card metadata.
            metadata (ModelCardMetadata):
                Metadata to associate with the `ModelCard. Defaults to an empty `ModelCardMetadata` object.

        Example:
        ```python
        from opsml import ModelCard, CardRegistry, RegistryType, SklearnModel, TaskType
        from sklearn import ensemble

        # for testing purposes
        from opsml.helpers.data import create_fake_data

        # pandas data
        X, y = create_fake_data(n_samples=1200)

        # train model
        reg = ensemble.RandomForestClassifier(n_estimators=5)
        reg.fit(X_train.to_numpy(), y_train)

        # create interface and card
        interface = SklearnModel(
            model=reg,
            sample_data=X_train,
            task_type=TaskType.Classification,
        )

        modelcard = ModelCard(
            interface=random_forest_classifier,
            space="my-repo",
            name="my-model",
            tags=["foo:bar", "baz:qux"],
        )

        # register card
        registry = CardRegistry(RegistryType.Model, save_kwargs=ModelSaveKwargs(save_onnx=True)) # convert to onnx
        registry.register_card(modelcard)
        ```
        """

    @property
    def model(self) -> Any:
        """Returns the model. This is a special property that is used to
        access the model from the interface. It is not settable. It will also
        raise an error if the interface is not set or if the model
        has not been loaded.
        """

    @property
    def onnx_session(self) -> Optional[OnnxSession]:
        """Returns the onnx session. This is a special property that is used to
        access the onnx session from the interface. It is not settable. It will also
        raise an error if the interface is not set or if the model
        has not been loaded.
        """

    @property
    def app_env(self) -> str:
        """Returns the app env"""

    @property
    def created_at(self) -> datetime:
        """Returns the created at timestamp"""

    @property
    def datacard_uid(self) -> str:
        """Returns the datacard uid"""

    @datacard_uid.setter
    def datacard_uid(self, datacard_uid: str) -> None:
        """Set the datacard uid"""

    @property
    def experimentcard_uid(self) -> str:
        """Returns the experimentcard uid"""

    @experimentcard_uid.setter
    def experimentcard_uid(self, experimentcard_uid: str) -> None:
        """Set the experimentcard uid"""

    @property
    def uri(self) -> Path:
        """Returns the uri of the `ModelCard` in the
        format of {registry}/{space}/{name}/v{version}
        """

    @property
    def interface(self) -> Optional[ModelInterface]:
        """Returns the `ModelInterface` associated with the `ModelCard`"""

    @interface.setter
    def interface(self, interface: Any) -> None:
        """Set the `ModelInterface` associated with the `ModelCard`"""

    @property
    def name(self) -> str:
        """Returns the name of the `ModelCard`"""

    @name.setter
    def name(self, name: str) -> None:
        """Set the name of the `ModelCard`

        Args:
            name (str):
                The name of the `ModelCard`
        """

    @property
    def space(self) -> str:
        """Returns the space of the `ModelCard`"""

    @space.setter
    def space(self, space: str) -> None:
        """Set the space of the `ModelCard`

        Args:
            space (str):
                The space of the `ModelCard`
        """

    @property
    def version(self) -> str:
        """Returns the version of the `ModelCard`"""

    @version.setter
    def version(self, version: str) -> None:
        """Set the version of the `ModelCard`

        Args:
            version (str):
                The version of the `ModelCard`
        """

    @property
    def uid(self) -> str:
        """Returns the uid of the `ModelCard`"""

    @property
    def tags(self) -> List[str]:
        """Returns the tags of the `ModelCard`"""

    @property
    def metadata(self) -> ModelCardMetadata:
        """Returns the metadata of the `ModelCard`"""

    @property
    def registry_type(self) -> RegistryType:
        """Returns the card type of the `ModelCard`"""

    def save(self, path: Path, save_kwargs: Optional[ModelSaveKwargs] = None) -> None:
        """Save the model card to a directory

        Args:
            path (Path):
                Path to save the model card.
            save_kwargs (SaveKwargs):
                Optional kwargs to pass to `ModelInterface` save method.
        """

    def load(
        self,
        path: Optional[Path] = None,
        load_kwargs: None | ModelLoadKwargs = None,
    ) -> None:
        """Load ModelCard interface components

        Args:
            path (Path | None):
                The path to load the data card from. If no path is provided,
                the model interface will be loaded from the server.
            load_kwargs (ModelLoadKwargs):
                Optional kwargs to pass to `ModelInterface` load method.
        """

    @staticmethod
    def load_from_path(
        path: Path,
        load_kwargs: None | ModelLoadKwargs = None,
        interface: Optional[ModelInterface] = None,
    ) -> "ModelCard":
        """Staticmethod to load a ModelCard from a path. Typically used when
        a `ModelCard`s artifacts have already been downloaded to a path.

        This is commonly used in API workflows where a user may download artifacts to
        a directory and load the contents during API/Application startup.

        Args:
            path (Path):
                The path to load the ModelCard from.
            load_kwargs (ModelLoadKwargs):
                Optional kwargs to pass to `ModelInterface` load method.
            interface (ModelInterface):
                Optional interface for the model. Used with Custom interfaces.

        Returns:
            ModelCard:
                The loaded ModelCard.

        Example:

            ```python
            # shell command
            opsml run get model --space <space_name> --name <model_name> --write-dir <path>

            # Within python application
            model_card = ModelCard.load_from_path(<path>)
            ```
        """

    def download_artifacts(self, path: Optional[Path] = None) -> None:
        """Download artifacts associated with the ModelCard

        Args:
            path (Path):
                Path to save the artifacts. If not provided, the artifacts will be saved
                to a directory called "card_artifacts"
        """

    def model_dump_json(self) -> str:
        """Return the model dump as a json string"""

    @staticmethod
    def model_validate_json(
        json_string: str, interface: Optional[ModelInterface] = None
    ) -> "ModelCard":
        """Validate the model json string

        Args:
            json_string (str):
                The json string to validate
            interface (ModelInterface):
                By default, the interface will be inferred and instantiated
                from the interface metadata. If an interface is provided
                (as in the case of custom interfaces), it will be used.
        """

    def drift_profile_path(self, alias: str) -> Path:
        """Helper method that returns the path to a specific drift profile.
        This method will fail if there is no drift profile map or the alias
        does not exist.

        Args:
            alias (str):
                The alias of the drift profile

        Returns:
            Path to the drift profile
        """

    def __str__(self) -> str:
        """Return a string representation of the ModelCard.

        Returns:
            String representation of the ModelCard.
        """

    @property
    def drift_profile(self) -> DriftProfileMap:
        """Return the drift profile map from the model interface.

        Returns:
            DriftProfileMap
        """

class ComputeEnvironment:
    cpu_count: int
    total_memory: int
    total_swap: int
    system: str
    os_version: str
    hostname: str
    python_version: str

    def __str__(self): ...

class UidMetadata:
    datacard_uids: List[str]
    modelcard_uids: List[str]
    promptcard_uids: List[str]
    service_card_uids: List[str]
    experimentcard_uids: List[str]

class ExperimentCard:
    def __init__(
        self,
        space: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
        uid: Optional[str] = None,
        tags: List[str] = [],
    ) -> None:
        """Instantiates a ExperimentCard.

        Cards are stored in the ExperimentCard Registry and follow the naming convention of:
        {registry}/{space}/{name}/v{version}

        Args:
            space (str | None):
                space to associate with `ExperimentCard`
            name (str | None):
                Name to associate with `ExperimentCard`
            version (str | None):
                Current version (assigned if card has been registered). Follows
                semantic versioning.
            uid (str | None):
                Unique id (assigned if card has been registered)
            tags (List[str]):
                Tags to associate with `ExperimentCard`. Can be a dictionary of strings or
                a `Tags` object.

        Example:
        ```python
        from opsml import start_experiment

        # start an experiment
        with start_experiment(space="test", log_hardware=True) as exp:
            exp.log_metric("accuracy", 0.95)
            exp.log_parameter("epochs", 10)
        ```
        """

    def get_metrics(
        self,
        names: Optional[list[str]] = None,
    ) -> Metrics:
        """
        Get metrics of an experiment

        Args:
            names (list[str] | None):
                Names of the metrics to get. If None, all metrics will be returned.

        Returns:
            Metrics
        """

    def get_parameters(
        self,
        names: Optional[list[str]] = None,
    ) -> "Parameters":
        """
        Get parameters of an experiment

        Args:
            names (list[str] | None):
                Names of the parameters to get. If None, all parameters will be returned.

        Returns:
            Parameters
        """

    @property
    def name(self) -> str:
        """Returns the name of the `ModelCard`"""

    @name.setter
    def name(self, name: str) -> None:
        """Set the name of the `ModelCard`

        Args:
            name (str):
                The name of the `ModelCard`
        """

    @property
    def space(self) -> str:
        """Returns the space of the `experimentcard`"""

    @space.setter
    def space(self, space: str) -> None:
        """Set the space of the `experimentcard`

        Args:
            space (str):
                The space of the `experimentcard`
        """

    @property
    def version(self) -> str:
        """Returns the version of the `experimentcard`"""

    @version.setter
    def version(self, version: str) -> None:
        """Set the version of the `experimentcard`

        Args:
            version (str):
                The version of the `experimentcard`
        """

    @property
    def eval_metrics(self) -> "EvalMetrics":
        """Returns the eval metrics of the `experimentcard`"""

    @eval_metrics.setter
    def eval_metrics(self, metrics: "EvalMetrics") -> None:
        """Set the eval metrics of the `experimentcard`

        Args:
            metrics (EvalMetrics):
                The eval metrics of the `experimentcard`
        """

    @property
    def uid(self) -> str:
        """Returns the uid of the `experimentcard`"""

    @property
    def uids(self) -> UidMetadata:
        """Returns the uids of the `experimentcard`"""

    @property
    def tags(self) -> List[str]:
        """Returns the tags of the `ExperimentCard`"""

    @property
    def artifacts(self) -> List[str]:
        """Returns the artifact names"""

    @property
    def compute_environment(self) -> ComputeEnvironment:
        """Returns the compute env"""

    @property
    def registry_type(self) -> RegistryType:
        """Returns the card type of the `experimentcard`"""

    @property
    def app_env(self) -> str:
        """Returns the app env"""

    @property
    def created_at(self) -> datetime:
        """Returns the created at timestamp"""

    def add_child_experiment(self, uid: str) -> None:
        """Add a child experiment to the experiment card

        Args:
            uid (str):
                The experiment card uid to add
        """

    def list_artifacts(self, path: Optional[Path]) -> List[str]:
        """List the artifacts associated with the experiment card

        Args:
            path (Path):
                Specific path you wish to list artifacts from. If not provided,
                all artifacts will be listed.

                Example:
                    You logged artifacts with the following paths:
                    - "data/processed/my_data.csv"
                    - "model/my_model.pkl"

                    If you wanted to list all artifacts in the "data" directory,
                    you would pass Path("data") as the path.
        """

    def download_artifacts(
        self,
        path: Optional[Path] = None,
        lpath: Optional[Path] = None,
    ) -> None:
        """Download artifacts associated with the ExperimentCard

        Args:
            path (Path | None):
                Specific path you wish to download artifacts from. If not provided,
                all artifacts will be downloaded.

            lpath (Path | None):
                Local path to save the artifacts. If not provided, the artifacts will be saved
                to a directory called "artifacts"
        """

    def download_artifact(
        self,
        path: Path,
        lpath: Optional[Path] = None,
    ) -> None:
        """Download a specific artifact associated with the ExperimentCard

        Args:
            path (Path):
                Path to the artifact to download
            lpath (Path | None):
                Local path to save the artifact. If not provided, the artifact will be saved
                to a directory called "artifacts"

        Examples:

        ```python
        # artifact logged to artifacts/data.csv
        download_artifact(Path("artifacts/data.csv"))
        #or
        download_artifact(Path("data.csv"))
        ```
        """

    @staticmethod
    def model_validate_json(json_string: str) -> "ExperimentCard":
        """Load card from json string

        Args:
            json_string (str):
                The json string to validate
        """

    def __str__(self) -> str:
        """Return a string representation of the `ExperimentCard`.

        Returns:
            String representation of the ModelCard.
        """

class PromptCard:
    def __init__(
        self,
        prompt: Prompt,
        space: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
        uid: Optional[str] = None,
        tags: List[str] = [],
        drift_profile: Optional[Dict[str, LLMDriftProfile]] = None,
    ) -> None:
        """Creates a `PromptCard`.

        Cards are stored in the PromptCard Registry and follow the naming convention of:
        {registry}/{space}/{name}/v{version}


        Args:
            prompt (Prompt):
                Prompt to associate with `PromptCard`
            space (str | None):
                space to associate with `PromptCard`
            name (str | None):
                Name to associate with `PromptCard`
            version (str | None):
                Current version (assigned if card has been registered). Follows
                semantic versioning.
            uid (str | None):
                Unique id (assigned if card has been registered)
            tags (List[str]):
                Tags to associate with `PromptCard`. Can be a dictionary of strings or
                a `Tags` object.
            drift_profile:
                Drift profile(s) to associate with the model. Must be a dictionary of
                alias and drift profile. Currently supports LLM drift profiles.
        Example:
        ```python
        from opsml import Prompt, PromptCard, CardRegistry, RegistryType

        # create prompt
        prompt = Prompt(
            model="openai:gpt-4o",
            message=[
                "My prompt $1 is $2",
                "My prompt $3 is $4",
            ],
            system_instruction="system_prompt",
        )

        # create card
        card = PromptCard(
            prompt=prompt,
            space="my-repo",
            name="my-prompt",
            version="0.0.1",
            tags=["gpt-4o", "prompt"],
        )

        # register card
        registry = CardRegistry(RegistryType.Prompt)
        registry.register_card(card)
        ```
        """

    @property
    def prompt(self) -> Prompt:
        """Returns the prompt"""

    @prompt.setter
    def prompt(self, prompt: Prompt) -> None:
        """Set the prompt

        Args:
            prompt (Prompt):
                The prompt to set
        """

    @property
    def experimentcard_uid(self) -> str:
        """Returns the experimentcard uid"""

    @experimentcard_uid.setter
    def experimentcard_uid(self, experimentcard_uid: str) -> None:
        """Set the experimentcard uid"""

    @property
    def name(self) -> str:
        """Returns the name of the `ModelCard`"""

    @name.setter
    def name(self, name: str) -> None:
        """Set the name of the `ModelCard`

        Args:
            name (str):
                The name of the `ModelCard`
        """

    @property
    def space(self) -> str:
        """Returns the space of the `ModelCard`"""

    @space.setter
    def space(self, space: str) -> None:
        """Set the space of the `ModelCard`

        Args:
            space (str):
                The space of the `ModelCard`
        """

    @property
    def version(self) -> str:
        """Returns the version of the `ModelCard`"""

    @version.setter
    def version(self, version: str) -> None:
        """Set the version of the `ModelCard`

        Args:
            version (str):
                The version of the `ModelCard`
        """

    @property
    def uid(self) -> str:
        """Returns the uid of the `ModelCard`"""

    @property
    def tags(self) -> List[str]:
        """Returns the tags of the `ModelCard`"""

    def save(self, path: Path) -> None:
        """Save the `PromptCard` to a directory

        Args:
            path (Path):
                Path to save the prompt card.
        """

    @staticmethod
    def model_validate_json(json_string: str) -> "PromptCard":
        """Load card from json string

        Args:
            json_string (str):
                The json string to validate
        """

    def __str__(self): ...
    def create_drift_profile(
        self,
        alias: str,
        config: LLMDriftConfig,
        metrics: List[LLMDriftMetric],
        workflow: Optional[Workflow] = None,
    ) -> None:
        """Create an LLMDriftProfile for LLM evaluation and drift detection.

        LLM evaluations are run asynchronously on the scouter server.

        Logic flow:
            1. If only metrics are provided, a workflow will be created automatically
               from the metrics. In this case a prompt is required for each metric.
            2. If a workflow is provided, it will be parsed and validated for compatibility:
               - A list of metrics to evaluate workflow output must be provided
               - Metric names must correspond to the final task names in the workflow

        Baseline metrics and thresholds will be extracted from the LLMDriftMetric objects.

        Args:
            alias (str):
                The alias for the drift profile. This will be used to reference
                the profile in the model card.
            config (LLMDriftConfig):
                The configuration for the LLM drift profile containing space, name,
                version, and alert settings.
            metrics (list[LLMDriftMetric]):
                A list of LLMDriftMetric objects representing the metrics to be monitored.
                Each metric defines evaluation criteria and alert thresholds.
            workflow (Optional[Workflow]):
                Optional custom workflow for advanced evaluation scenarios. If provided,
                the workflow will be validated to ensure proper parameter and response
                type configuration.

        Returns:
            LLMDriftProfile: Configured profile ready for LLM drift monitoring.

        Raises:
            ProfileError: If workflow validation fails, metrics are empty when no
                workflow is provided, or if workflow tasks don't match metric names.

        Examples:
            Basic usage with metrics only:

            >>> config = LLMDriftConfig("my_space", "my_model", "1.0")
            >>> metrics = [
            ...     LLMDriftMetric("accuracy", 0.95, AlertThreshold.Above, 0.1, prompt),
            ...     LLMDriftMetric("relevance", 0.85, AlertThreshold.Below, 0.2, prompt2)
            ... ]
            >>> profile = Drifter().create_llm_drift_profile(config, metrics)

            Advanced usage with custom workflow:

            >>> workflow = create_custom_workflow()  # Your custom workflow
            >>> metrics = [LLMDriftMetric("final_task", 0.9, AlertThreshold.Above)]
            >>> profile = Drifter().create_llm_drift_profile(config, metrics, workflow)

        Note:
            - When using custom workflows, ensure final tasks have Score response types
            - Initial workflow tasks must include "input" and/or "response" parameters
            - All metric names must match corresponding workflow task names
        """

    @property
    def drift_profile(self) -> DriftProfileMap:
        """Return the drift profile map from the model interface.

        Returns:
            DriftProfileMap
        """

    @drift_profile.setter
    def drift_profile(self, drift_profile: DriftProfileMap) -> None:
        """Set the drift profile map for the prompt card.

        Args:
            drift_profile (DriftProfileMap):
                The drift profile map to set.
        """

class Card:
    """Represents a card from a given registry that can be used in a service card"""

    def __init__(
        self,
        alias: str,
        registry_type: Optional[RegistryType] = None,
        space: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
        uid: Optional[str] = None,
        card: Optional["CardType"] = None,
        drift: Optional[DriftConfig] = None,
    ) -> None:
        """Initialize the service card. Card accepts either a combination of
        space and name (with version as optional) or a uid. If only space and name are
        provided with no version, the latest version for a given space and name will be used
        (e.g. {space}/{name}/v*). If a version is provided, it must follow semver rules that
        are compatible with opsml (e.g. v1.*, v1.2.3, v2.3.4-alpha, etc.). If both space/name and uid
        are provided, the uid will take precedence. If neither space/name nor uid are provided,
        an error will be raised.

        Alias is used to identify the card in the service card and is not necessarily the name of
        the card. It is recommended to use a short and descriptive alias that is easy to remember.

        Example:

        ```python
        service = ServiceCard(...)
        service["my_alias"]
        ```


        Args:
            alias (str):
                The alias of the card
            registry_type (RegistryType):
                The type of registry the service card belongs to. This is
                required if no card is provided.
            space (str):
                The space of the service card
            name (str):
                The name of the service card
            version (str):
                The version of the service card
            uid (str):
                The uid of the service card
            card (Union[DataCard, ModelCard, PromptCard, ExperimentCard]):
                Optional card to add to the service. If provided, arguments will
                be extracted from the card. This card must be registered in a registry.
            drift (DriftConfig | None):
                Optional drift configuration for the card. This is used to
                configure drift detection for the card in the service.


        Example:

        ```python
        from opsml import Card, ServiceCard, RegistryType

        # With arguments
        card = Card(
            alias="my_alias",
            registry_type=RegistryType.Model,
            space="my_space",
            name="my_name",
            version="1.0.0",
        )

        # With card uid
        card = Card(
            alias="my_alias",
            registry_type=RegistryType.Model,
            uid="my_uid",
        )

        # With registered card
        card = Card(
            alias="my_alias",
            card=model_card,  # ModelCard object
        )
        ```

        """
    @property
    def alias(self) -> str:
        """Alias used to reference this card within the service."""

    @property
    def space(self) -> str:
        """Space this card belongs to."""

    @property
    def name(self) -> str:
        """Name of the card."""

    @property
    def version(self) -> Optional[str]:
        """Version specifier for the card."""

    @property
    def registry_type(self) -> RegistryType:
        """Registry type of the card."""

    @property
    def drift(self) -> Optional[DriftConfig]:
        """Drift detection configuration if enabled."""

    @property
    def uid(self) -> Optional[str]:
        """Unique identifier of the card."""

class McpCapability:
    """
    Enum representing Model Context Protocol capabilities.

    Attributes:
        Resources: Resource access capability
        Tools: Tool invocation capability
        Prompts: Prompt template capability
    """

    Resources: "McpCapability"
    Tools: "McpCapability"
    Prompts: "McpCapability"

class McpTransport:
    """
    Enum representing Model Context Protocol transport types.

    Attributes:
        Http: HTTP-based transport
        Stdio: Standard I/O transport
    """

    Http: "McpTransport"
    Stdio: "McpTransport"

class McpConfig:
    def __init__(
        self,
        capabilities: List[McpCapability],
        transport: McpTransport,
    ):
        """Initialize MCP service configuration.

        Required when service type is 'Mcp'.

        Args:
            capabilities: List of MCP capabilities to enable (resources, tools, prompts)
            transport: Transport protocol to use (http or stdio)

        Raises:
            ValueError: If capabilities list is empty
        """

    @property
    def capabilities(self) -> List[McpCapability]:
        """List of enabled MCP capabilities."""

    @property
    def transport(self) -> McpTransport:
        """Transport protocol for MCP communication."""

class ServiceCard:
    """Creates a ServiceCard to hold a collection of cards."""

    def __init__(
        self,
        space: str,
        name: str,
        cards: List[Card],
        version: Optional[str] = None,
        service_type: Optional[ServiceType] = None,
        load_spec: bool = False,
    ) -> None:
        """Initialize the service card

        Args:
            space (str):
                The space of the service card
            name (str):
                The name of the service card
            cards (List[Card]):
                The cards in the service card
            version (str | None):
                The version of the service card. If not provided, the latest version
                for a given space and name will be used (e.g. {space}/{name}/v*).
            service_type (ServiceType | None):
                The type of service (Api, Mcp, Agent). If not provided, defaults to Api.
            load_spec (bool):
                Whether to load the opsmlspec.yaml file if it exists in the service card directory.
                This is useful when you have additional metadata in the opsmlspec.yaml file that you want
                to include in the service card. Defaults to False.
        """

    @property
    def space(self) -> str:
        """Return the space of the service card"""

    @property
    def name(self) -> str:
        """Return the name of the service card"""

    @property
    def version(self) -> str:
        """Return the version of the service card"""

    @property
    def uid(self) -> str:
        """Return the uid of the service card"""

    @property
    def created_at(self) -> datetime:
        """Return the created at timestamp"""

    @property
    def cards(self) -> List["CardType"]:
        """Return the cards in the service card"""

    @property
    def opsml_version(self) -> str:
        """Return the opsml version"""

    def save(self, path: Path) -> None:
        """Save the service card to a directory

        Args:
            path (Path):
                Path to save the service card.
        """

    def model_validate_json(self, json_string: str) -> "ServiceCard":
        """Load service card from json string

        Args:
            json_string (str):
                The json string to validate
        """

    def load(
        self,
        load_kwargs: Optional[Dict[str, ModelLoadKwargs | DataLoadKwargs]] = None,
    ) -> None:
        """Call the load method on each Card that requires additional loading.
        This applies to ModelCards and DataCards. PromptCards and ExperimentCards
        do not require additional loading and are loaded automatically when loading
        the ServiceCard from the registry.

        Args:
            load_kwargs (Dict[str, ModelLoadKwargs | DataLoadKwargs]):
                Optional kwargs for loading cards. Expected format:
                {
                    "card_alias":  DataLoadKwargs | ModelLoadKwargs
                }
        """

    @staticmethod
    def from_path(
        path: Optional[Path] = None,
        load_kwargs: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> "ServiceCard":
        """Loads a service card and its associated cards from a filesystem path.

        Args:
            path (Path):
                Path to load the service card from. Defaults to "service".
            load_kwargs (Dict[str, Dict[str, Any]]):
                Optional kwargs for loading cards. Expected format:
                {
                    "card_alias": {
                        "interface": interface_object,
                        "load_kwargs": DataLoadKwargs | ModelLoadKwargs
                    }
                }

        Returns:
            ServiceCard: The loaded service card with all cards instantiated.

        Raises:
            PyError: If service card JSON cannot be read
            PyError: If cards cannot be loaded
            PyError: If invalid kwargs are provided

        Example:
            ```python
            # Load with custom kwargs for model loading
            load_kwargs = {
                "model_card": {
                    "load_kwargs": ModelLoadKwargs(load_onnx=True)
                }
            }
            service = ServiceCard.from_path(load_kwargs=load_kwargs)
            ```
        """

    def __getitem__(self, alias: str) -> "CardType":
        """Get a card from the service card by alias

        Args:
            alias (str):
                The alias of the card to get

        Returns:
            Card:
                The card with the given alias
        """

    def download_artifacts(self, path: Optional[Path] = None) -> None:
        """Download artifacts associated with each card in the service card. This method
        will always overwrite existing artifacts.

        If the path is not provided, the artifacts will be saved to a directory.

        ```
        service/
        |-- {name}-{version}/
            |-- alias1/
            |-- alias2/
            |-- alias3/
        `-- ...
        ```

        Args:
            path (Path):
                Top-level Path to download the artifacts to. If not provided, the artifacts will be saved
                to a directory using the ServiceCard name.
        """

# Define a TypeVar that can only be one of our card types
CardType = TypeVar(  # pylint: disable=invalid-name
    "CardType",
    DataCard,
    ModelCard,
    PromptCard,
    ExperimentCard,
    ServiceCard,
)

class CardRegistry(Generic[CardType]):
    @overload
    def __init__(
        self, registry_type: Literal[RegistryType.Data]
    ) -> "CardRegistry[DataCard]": ...
    @overload
    def __init__(
        self, registry_type: Literal[RegistryType.Model]
    ) -> "CardRegistry[ModelCard]": ...
    @overload
    def __init__(
        self, registry_type: Literal[RegistryType.Prompt]
    ) -> "CardRegistry[PromptCard]": ...
    @overload
    def __init__(
        self, registry_type: Literal[RegistryType.Experiment]
    ) -> "CardRegistry[ExperimentCard]": ...
    @overload
    def __init__(
        self, registry_type: Literal[RegistryType.Service]
    ) -> "CardRegistry[ServiceCard]": ...
    @overload
    def __init__(
        self, registry_type: Literal[RegistryType.Audit]
    ) -> "CardRegistry[Any]": ...

    # String literal overloads
    @overload
    def __init__(self, registry_type: Literal["data"]) -> "CardRegistry[DataCard]": ...
    @overload
    def __init__(
        self, registry_type: Literal["model"]
    ) -> "CardRegistry[ModelCard]": ...
    @overload
    def __init__(
        self, registry_type: Literal["prompt"]
    ) -> "CardRegistry[PromptCard]": ...
    @overload
    def __init__(
        self, registry_type: Literal["experiment"]
    ) -> "CardRegistry[ExperimentCard]": ...
    @overload
    def __init__(
        self, registry_type: Literal["service"]
    ) -> "CardRegistry[ServiceCard]": ...
    @overload
    def __init__(self, registry_type: Literal["audit"]) -> "CardRegistry[Any]": ...
    def __init__(self, registry_type: Union[RegistryType, str]) -> None:
        """Interface for connecting to any of the Card registries

        Args:
            registry_type (RegistryType | str):
                The type of registry to connect to. Can be a `RegistryType` or a string

        Returns:
            Instantiated connection to specific Card registry


        Example:
        ```python
            data_registry = CardRegistry(RegistryType.Data)
            data_registry.list_cards()

            or
            data_registry = CardRegistry("data")
            data_registry.list_cards()
        ```
        """

    @property
    def registry_type(self) -> RegistryType:
        """Returns the type of registry"""

    @property
    def table_name(self) -> str:
        """Returns the table name for the registry"""

    @property
    def mode(self) -> RegistryMode:
        """Returns the mode of the registry"""

    def list_cards(
        self,
        uid: Optional[str] = None,
        space: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
        max_date: Optional[str] = None,
        tags: Optional[List[str]] = None,
        sort_by_timestamp: Optional[bool] = False,
        limit: int = 25,
    ) -> CardList:
        """Retrieves records from registry

        Args:
            uid (str):
                Unique identifier for Card. If present, the uid takes precedence
            space (str):
                Optional space associated with card
            name (str):
                Optional name of card
            version (str):
                Optional version number of existing data. If not specified, the
                most recent version will be used
            tags (List[str]):
                Optional list of tags to search for
            max_date (str):
                Optional max date to search. (e.g. "2023-05-01" would search for cards up to and including "2023-05-01").
                Must be in the format "YYYY-MM-DD"
            sort_by_timestamp:
                If True, sorts by timestamp descending
            limit (int):
                Places a limit on result list. Results are sorted by SemVer.
                Defaults to 25.

        Returns:
            List of Cards
        """

    def register_card(
        self,
        card: CardType,
        version_type: VersionType = VersionType.Minor,
        pre_tag: Optional[str] = None,
        build_tag: Optional[str] = None,
        save_kwargs: Optional[ModelSaveKwargs | DataSaveKwargs] = None,
    ) -> None:
        """Register a Card

        Args:
            card (ArtifactCard):
                Card to register. Can be a DataCard, ModelCard,
                experimentcard.
            version_type (VersionType):
                How to increment the version SemVer.
            pre_tag (str):
                Optional pre tag to associate with the version.
            build_tag (str):
                Optional build_tag to associate with the version.
            save_kwargs (SaveKwargs):
                Optional SaveKwargs to pass to the Card interface (If using DataCards
                and ModelCards).

        """

    @overload
    def load_card(
        self: "CardRegistry[DataCard]",
        uid: Optional[str] = None,
        space: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
        interface: Optional[DataInterface] = None,
    ) -> DataCard: ...
    @overload
    def load_card(
        self: "CardRegistry[ServiceCard]",
        uid: Optional[str] = None,
        space: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
        interface=Optional[ServiceCardInterfaceType],
    ) -> ServiceCard: ...
    @overload
    def load_card(
        self: "CardRegistry[ModelCard]",
        uid: Optional[str] = None,
        space: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
        interface: Optional[ModelInterface] = None,
    ) -> ModelCard: ...
    @overload
    def load_card(
        self: "CardRegistry[PromptCard]",
        uid: Optional[str] = None,
        space: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
        interface: None = None,
    ) -> PromptCard: ...
    @overload
    def load_card(
        self: "CardRegistry[ExperimentCard]",
        uid: Optional[str] = None,
        space: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
        interface: None = None,
    ) -> ExperimentCard: ...
    def load_card(
        self,
        uid: Optional[str] = None,
        space: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
        interface: Optional[LoadInterfaceType] = None,
    ) -> Union[DataCard, ModelCard, PromptCard, ExperimentCard, ServiceCard]:
        """Load a Card from the registry

        Args:
            uid (str, optional):
                Unique identifier for Card. If present, the uid takes precedence over space/name/version.
            space (str, optional):
                Space associated with the card.
            name (str, optional):
                Name of the card.
            version (str, optional):
                Version number of existing card. If not specified, the most recent version will be used.
            interface (LoadInterfaceType, optional):
                Interface to load the card with. Required for cards registered with custom interfaces.
                The expected interface type depends on the registry:

                - DataCard registry: DataInterface
                - ModelCard registry: ModelInterface
                - ExperimentCard registry: Not used
                - PromptCard registry: Not used
                - ServiceCard registry: Dict[str, Union[DataInterface, ModelInterface]]
                  Keys should be card aliases within the service.

        Returns:
            Union[DataCard, ModelCard, PromptCard, ExperimentCard, ServiceCard]:
                The loaded card instance from the registry.
        """

    def update_card(
        self,
        card: CardType,
    ) -> None:
        """Update a Card in the registry.
        Note: This will only update the registry record for a given card. It
        will not re-save/update the underlying artifacts (except for metadata).

        Args:
            card (ArtifactCard):
                Card to update. Can be a DataCard, ModelCard,
                experimentcard.
        """

    def delete_card(
        self,
        card: CardType,
    ) -> None:
        """Delete a Card from the registry. This will also remove
        the underlying artifacts associated with the card.

        Args:
            card (ArtifactCard):
                Card to delete. Can be a DataCard, ModelCard,
                experimentcard.
        """

class CardRegistries:
    def __init__(self) -> None: ...
    @property
    def data(self) -> CardRegistry[DataCard]: ...
    @property
    def model(self) -> CardRegistry[ModelCard]: ...
    @property
    def experiment(self) -> CardRegistry[ExperimentCard]: ...
    @property
    def audit(self) -> CardRegistry[Any]: ...
    @property
    def prompt(self) -> CardRegistry[PromptCard]: ...
    @property
    def service(self) -> CardRegistry[ServiceCard]: ...

def download_service(
    write_dir: Path,
    space: Optional[str] = None,
    name: Optional[str] = None,
    version: Optional[str] = None,
    uid: Optional[str] = None,
) -> None:
    """Download a service from the registry.

    Args:
        space (str):
            Space associated with the service.
        name (str):
            Name of the service.
        version (str):
            Version number of the service.
        uid (str):
            Unique identifier for the service.
        write_dir (str):
            Directory to write the downloaded service to.
    """

########################################################################################
#  This section contains the type definitions for opsml.evaluate module
# __opsml.evaluate__
# ######################################################################################
Context: TypeAlias = Union[Dict[str, Any], BaseModel]

class LLMEvalTaskResult:
    """Eval Result for a specific evaluation"""

    @property
    def id(self) -> str:
        """Get the record id associated with this result"""

    @property
    def metrics(self) -> Dict[str, Score]:
        """Get the list of metrics"""

    @property
    def embedding(self) -> Dict[str, List[float]]:
        """Get embeddings of embedding targets"""

class LLMEvalResults:
    """Defines the results of an LLM eval metric"""

    def __getitem__(self, key: str) -> LLMEvalTaskResult:
        """Get the task results for a specific record ID. A RuntimeError will be raised if the record ID does not exist."""

    def __str__(self):
        """String representation of the LLMEvalResults"""

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
    def model_validate_json(json_string: str) -> "LLMEvalResults":
        """Validate and create an LLMEvalResults instance from a JSON string

        Args:
            json_string (str):
                JSON string to validate and create the LLMEvalResults instance from.
        """

    @property
    def errored_tasks(self) -> List[str]:
        """Get a list of record IDs that had errors during evaluation"""

    @property
    def histograms(self) -> Optional[Dict[str, Histogram]]:
        """Get histograms for all calculated features (metrics, embeddings, similarities)"""

class LLMEvalMetric:
    """Defines an LLM eval metric to use when evaluating LLMs"""

    def __init__(self, name: str, prompt: Prompt):
        """
        Initialize an LLMEvalMetric to use for evaluating LLMs. This is
        most commonly used in conjunction with `evaluate_llm` where LLM inputs
        and responses can be evaluated against a variety of user-defined metrics.

        Args:
            name (str):
                Name of the metric
            prompt (Prompt):
                Prompt to use for the metric. For example, a user may create
                an accuracy analysis prompt or a query reformulation analysis prompt.
        """

    def __str__(self) -> str:
        """
        String representation of the LLMEvalMetric
        """

class LLMEvalRecord:
    """LLM record containing context tied to a Large Language Model interaction
    that is used to evaluate LLM responses.


    Examples:
        >>> record = LLMEvalRecord(
                id="123",
                context={
                    "input": "What is the capital of France?",
                    "response": "Paris is the capital of France."
                },
        ... )
        >>> print(record.context["input"])
        "What is the capital of France?"
    """

    def __init__(
        self,
        context: Context,
        id: Optional[str] = None,
    ) -> None:
        """Creates a new LLM record to associate with an `LLMDriftProfile`.
        The record is sent to the `Scouter` server via the `ScouterQueue` and is
        then used to inject context into the evaluation prompts.

        Args:
            context:
                Additional context information as a dictionary or a pydantic BaseModel. During evaluation,
                this will be merged with the input and response data and passed to the assigned
                evaluation prompts. So if you're evaluation prompts expect additional context via
                bound variables (e.g., `${foo}`), you can pass that here as key value pairs.
                {"foo": "bar"}
            id:
                Unique identifier for the record. If not provided, a new UUID will be generated.
                This is helpful for when joining evaluation results back to the original request.

        Raises:
            TypeError: If context is not a dict or a pydantic BaseModel.

        """

    @property
    def context(self) -> Dict[str, Any]:
        """Get the contextual information.

        Returns:
            The context data as a Python object (deserialized from JSON).
        """

def evaluate_llm(
    records: List[LLMEvalRecord],
    metrics: List[LLMEvalMetric],
    config: Optional["EvaluationConfig"] = None,
) -> LLMEvalResults:
    """
    Evaluate LLM responses using the provided evaluation metrics.

    Args:
        records (List[LLMEvalRecord]):
            List of LLM evaluation records to evaluate.
        metrics (List[LLMEvalMetric]):
            List of LLMEvalMetric instances to use for evaluation.
        config (Optional[EvaluationConfig]):
            Optional EvaluationConfig instance to configure evaluation options.

    Returns:
        LLMEvalResults
    """

class EvaluationConfig:
    """Configuration options for LLM evaluation."""

    def __init__(
        self,
        embedder: Optional[Embedder] = None,
        embedding_targets: Optional[List[str]] = None,
        compute_similarity: bool = False,
        cluster: bool = False,
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
            cluster (bool):
                Whether to perform clustering on the embeddings. Default is False.
            compute_histograms (bool):
                Whether to compute histograms for all calculated features (metrics, embeddings, similarities).
                Default is False.
        """

########################################################################################
#  This section contains the type definitions for opsml.experiment module
# __opsml.experiment__
# ######################################################################################

class ExperimentMetric:
    def __init__(
        self,
        name: str,
        value: float,
        step: Optional[int] = None,
        timestamp: Optional[int] = None,
        created_at: Optional[datetime] = None,
    ) -> None:
        """
        Initialize a Metric

        Args:
            name (str):
                Name of the metric
            value (float):
                Value of the metric
            step (int | None):
                Step of the metric
            timestamp (int | None):
                Timestamp of the metric
            created_at (datetime | None):
                Created at of the metric
        """

    @property
    def name(self) -> str:
        """
        Name of the metric
        """

    @property
    def value(self) -> float:
        """
        Value of the metric
        """

    @property
    def step(self) -> Optional[int]:
        """
        Step of the metric
        """

    @property
    def timestamp(self) -> Optional[int]:
        """
        Timestamp of the metric
        """

    @property
    def created_at(self) -> Optional[datetime]:
        """
        Created at of the metric
        """

class ExperimentMetrics:
    def __str__(self): ...
    def __getitem__(self, index: int) -> Metric: ...
    def __iter__(self): ...
    def __len__(self) -> int: ...

class Parameter:
    def __init__(
        self,
        name: str,
        value: Union[int, float, str],
    ) -> None:
        """
        Initialize a Parameter

        Args:
            name (str):
                Name of the parameter
            value (int | float | str):
                Value of the parameter
        """

    @property
    def name(self) -> str:
        """
        Name of the parameter
        """

    @property
    def value(self) -> Union[int, float, str]:
        """
        Value of the parameter
        """

class Parameters:
    def __str__(self): ...
    def __getitem__(self, index: int) -> Parameter: ...
    def __iter__(self): ...
    def __len__(self) -> int: ...

class LLMEvaluator:
    @staticmethod
    def evaluate(
        records: List[LLMEvalRecord],
        metrics: List[LLMEvalMetric],
        config: Optional[EvaluationConfig] = None,
    ) -> LLMEvalResults:
        """
            Evaluate LLM responses using the provided evaluation metrics.

        Args:
            records (List[LLMEvalRecord]):
                List of LLM evaluation records to evaluate.
            metrics (List[LLMEvalMetric]):
                List of LLMEvalMetric instances to use for evaluation.
            config (Optional[EvaluationConfig]):
                Optional EvaluationConfig instance to configure evaluation options.

        Returns:
            LLMEvalResults
        """

class Experiment:
    def start_experiment(
        self,
        space: Optional[str] = None,
        name: Optional[str] = None,
        code_dir: Optional[Path] = None,
        log_hardware: bool = False,
        experiment_uid: Optional[str] = None,
    ) -> "Experiment":
        """
        Start an Experiment

        Args:
            space (str | None):
                space to associate with `ExperimentCard`
            name (str | None):
                Name to associate with `ExperimentCard`
            code_dir (Path | None):
                Directory to log code from
            log_hardware (bool):
                Whether to log hardware information or not
            experiment_uid (str | None):
                Experiment UID. If provided, the experiment will be loaded from the server.

        Returns:
            Experiment
        """

    def __enter__(self) -> "Experiment":
        pass

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        pass

    @property
    def llm(self) -> LLMEvaluator:
        """Access to LLM evaluation methods."""

    def log_metric(
        self,
        name: str,
        value: float,
        step: Optional[int] = None,
        timestamp: Optional[int] = None,
        created_at: Optional[datetime] = None,
    ) -> None:
        """
        Log a metric

        Args:
            name (str):
                Name of the metric
            value (float):
                Value of the metric
            step (int | None):
                Step of the metric
            timestamp (int | None):
                Timestamp of the metric
            created_at (datetime | None):
                Created at of the metric
        """

    def log_metrics(self, metrics: list[Metric]) -> None:
        """
        Log multiple metrics

        Args:
            metrics (list[Metric]):
                List of metrics to log
        """

    def log_eval_metrics(self, metrics: "EvalMetrics") -> None:
        """
        Log evaluation metrics

        Args:
            metrics (EvalMetrics):
                Evaluation metrics to log
        """

    def log_parameter(
        self,
        name: str,
        value: Union[int, float, str],
    ) -> None:
        """
        Log a parameter

        Args:
            name (str):
                Name of the parameter
            value (int | float | str):
                Value of the parameter
        """

    def log_parameters(
        self, parameters: list[Parameter] | Dict[str, Union[int, float, str]]
    ) -> None:
        """
        Log multiple parameters

        Args:
            parameters (list[Parameter] | Dict[str, Union[int, float, str]]):
                Parameters to log
        """

    def log_artifact(
        self,
        lpath: Path,
        rpath: Optional[str] = None,
    ) -> None:
        """
        Log an artifact

        Args:
            lpath (Path):
                The local path where the artifact has been saved to
            rpath (Optional[str]):
                The path to associate with the artifact in the experiment artifact directory
                {experiment_path}/artifacts. If not provided, defaults to
                {experiment}/artifacts/{filename}
        """

    def log_figure_from_path(
        self,
        lpath: Path,
        rpath: Optional[str] = None,
    ) -> None:
        """
        Log a figure

        Args:
            lpath (Path):
                The local path where the figure has been saved to. Must be an image type
                (e.g. jpeg, tiff, png, etc.)
            rpath (Optional[str]):
                The path to associate with the figure in the experiment artifact directory
                {experiment_path}/artifacts/figures. If not provided, defaults to
                {experiment}/artifacts/figures/{filename}

        """

    def log_figure(
        self, name: str, figure: Any, kwargs: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log a figure. This method will log a matplotlib Figure object to the experiment artifacts.

        Args:
            name (str):
                Name of the figure including its file extension
            figure (Any):
                Figure to log
            kwargs (Optional[Dict[str, Any]]):
                Additional keyword arguments
        """

    def log_artifacts(
        self,
        paths: Path,
    ) -> None:
        """
        Log multiple artifacts

        Args:
            paths (Path):
                Paths to a directory containing artifacts.
                All files in the directory will be logged.
        """

    @property
    def card(self) -> "ExperimentCard":
        """
        ExperimentCard associated with the Experiment
        """

    def register_card(
        self,
        card: Union[DataCard, ModelCard, PromptCard],
        version_type: VersionType = VersionType.Minor,
        pre_tag: Optional[str] = None,
        build_tag: Optional[str] = None,
        save_kwargs: Optional[ModelSaveKwargs | DataSaveKwargs] = None,
    ) -> None:
        """Register a Card as part of an experiment

        Args:
            card (DataCard | ModelCard):
                Card to register. Can be a DataCard or a ModelCard
            version_type (VersionType):
                How to increment the version SemVer. Default is VersionType.Minor.
            pre_tag (str):
                Optional pre tag to associate with the version.
            build_tag (str):
                Optional build_tag to associate with the version.
            save_kwargs (SaveKwargs):
                Optional SaveKwargs to pass to the Card interface (If using DataCards
                and ModelCards).

        """

def start_experiment(
    space: Optional[str] = None,
    name: Optional[str] = None,
    code_dir: Optional[Path] = None,
    log_hardware: bool = False,
    experiment_uid: Optional[str] = None,
) -> Experiment:
    """
    Start an Experiment

    Args:
        space (str | None):
            space to associate with `ExperimentCard`
        name (str | None):
            Name to associate with `ExperimentCard`
        code_dir (Path | None):
            Directory to log code from
        log_hardware (bool):
            Whether to log hardware information or not
        experiment_uid (str | None):
            Experiment UID. If provided, the experiment will be loaded from the server.

    Returns:
        Experiment
    """

class EvalMetrics:
    """
    Map of metrics used that can be used to evaluate a model.
    The metrics are also used when comparing a model with other models
    """

    def __init__(self, metrics: Dict[str, float]) -> None:
        """
        Initialize EvalMetrics

        Args:
            metrics (Dict[str, float]):
                Dictionary of metrics containing the name of the metric as the key and its value as the value.
        """

    def __getitem__(self, key: str) -> float:
        """Get the value of a metric by name. A RuntimeError will be raised if the metric does not exist."""

def get_experiment_metrics(
    experiment_uid: str,
    names: Optional[list[str]] = None,
) -> Metrics:
    """
    Get metrics of an experiment

    Args:
        experiment_uid (str):
            UID of the experiment
        names (list[str] | None):
            Names of the metrics to get. If None, all metrics will be returned.

    Returns:
        Metrics
    """

def get_experiment_parameters(
    experiment_uid: str,
    names: Optional[list[str]] = None,
) -> Parameters:
    """
    Get parameters of an experiment

    Args:
        experiment_uid (str):
            UID of the experiment
        names (list[str] | None):
            Names of the parameters to get. If None, all parameters will be returned.

    Returns:
        Parameters
    """

def download_artifact(
    experiment_uid: str,
    path: Path,
    lpath: Optional[Path] = None,
) -> None:
    """
    Download an artifact from an experiment
    Args:
        experiment_uid (str):
            UID of the experiment
        path (Path):
            Path of the artifact to download
        lpath (Path | None):
            Local path to download the artifact to. If None, the artifact will be downloaded to the current working directory.
    """

########################################################################################
#  This section contains the type definitions for opsml.app module
# __opsml.app__
# ######################################################################################

class ReloadConfig:
    """Reload configuation to use with an Opsml AppState object. Defines the reload logic
    for checking, downloading and reloading ServiceCards and ScouterQueues associated with
    an AppState
    """

    def __init__(
        self,
        cron: str,
        max_retries: int = 3,
        write_path: Optional[Path] = None,
    ):
        """Initialize the reload configuration.

        Args:
            cron (str):
                The cron expression for the reload schedule.
            max_retries (int):
                The maximum number of retries for loading the service card.
                Defaults to 3.
            write_path (Optional[Path]):
                The optional path to write the service card. Defaults to Path({current directory})/ service_reload
        """

    @property
    def cron(self) -> str:
        """Get the cron expression for the reload schedule."""

    @cron.setter
    def cron(self, value: str):
        """Set the cron expression for the reload schedule."""

class AppState:
    """OpsML application state object. This is typically used in API
    workflows where you wish create a shared state to share among all requests.
    The OpsML app state provides a convenient way to load and store artifacts.
    Most notably, it provides an integration with Scouter so that you can load a `ServiceCard`
    along with a `ScouterQueue` for drift detection. Future iterations of this class may
    include other convenience methods that simplify common API tasks.
    """

    @staticmethod
    def from_path(
        path: Path,
        transport_config: Optional[
            Union[
                KafkaConfig,
                RabbitMQConfig,
                RedisConfig,
                HttpConfig,
            ]
        ] = None,
        reload_config: Optional[ReloadConfig] = None,
        load_kwargs: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> "AppState":
        """
        Load the AppState from a file path.

        Args:
            path (str):
                The file path to load the AppState from. This is typically the path
                pointing to the directory containing the `ServiceCard`.

            transport_config (KafkaConfig | RabbitMQConfig | RedisConfig | HttpConfig | None):
                Optional transport configuration for the queue publisher
                Can be KafkaConfig, RabbitMQConfig RedisConfig, or HttpConfig. If not provided,
                the queue will not be initialized.

            reload_config (ReloadConfig | None):
                Optional reload configuration for the AppState. If provided,
                the AppState will periodically check for updates to the ServiceCard
                and reload it if necessary.

            load_kwargs (Dict[str, Dict[str, Any]]):
                Optional kwargs for loading cards. Expected format:
                {
                    "card_alias": {
                        "interface": interface_object,
                        "load_kwargs": DataLoadKwargs | ModelLoadKwargs
                    }
                }

        Example:
            ```python
            from opsml.app import AppState
            from opsml.scouter import KafkaConfig

            app_state = AppState.from_path(
                "/path/to/service",
                transport_config=KafkaConfig(),
                )

            # Access the service card and queue
            service = app_state.service
            queue = app_state.queue
            ```

        Returns:
            AppState: The loaded AppState.
        """

    @property
    def service(self) -> ServiceCard:
        """Get the service card."""

    @property
    def queue(self) -> ScouterQueue:
        """Get the Scouter queue."""

    @property
    def reloader_running(self) -> bool:
        """Check if the ServiceReloader is currently running."""

    def reload(self) -> None:
        """Forces `AppState` to check for new `ServiceCards` and reload if necessary."""

    def start_reloader(self) -> None:
        """Starts the `AppState` reloader."""

    def stop_reloader(self) -> None:
        """Stops the `AppState` reloader."""

    def shutdown(self) -> None:
        """Shuts down the `AppState` `ScouterQueue` and reloader if running.
        This is a destructive operation and will attempt to close all background threads
        associated with the `ScouterQueue` and reloader. Only use this method with graceful
        shutdown procedures in mind.
        """

########################################################################################
#  This section contains the type definitions for the opsmlspec file
# ######################################################################################

class SpaceConfig:
    """Configuration for service space or team designation.

    A service must belong to either a space or a team (mutually exclusive).
    """

    def __init__(self, space: Optional[str] = None, team: Optional[str] = None):
        """Initialize space configuration.

        Args:
            space: Space name for general use
            team: Team name for team-based organization

        Raises:
            ValueError: If both or neither space and team are provided
        """

    @property
    def space(self) -> Optional[str]:
        """Return the space name if this is a space-based config."""

    @property
    def team(self) -> Optional[str]:
        """Return the team name if this is a team-based config."""

class ServiceMetadata:
    def __init__(
        self,
        description: str,
        language: Optional[str] = None,
        tags: List[str] = [],
    ):
        """Initialize service metadata.

        Args:
            description:
                Description of the service (required)
            language:
                Programming language used (e.g., 'python'). Defaults to None
            tags:
                Tags for categorization and search. Defaults to empty list
        """

    @property
    def description(self) -> str:
        """Service description."""

    @property
    def language(self) -> Optional[str]:
        """Programming language used by the service."""

    @property
    def tags(self) -> List[str]:
        """Tags for categorization."""

class ServiceConfig:
    def __init__(
        self,
        version: Optional[str] = None,
        cards: Optional[List[Card]] = None,
        write_dir: Optional[str] = None,
        mcp: Optional[McpConfig] = None,
    ):
        """Initialize service configuration.

        Args:
            version:
                Version of the service. Defaults to None
            cards:
                List of cards included in the service. Defaults to None
            write_dir:
                Directory to write service artifacts to. Defaults to 'opsml_service'
            mcp:
                MCP configuration (required if service type is Mcp). Defaults to None
        """

    @property
    def version(self) -> Optional[str]:
        """Service version."""

    @property
    def cards(self) -> Optional[List[Card]]:
        """Cards included in this service."""

    @property
    def write_dir(self) -> Optional[str]:
        """Directory for writing service artifacts."""

    @property
    def mcp(self) -> Optional[McpConfig]:
        """MCP configuration if service type is Mcp."""

class GpuConfig:
    def __init__(
        self,
        gpu_type: str,
        count: int,
        memory: str,
    ):
        """Initialize GPU resource configuration.

        Args:
            gpu_type:
                GPU type identifier (e.g., 'nvidia-tesla-t4')
            count:
                Number of GPUs required
            memory:
                GPU memory per device (e.g., '16Gi')

        Raises:
            ValueError: If count is not positive or memory format is invalid
        """

    @property
    def gpu_type(self) -> str:
        """GPU type identifier."""

    @property
    def count(self) -> int:
        """Number of GPUs."""

    @property
    def memory(self) -> str:
        """GPU memory specification."""

class Resources:
    def __init__(
        self,
        cpu: int,
        memory: str,
        storage: str,
        gpu: Optional[GpuConfig] = None,
    ):
        """Initialize resource requirements for deployment.

        Args:
            cpu:
                Number of CPUs required
            memory:
                Amount of memory (e.g., '16Gi')
            storage:
                Storage capacity (e.g., '100Gi')
            gpu:
                GPU configuration if GPU resources are needed. Defaults to None

        Raises:
            ValueError: If cpu is not positive or memory/storage format is invalid
        """

    @property
    def cpu(self) -> int:
        """Number of CPUs required."""

    @property
    def memory(self) -> str:
        """Memory requirement specification."""

    @property
    def storage(self) -> str:
        """Storage requirement specification."""

    @property
    def gpu(self) -> Optional[GpuConfig]:
        """GPU configuration if enabled."""

class DeploymentConfig:
    def __init__(
        self,
        environment: str,
        endpoints: List[str],
        provider: Optional[str] = None,
        location: Optional[List[str]] = None,
        resources: Optional[Resources] = None,
        links: Optional[Dict[str, str]] = None,
    ):
        """Initialize deployment configuration.

        Args:
            environment:
                Deployment environment (e.g., 'development', 'production')
            endpoints:
                List of endpoint URLs for the deployed service
            provider:
                Cloud provider (e.g., 'gcp', 'aws'). Defaults to None
            location:
                Deployment locations/regions. Defaults to None
            resources:
                Resource requirements for deployment. Defaults to None
            links:
                Related links (e.g., logging, monitoring URLs). Defaults to None

        Raises:
            ValueError: If endpoints list is empty
        """

    @property
    def environment(self) -> str:
        """Deployment environment name."""

    @property
    def provider(self) -> Optional[str]:
        """Cloud provider identifier."""

    @property
    def location(self) -> Optional[List[str]]:
        """Deployment locations/regions."""

    @property
    def endpoints(self) -> List[str]:
        """Service endpoint URLs."""

    @property
    def resources(self) -> Optional[Resources]:
        """Resource requirements for this deployment."""

    @property
    def links(self) -> Optional[Dict[str, str]]:
        """Related links for monitoring, logging, etc."""

class ServiceSpec:
    """Service specification representing the opsmlspec.yaml structure."""
    def __init__(
        self,
        name: str,
        space_config: SpaceConfig,
        service_type: ServiceType,
        metadata: Optional[ServiceMetadata] = None,
        service: Optional[ServiceConfig] = None,
        deploy: Optional[List[DeploymentConfig]] = None,
        root_path: Path = Path("."),
    ):
        """Initialize a service specification from opsmlspec.yaml.

        This class represents the complete service definition including
        metadata, card dependencies, and deployment configurations.

        Args:
            name:
                Name of the service (required)
            space_config:
                Space or team configuration (required)
            service_type:
                Type of service (Api, Mcp, or Agent) (required)
            metadata:
                Additional service metadata. Defaults to None
            service:
                Service configuration including cards and MCP settings. Defaults to None
            deploy:
                List of deployment configurations. Defaults to None
            root_path: Root path for the service specification file. Defaults to current directory

        Example:
            ```python
            spec = ServiceSpec(
                name="recommendation-api",
                space_config=SpaceConfig(space="data-science"),
                service_type=ServiceType.Api,
                metadata=ServiceMetadata(
                    description="Recommendation service",
                    language="python",
                    tags=["ml", "production"],
                ),
                service=ServiceConfig(
                    version="1.0.0",
                    cards=[
                        Card(
                            alias="recommender",
                            name="recommender-model",
                            registry_type=RegistryType.Model,
                            version="1.*",
                        )
                    ],
                ),
            )
            ```
        """

    @property
    def name(self) -> str:
        """Service name."""
    @name.setter
    def name(self, name: str) -> None:
        """Set the service name."""
    @property
    def space_config(self) -> SpaceConfig:
        """Space or team configuration."""
    @property
    def service_type(self) -> ServiceType:
        """Type of service (Api, Mcp, or Agent)."""
    @property
    def metadata(self) -> Optional[ServiceMetadata]:
        """Service metadata."""
    @property
    def service(self) -> Optional[ServiceConfig]:
        """Service configuration."""
    @property
    def deploy(self) -> Optional[List[DeploymentConfig]]:
        """Deployment configurations."""
    @property
    def root_path(self) -> Path:
        """Root path of the service specification file."""

    def from_path(self, path: Optional[Path] = None) -> "ServiceSpec":
        """Load the service specification from an opsmlspec.yaml file or
        a provided path.

        Args:
            path (Optional[Path]):
                Optional path to the opsmlspec.yaml file. If not provided,
                the method will look for opsmlspec.yaml in the root_path.
        """

    def __str__(self) -> str:
        """String representation of the ServiceSpec."""

__all__ = [
    ### App
    "AppState",
    "ReloadConfig",
    #### Cards
    "Card",
    "CardRecord",
    "CardList",
    "CardRegistry",
    "CardRegistries",
    "DataCard",
    "DataCardMetadata",
    "RegistryType",
    "RegistryMode",
    "ModelCard",
    "ModelCardMetadata",
    "ExperimentCard",
    "ComputeEnvironment",
    "PromptCard",
    "ServiceCard",
    "ServiceType",
    "download_service",
    #### Data
    "ColType",
    "ColValType",
    "ColumnSplit",
    "StartStopSplit",
    "IndiceSplit",
    "DataSplit",
    "DataSplits",
    "Data",
    "DependentVars",
    "Inequality",
    "DataSplitter",
    "DataInterface",
    "SqlLogic",
    "DataInterfaceSaveMetadata",
    "DataInterfaceMetadata",
    "NumpyData",
    "PolarsData",
    "PandasData",
    "ArrowData",
    "TorchData",
    "SqlData",
    "generate_feature_schema",
    "DataSaveKwargs",
    "DataLoadKwargs",
    "DataInterfaceType",
    #### Model
    "HuggingFaceORTModel",
    "HuggingFaceOnnxArgs",
    "ModelInterfaceMetadata",
    "ModelInterfaceSaveMetadata",
    "ModelInterfaceType",
    "ModelInterface",
    "TaskType",
    "SklearnModel",
    "DataProcessor",
    "LightGBMModel",
    "ModelType",
    "XGBoostModel",
    "TorchModel",
    "LightningModel",
    "HuggingFaceTask",
    "HuggingFaceModel",
    "OnnxModel",
    "CatBoostModel",
    "OnnxSession",
    "TensorFlowModel",
    "ModelLoadKwargs",
    "ModelSaveKwargs",
    "OnnxSchema",
    "ProcessorType",
    #### Types
    "CommonKwargs",
    "SaveName",
    "Suffix",
    "VersionType",
    "DriftProfileUri",
    "DriftArgs",
    "DriftProfileMap",
    "DataType",
    "ExtraMetadata",
    "Feature",
    "FeatureSchema",
    # Experiment
    "Experiment",
    "start_experiment",
    "ExperimentMetric",
    "ExperimentMetrics",
    "EvalMetrics",
    "Parameter",
    "Parameters",
    "get_experiment_metrics",
    "get_experiment_parameters",
    "download_artifact",
    "LLMEvaluator",
    ## Evaluate
    "LLMEvalTaskResult",
    "LLMEvalMetric",
    "LLMEvalResults",
    "LLMEvalRecord",
    "evaluate_llm",
    "EvaluationConfig",
    ## GenAI
    "PromptTokenDetails",
    "CompletionTokenDetails",
    "Usage",
    "ImageUrl",
    "AudioUrl",
    "BinaryContent",
    "DocumentUrl",
    "Message",
    "ModelSettings",
    "Prompt",
    "Provider",
    "TaskStatus",
    "AgentResponse",
    "Task",
    "TaskList",
    "Agent",
    "Workflow",
    "PyTask",
    "ChatResponse",
    "EventDetails",
    "TaskEvent",
    "WorkflowResult",
    "Score",
    "Embedder",
    ## Scouter
    "AlertZone",
    "SpcAlertType",
    "SpcAlertRule",
    "PsiAlertConfig",
    "SpcAlertConfig",
    "SpcAlert",
    "AlertThreshold",
    "CustomMetricAlertCondition",
    "CustomMetricAlertConfig",
    "SlackDispatchConfig",
    "OpsGenieDispatchConfig",
    "ConsoleDispatchConfig",
    "AlertDispatchType",
    "PsiNormalThreshold",
    "PsiChiSquareThreshold",
    "PsiFixedThreshold",
    "LLMMetricAlertCondition",
    "LLMAlertConfig",
    "TimeInterval",
    "DriftRequest",
    "ScouterClient",
    "BinnedMetricStats",
    "BinnedMetric",
    "BinnedMetrics",
    "BinnedPsiMetric",
    "BinnedPsiFeatureMetrics",
    "SpcDriftFeature",
    "BinnedSpcFeatureMetrics",
    "HttpConfig",
    "ProfileStatusRequest",
    "Alert",
    "DriftAlertRequest",
    "GetProfileRequest",
    "FeatureMap",
    "SpcFeatureDriftProfile",
    "SpcDriftConfig",
    "SpcDriftProfile",
    "SpcFeatureDrift",
    "SpcDriftMap",
    "PsiDriftConfig",
    "PsiDriftProfile",
    "PsiDriftMap",
    "CustomMetricDriftConfig",
    "CustomMetric",
    "CustomDriftProfile",
    "LLMDriftMetric",
    "LLMDriftConfig",
    "LLMDriftProfile",
    "Drifter",
    "LatencyMetrics",
    "RouteMetrics",
    "ObservabilityMetrics",
    "Observer",
    "Distinct",
    "Quantiles",
    "Histogram",
    "NumericStats",
    "CharStats",
    "WordStats",
    "StringStats",
    "FeatureProfile",
    "DataProfile",
    "DataProfiler",
    "ScouterQueue",
    "Queue",
    "KafkaConfig",
    "RabbitMQConfig",
    "RedisConfig",
    "SpcServerRecord",
    "PsiServerRecord",
    "CustomMetricServerRecord",
    "ServerRecord",
    "ServerRecords",
    "QueueFeature",
    "Features",
    "RecordType",
    "Metric",
    "Metrics",
    "LLMRecord",
    "EntityType",
    "DriftType",
    "CommonCrons",
    "ScouterDataType",
    # scouter tracing
    "init_tracer",
    "SpanKind",
    "FunctionType",
    "ActiveSpan",
    "ExportConfig",
    "GrpcConfig",
    "GrpcSpanExporter",
    "OtelHttpConfig",
    "HttpSpanExporter",
    "StdoutSpanExporter",
    "OtelProtocol",
    "TraceRecord",
    "TraceSpanRecord",
    "TraceBaggageRecord",
    "TestSpanExporter",
    "flush_tracer",
    "BatchConfig",
    "shutdown_tracer",
    # Logging
    "LogLevel",
    "RustyLogger",
    "LoggingConfig",
    "WriteLevel",
    # Mock
    "OpsmlTestServer",
    "OpsmlServerContext",
    "LLMTestServer",
    "MockConfig",
    "RegistryTestHelper",
]
