/**
 * Maps to 'pub struct Function'
 */
export interface OpenAIFunction {
  arguments: string;
  name: string;
}

/**
 * Maps to 'pub struct ToolCall'
 */
export interface OpenAIToolCall {
  id: string;
  type: string;
  function: OpenAIFunction;
}

/**
 * Maps to 'pub struct UrlCitation'
 */
export interface OpenAIUrlCitation {
  end_index: number; // u64
  start_index: number; // u64
  title: string;
  url: string;
}

/**
 * Maps to 'pub struct Annotations'
 */
export interface OpenAIAnnotations {
  type: string;
  url_citations: OpenAIUrlCitation[];
}

/**
 * Maps to 'pub struct Audio'
 */
export interface OpenAIAudio {
  data: string;
  expires_at: number; // u64 Unix timestamp
  id: string;
  transcript: string;
}

/**
 * Maps to 'pub struct ChatCompletionMessage'
 */
export interface OpenAIChatCompletionMessage {
  content: string | null; // Option<String>
  refusal?: string | null; // skip_serializing_if Option::is_none
  role: string;
  annotations: OpenAIAnnotations[];
  tool_calls: OpenAIToolCall[];
  audio?: OpenAIAudio | null;
}

/**
 * Maps to 'pub struct TopLogProbs'
 */
export interface OpenAITopLogProbs {
  bytes: number[] | null; // Option<Vec<u8>>
  logprob: number; // f64
  token: string;
}

/**
 * Maps to 'pub struct LogContent'
 */
export interface OpenAILogContent {
  bytes: number[] | null;
  logprob: number;
  token: string;
  top_logprobs?: OpenAITopLogProbs[] | null;
}

/**
 * Maps to 'pub struct LogProbs'
 */
export interface OpenAILogProbs {
  content: OpenAILogContent[] | null;
  refusal: OpenAILogContent[] | null;
}

/**
 * Maps to 'pub struct Choice'
 */
export interface OpenAIChoice {
  message: OpenAIChatCompletionMessage;
  finish_reason: string;
  logprobs?: OpenAILogProbs | null;
}

/**
 * Maps to 'pub struct CompletionTokenDetails'
 */
export interface OpenAICompletionTokenDetails {
  accepted_prediction_tokens: number;
  audio_tokens: number;
  reasoning_tokens: number;
  rejected_prediction_tokens: number;
}

/**
 * Maps to 'pub struct PromptTokenDetails'
 */
export interface OpenAIPromptTokenDetails {
  audio_tokens: number;
  cached_tokens: number;
}

/**
 * Maps to 'pub struct Usage'
 */
export interface OpenAIUsage {
  completion_tokens: number;
  prompt_tokens: number;
  total_tokens: number;
  completion_tokens_details: OpenAICompletionTokenDetails;
  prompt_tokens_details: OpenAIPromptTokenDetails;
  finish_reason?: string | null;
}

/**
 * Maps to 'pub struct OpenAIChatResponse'
 */
export interface OpenAIChatResponse {
  id: string;
  object: string;
  created: number; // u64
  model: string;
  choices: OpenAIChoice[];
  usage: OpenAIUsage;
  service_tier?: string | null;
  system_fingerprint?: string | null;
}
