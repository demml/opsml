import type { MessageParam, TextBlockParam } from "./anthropic/v1/request";
import type { AnthropicMessageResponse } from "./anthropic/v1/response";
import type { GeminiContent } from "./google/v1/generate/request";
import type { GenerateContentResponse } from "./google/v1/generate/response";
import type { ChatMessage } from "./openai/v1/chat/request";
import type { OpenAIChatResponse } from "./openai/v1/chat/response";

/**
 * Mirrors Rust: enum MessageNum (untagged)
 * This is the generic type returned by message accessors.
 */
export type MessageNum =
  | ChatMessage // OpenAI
  | MessageParam // Anthropic
  | GeminiContent // Gemini
  | TextBlockParam; // Anthropic System (Special Case)

export type ChatResponse =
  | { OpenAIV1: OpenAIChatResponse }
  | { GeminiV1: GenerateContentResponse }
  | { VertexGenerateV1: GenerateContentResponse }
  | { VertexPredictV1: any } // Replace 'any' if PredictResponse is defined
  | { AnthropicMessageV1: AnthropicMessageResponse };
