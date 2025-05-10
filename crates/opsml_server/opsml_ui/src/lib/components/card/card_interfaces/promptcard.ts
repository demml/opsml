import { RegistryType } from "$lib/utils";

enum RiskLevel {
  Safe = 0,
  Low = 1,
  Medium = 2,
  High = 3,
  Critical = 4,
}

// PII Configuration interface
interface PIIConfig {
  checkEmail: boolean;
  checkPhone: boolean;
  checkCreditCard: boolean;
  checkSsn: boolean;
  checkIp: boolean;
  checkPassword: boolean;
  checkAddress: boolean;
  checkName: boolean;
  checkDob: boolean;
  customPiiPatterns: string[];
}

// Main sanitization configuration interface
interface SanitizationConfig {
  // Minimum risk level that will cause rejection
  riskThreshold: RiskLevel;

  // Whether to sanitize delimiters (like ``` or ---)
  checkDelimiters: boolean;

  // Whether to sanitize common prompt injection keywords
  checkKeywords: boolean;

  // Whether to sanitize control characters
  checkControlChars: boolean;

  // Custom regex patterns to detect and sanitize
  customPatterns: string[];

  // PII detection configuration
  checkPii: boolean;

  // Whether to sanitize or just detect issues
  sanitize: boolean;

  // Whether to throw error on high risk or just sanitize
  errorOnHighRisk: boolean;

  // PII detection configuration
  piiConfig: PIIConfig;
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

export interface Message {
  content: PromptContent;
  next_param: number;
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
  prompt: Message[];
  system_prompt: Message[];
  sanitization_config: SanitizationConfig | undefined;
  version: string;
  model_settings: ModelSettings;
}

export interface PromptCardMetadata {
  experimentcard_uid?: string;
  auditcard_uid?: string;
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
