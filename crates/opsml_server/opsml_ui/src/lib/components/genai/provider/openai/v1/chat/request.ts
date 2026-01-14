/**
 * OpenAI V1 Type Definitions
 * Logic: Strictly typed for multi-modal completion requests.
 * Focus: Discriminators for untagged ContentPart serialization.
 */

import type { MessageNum } from "../../../types";
import type { OpenAIChatSettings } from "./settings";

// --- Content Part Constants ---
export const OPENAI_CONTENT_PART_TEXT = "text" as const;
export const OPENAI_CONTENT_PART_IMAGE_URL = "image_url" as const;
export const OPENAI_CONTENT_PART_INPUT_AUDIO = "input_audio" as const;
export const OPENAI_CONTENT_PART_FILE = "file" as const;

// --- Specialized Content Structures ---

export interface File {
  file_data?: string;
  file_id?: string;
  filename?: string;
}

export interface FileContentPart {
  type: typeof OPENAI_CONTENT_PART_FILE;
  file: File;
}

export interface InputAudioData {
  data: string; // Base64 encoded audio
  format: string; // e.g., "wav", "mp3"
}

export interface InputAudioContentPart {
  type: typeof OPENAI_CONTENT_PART_INPUT_AUDIO;
  input_audio: InputAudioData;
}

export interface ImageUrl {
  url: string;
  detail?: "low" | "high" | "auto"; // Common OpenAI fidelity values
}

export interface ImageContentPart {
  type: typeof OPENAI_CONTENT_PART_IMAGE_URL;
  image_url: ImageUrl;
}

export interface TextContentPart {
  type: typeof OPENAI_CONTENT_PART_TEXT;
  text: string;
}

// --- Union & Message Logic ---

/**
 * Mirrors Rust: enum ContentPart (untagged)
 * Logic: TypeScript discriminated union allows for clean type-guards.
 */
export type ContentPart =
  | TextContentPart
  | ImageContentPart
  | InputAudioContentPart
  | FileContentPart;

export interface ChatMessage {
  role: "system" | "user" | "assistant" | "tool";
  content: ContentPart[];
  name?: string;
}

// --- Top Level Request ---

/**
 * Mirrors Rust: OpenAIChatCompletionRequestV1
 * Logic: Flattened settings for high-performance direct serialization.
 */
export type OpenAIChatCompletionRequestV1 = {
  model: string;
  messages: MessageNum[]; // Maps to Vec<MessageNum>
  response_format?: Record<string, any>;
} & OpenAIChatSettings; // Flattened per #[serde(flatten)]
