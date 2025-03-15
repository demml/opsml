from typing import List, Optional

class OpenAIConfig:
    def __init__(
        self,
        api_key: Optional[str] = None,
        url: Optional[str] = None,
        organization: Optional[str] = None,
        project: Optional[str] = None,
    ) -> None:
        """OpenAIConfig for configuring the OpenAI API.
        api_key and url will be sourced from the environment if not provided.

        Args:
            api_key (Optional[str]):
                The API key to use for the OpenAI API.
            url (Optional[str]):
                The URL to use for the OpenAI API.
        """

class PromptTokensDetails:
    audio_tokens: Optional[int]
    cached_tokens: Optional[int]

class CompletionTokensDetails:
    accepted_prediction_tokens: Optional[int]
    audio_tokens: Optional[int]
    reasoning_tokens: Optional[int]
    rejected_prediction_tokens: Optional[int]

class CompletionUsage:
    completion_tokens: int
    prompt_tokens: int
    total_tokens: int
    completion_tokens_details: Optional[CompletionTokensDetails]
    prompt_tokens_details: Optional[PromptTokensDetails]

class TopLogProb:
    token: str
    bytes: Optional[int]
    logprob: float

class ChatCompletionTokenLogprob:
    token: str
    bytes: Optional[int]
    logprob: float
    top_logprobs: Optional[List[TopLogProb]]

class ChoiceLogprobs:
    content: Optional[List[ChatCompletionTokenLogprob]]
    refusal: Optional[List[ChatCompletionTokenLogprob]]

class ChoiceDeltaFunctionCall:
    arguments: Optional[str]
    name: Optional[str]

class ChoiceDeltaToolCallFunction:
    arguments: Optional[str]
    name: Optional[str]

class ChoiceDeltaToolCall:
    index: int
    id: Optional[str]
    function: Optional[ChoiceDeltaToolCallFunction]
    type: Optional[str]

class ChoiceDelta:
    content: Optional[str]
    function_call: Optional[ChoiceDeltaFunctionCall]
    refusal: Optional[str]
    role: Optional[str]
    tool_calls: Optional[list[ChoiceDeltaToolCall]]

class ChunkChoice:
    delta: ChoiceDelta
    finish_reason: Optional[str]
    index: int
    logprobs: Optional[ChoiceLogprobs]

class ChatCompletionChunk:
    id: str
    choices: list[ChunkChoice]
    created: int
    model: str
    object: str
    service_tier: Optional[str]
    system_fingerprint: Optional[str]
    usage: Optional[CompletionUsage]
