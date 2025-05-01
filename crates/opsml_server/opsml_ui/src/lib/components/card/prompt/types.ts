export interface Prompt {
  model: string;
  prompt: Message[];
  system_prompt: Message[];
  version: string;
}

export type MessageRole = "system" | "user";

export interface Message {
  content: PromptContent;
  next_param: number;
  role: MessageRole;
}

type PromptContent =
  | { Str: string }
  | { Audio: AudioUrl }
  | { Image: ImageUrl }
  | { Document: DocumentUrl }
  | { Binary: BinaryContent };

export interface AudioUrl {
  url: string;
  kind: string;
}

export interface ImageUrl {
  url: string;
  kind: string;
}

export interface DocumentUrl {
  url: string;
  kind: string;
}

export interface BinaryContent {
  data: Uint8Array;
  media_type: string;
  kind: string;
}
