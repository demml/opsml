import type { MessageParam, TextBlockParam } from "./anthropic/v1/request";
import type { GeminiContent } from "./google/v1/generate/request";
import type { ChatMessage } from "./openai/v1/chat/request";

/**
 * Mirrors Rust: enum MessageNum (untagged)
 * This is the generic type returned by message accessors.
 */
export type MessageNum =
  | ChatMessage // OpenAI
  | MessageParam // Anthropic
  | GeminiContent // Gemini
  | TextBlockParam; // Anthropic System (Special Case)
