import type { GeminiSettings } from "./settings/gemini";
import type { OpenAIChatSettings } from "./settings/openai";

/**
 * Provider enum for model sources.
 */
export enum Provider {
  OpenAI = "OpenAI",
  Gemini = "Gemini",
  Google = "Google",
  Vertex = "Vertex",
  Undefined = "Undefined",
}

/**
 * ResponseType enum for prompt responses.
 */
export enum ResponseType {
  Score = "Score",
  Pydantic = "Pydantic",
  Null = "Null",
}

/**
 * Audio URL type for audio content.
 */
export interface AudioUrl {
  url: string;
  kind: "audio-url";
}

/**
 * Image URL type for image content.
 */
export interface ImageUrl {
  url: string;
  kind: "image-url";
}

/**
 * Document URL type for document content.
 */
export interface DocumentUrl {
  url: string;
  kind: "document-url";
}

/**
 * Binary content type for arbitrary media.
 */
export interface BinaryContent {
  data: Uint8Array;
  media_type: string;
  kind: "binary";
}

/**
 * PromptContent union for all supported content types.
 */
export type PromptContent =
  | { Str: string }
  | { Audio: AudioUrl }
  | { Image: ImageUrl }
  | { Document: DocumentUrl }
  | { Binary: BinaryContent };

/**
 * Role enum for message sender/receiver.
 */
export enum Role {
  User = "user",
  Assistant = "assistant",
  Developer = "developer",
  Tool = "tool",
  Model = "model",
}

/**
 * Message structure for prompt conversations.
 */
export interface Message {
  content: PromptContent;
  role: Role | string;
  variables: string[];
}

/**
 * ModelSettings union for supported providers.
 */
export type ModelSettings =
  | { OpenAIChat: OpenAIChatSettings }
  | { GoogleChat: GeminiSettings };

/**
 * Main Prompt interface for LLM requests.
 */
export interface Prompt {
  message: Message[];
  system_instruction: Message[];
  model_settings: ModelSettings;
  model: string;
  provider: Provider;
  version: string;
  response_json_schema?: unknown;
  parameters: string[];
  response_type: ResponseType;
}
