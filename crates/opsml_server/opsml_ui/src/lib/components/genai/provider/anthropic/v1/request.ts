import type { MessageNum } from "../../types";

// Content Block Types
export const BASE64_TYPE = "base64" as const;
export const URL_TYPE = "url" as const;
export const EPHEMERAL_TYPE = "ephemeral" as const;
export const IMAGE_TYPE = "image" as const;
export const TEXT_TYPE = "text" as const;
export const DOCUMENT_TYPE = "document" as const;
export const WEB_SEARCH_RESULT_TYPE = "web_search_result" as const;
export const SEARCH_TYPE = "search_result" as const;
export const THINKING_TYPE = "thinking" as const;
export const REDACTED_THINKING_TYPE = "redacted_thinking" as const;
export const TOOL_USE_TYPE = "tool_use" as const;
export const TOOL_RESULT_TYPE = "tool_result" as const;
export const WEB_SEARCH_TOOL_RESULT_TYPE = "web_search_tool_result" as const;
export const SERVER_TOOL_USE_TYPE = "server_tool_use" as const;

// MIME Types
export const DOCUMENT_BASE64_PDF_TYPE = "application/pdf" as const;
export const DOCUMENT_PLAIN_TEXT_TYPE = "text/plain" as const;

// Citation Types
export const CHAR_LOCATION_TYPE = "char_location" as const;
export const PAGE_LOCATION_TYPE = "page_location" as const;
export const CONTENT_BLOCK_LOCATION_TYPE = "content_block_location" as const;
export const WEB_SEARCH_RESULT_LOCATION_TYPE =
  "web_search_result_location" as const;
export const SEARCH_RESULT_LOCATION_TYPE = "search_result_location" as const;
export const WEB_SEARCH_TOOL_RESULT_ERROR_TYPE =
  "web_search_tool_result_error" as const;

export interface CitationCharLocationParam {
  type: typeof CHAR_LOCATION_TYPE;
  cited_text: string;
  document_index: number;
  document_title: string;
  end_char_index: number;
  start_char_index: number;
}

export interface CitationPageLocationParam {
  type: typeof PAGE_LOCATION_TYPE;
  cited_text: string;
  document_index: number;
  document_title: string;
  end_page_number: number;
  start_page_number: number;
}

export interface CitationContentBlockLocationParam {
  type: typeof CONTENT_BLOCK_LOCATION_TYPE;
  cited_text: string;
  document_index: number;
  document_title: string;
  end_block_index: number;
  start_block_index: number;
}

export interface CitationWebSearchResultLocationParam {
  type: typeof WEB_SEARCH_RESULT_LOCATION_TYPE;
  cited_text: string;
  encrypted_index: string;
  title: string;
  url: string;
}

export interface CitationSearchResultLocationParam {
  type: typeof SEARCH_RESULT_LOCATION_TYPE;
  cited_text: string;
  end_block_index: number;
  search_result_index: number;
  source: string;
  start_block_index: number;
  title: string;
}

/**
 * TypeScript Discriminated Union
 * Mirrors Rust: enum TextCitationParam
 */
export type TextCitationParam =
  | CitationCharLocationParam
  | CitationPageLocationParam
  | CitationContentBlockLocationParam
  | CitationWebSearchResultLocationParam
  | CitationSearchResultLocationParam;

/**
 * Anthropic Content Blocks & Source Mappings
 * Handling #[serde(untagged)] via Union Types
 */

// --- Base Types ---
export interface CacheControl {
  type: "ephemeral";
  ttl?: string;
}

export interface CitationsConfigParams {
  enabled?: boolean;
}

// --- Text Content ---
export interface TextBlockParam {
  type: typeof TEXT_TYPE;
  text: string;
  cache_control?: CacheControl;
  citations?: TextCitationParam;
}

// --- Image Sources (Untagged Serialization) ---
export interface Base64ImageSource {
  type: typeof BASE64_TYPE;
  media_type: string;
  data: string;
}

export interface UrlImageSource {
  type: typeof URL_TYPE;
  url: string;
}

/** * Mirrors Rust: ImageSource
 * Since ImageSource is untagged, the TS type is the union of the structures.
 */
export type ImageSource = Base64ImageSource | UrlImageSource;

export interface ImageBlockParam {
  type: typeof IMAGE_TYPE;
  source: ImageSource;
  cache_control?: CacheControl;
}

// --- Document Sources (Untagged Serialization) ---
export interface Base64PDFSource {
  type: typeof BASE64_TYPE;
  media_type: string; // usually application/pdf
  data: string;
}

export interface UrlPDFSource {
  type: typeof URL_TYPE;
  url: string;
}

export interface PlainTextSource {
  type: typeof TEXT_TYPE;
  media_type: string; // usually text/plain
  data: string;
}

/** * Mirrors Rust: DocumentSource (Untagged)
 */
export type DocumentSource = Base64PDFSource | UrlPDFSource | PlainTextSource;

export interface DocumentBlockParam {
  type: typeof DOCUMENT_TYPE;
  source: DocumentSource;
  cache_control?: CacheControl;
  title?: string;
  context?: string;
  citations?: CitationsConfigParams;
}

/**
 * Advanced Anthropic Content Blocks
 * Logic: Precise mapping of Tooling, Thinking, and Search results.
 */

// --- Search and Discovery ---
export interface SearchResultBlockParam {
  type: typeof SEARCH_TYPE;
  content: TextBlockParam[];
  source: string;
  title: string;
  cache_control?: CacheControl;
  citations?: CitationsConfigParams;
}

export interface WebSearchResultBlockParam {
  type: typeof WEB_SEARCH_RESULT_TYPE;
  encrypted_content: string;
  title: string;
  url: string;
  page_agent?: string;
}

// --- Thinking / Reasonance ---
export interface ThinkingBlockParam {
  type: typeof THINKING_TYPE;
  thinking: string;
  signature?: string;
}

export interface RedactedThinkingBlockParam {
  type: typeof REDACTED_THINKING_TYPE;
  data: string;
}

// --- Tooling ---
export interface ToolUseBlockParam {
  type: typeof TOOL_USE_TYPE;
  id: string;
  name: string;
  input: Record<string, any>; // Maps to serde_json::Value
  cache_control?: CacheControl;
}

export interface ServerToolUseBlockParam {
  type: typeof SERVER_TOOL_USE_TYPE;
  id: string;
  name: string;
  input: Record<string, any>;
  cache_control?: CacheControl;
}

/** * Mirrors Rust: ToolResultContentEnum (Untagged)
 * Logic: Since it is untagged, the serialized form is simply the array itself.
 */
export type ToolResultContent =
  | TextBlockParam[]
  | ImageBlockParam[]
  | DocumentBlockParam[]
  | SearchResultBlockParam[];

export interface ToolResultBlockParam {
  type: typeof TOOL_RESULT_TYPE;
  tool_use_id: string;
  is_error?: boolean;
  cache_control?: CacheControl;
  content?: ToolResultContent;
}

/**
 * Anthropic Request & Configuration Mappings
 * Handles #[serde(flatten)] and #[serde(untagged)] request structures.
 */

// --- Specialized Tool Results ---
export interface WebSearchToolResultBlockParam {
  type: typeof WEB_SEARCH_TOOL_RESULT_TYPE;
  tool_use_id: string;
  content: WebSearchResultBlockParam[];
  cache_control?: CacheControl;
}

// --- Content Block Union (Mirrors Rust: enum ContentBlock via untagged) ---
export type ContentBlock =
  | TextBlockParam
  | ImageBlockParam
  | DocumentBlockParam
  | SearchResultBlockParam
  | ThinkingBlockParam
  | RedactedThinkingBlockParam
  | ToolUseBlockParam
  | ToolResultBlockParam
  | ServerToolUseBlockParam
  | WebSearchResultBlockParam;

/** * Mirrors Rust: ContentBlockParam
 * Since 'inner' is flattened and untagged, the param is exactly the block.
 */
export type ContentBlockParam = ContentBlock;

export interface MessageParam {
  role: string;
  content: ContentBlockParam[];
}

// --- Configuration & Settings ---
export interface Metadata {
  user_id?: string;
}

export interface Tool {
  name: string;
  description?: string;
  input_schema: Record<string, any>; // Maps to serde_json::Value
  cache_control?: CacheControl;
}

export interface ThinkingConfig {
  type: string; // e.g., "enabled"
  budget_tokens?: number;
}

export interface ToolChoice {
  type: "auto" | "any" | "tool" | "none";
  disable_parallel_tool_use?: boolean;
  name?: string; // Required if type is "tool"
}

export interface AnthropicSettings {
  max_tokens: number;
  metadata?: Metadata;
  service_tier?: string;
  stop_sequences?: string[];
  stream?: boolean;
  system?: string;
  temperature?: number;
  thinking?: ThinkingConfig;
  tool_choice?: ToolChoice;
  tools?: Tool[];
  top_k?: number;
  top_p?: number;
  extra_body?: Record<string, any>;
}

// --- Request Wrappers ---

/**
 * Mirrors Rust: AnthropicMessageRequestV1
 * Logic: settings is flattened, so we use an Intersection Type (&)
 */
export type AnthropicMessageRequestV1 = {
  model: string;
  messages: MessageNum[]; // Maps to Vec<MessageNum>
  system: MessageNum[];
  output_format?: Record<string, any>;
} & AnthropicSettings;

export interface SystemPrompt {
  // Flattened Vec<TextBlockParam>
  content: TextBlockParam[];
}
