from typing import List, Optional

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
    def __init__(self, mode: Optional[Mode], allowed_function_names: Optional[list[str]]) -> None: ...

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
