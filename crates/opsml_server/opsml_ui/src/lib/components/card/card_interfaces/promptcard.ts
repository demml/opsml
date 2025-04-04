import type { RegistryType } from "$lib/utils";

// Message types
export type MessagePartText = {
  text: string;
  type: string;
};

export type ImageUrl = {
  url: string;
  detail: string;
};

export type MessagePartImage = {
  image_url: ImageUrl;
  type: string;
};

export type InputAudio = {
  data: string;
  format: string;
};

export type MessagePartAudio = {
  input_audio: InputAudio;
  type: string;
};

export type MessagePart =
  | { Text: MessagePartText }
  | { Image: MessagePartImage }
  | { Audio: MessagePartAudio };

export type MessageContent = { Text: string } | { Parts: MessagePart[] };

export interface Message {
  role: string;
  content: MessageContent;
  name?: string;
}

// Chat prompt types
export interface SanitizationConfig {
  sanitize: boolean;
  risk_threshold: number;
}

export interface SanitizedResult {
  original_text: string;
  sanitized_text: string;
  risk_level: number;
  issues: string[];
}

export interface Prompt {
  model: string;
  messages: Message[];
  additional_data?: Record<string, any>;
  version: string;
  sanitization_config?: SanitizationConfig;
  sanitized_results: SanitizedResult[];
  has_sanitize_error: boolean;
}

export interface PromptCardMetadata {
  experimentcard_uid?: string;
  auditcard_uid?: string;
}

export interface PromptCard {
  prompt: Prompt;
  space: string;
  name: string;
  version: string;
  uid: string;
  tags: string[];
  metadata: PromptCardMetadata;
  registry_type: RegistryType.Prompt;
  app_env: string;
  created_at: string; // ISO datetime string
  is_card: boolean;
}
