import { RegistryType } from "$lib/utils";
import type { DriftType } from "../model/monitoring/types";
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

export interface Message {
  content: PromptContent;
  next_param: number;
  role: string;
}

export interface ModelSettings {
  model: string;
  provider: string;
  max_token?: number;
  temperature?: number;
  top_p?: number;
  frequency_penalty?: number;
  presence_penalty?: number;
  timeout?: number;
  parallel_tool_calls?: boolean;
  seed?: number;
  logit_bias?: Record<string, number>;
  stop_sequences?: string[];
  extra_body?: any;
}

export interface Prompt {
  user_message: Message[];
  system_message: Message[];
  version: string;
  model_settings: ModelSettings;
  response_json_schema?: string;
  parameters: string[];
}

export interface DriftProfileUri {
  root_dir: string;
  uri: string;
  drift_type: DriftType;
}

export interface PromptCardMetadata {
  experimentcard_uid?: string;
  auditcard_uid?: string;
  drift_profile_uri_map?: Record<string, DriftProfileUri>;
}

export interface PromptCard {
  prompt: Prompt;
  name: string;
  space: string;
  version: string;
  uid: string;
  tags: string[];
  metadata: PromptCardMetadata;
  registry_type: RegistryType.Prompt;
  app_env: string;
  created_at: string; // ISO datetime string
  is_card: boolean;
  opsml_version: string;
}
