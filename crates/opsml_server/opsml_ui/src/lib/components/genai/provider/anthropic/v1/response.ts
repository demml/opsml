import type { JsonValue } from "$lib/types";

/**
 * Maps to 'pub struct CitationCharLocation'
 */
export interface CitationCharLocation {
  cited_text: string;
  document_index: number; // i32
  document_title: string;
  end_char_index: number;
  file_id: string;
  start_char_index: number;
  type: string; // From #[serde(rename = "type")]
}

/**
 * Maps to 'pub struct CitationPageLocation'
 */
export interface CitationPageLocation {
  cited_text: string;
  document_index: number;
  document_title: string;
  end_page_number: number;
  file_id: string;
  start_page_number: number;
  type: string;
}

/**
 * Maps to 'pub struct CitationContentBlockLocation'
 */
export interface CitationContentBlockLocation {
  cited_text: string;
  document_index: number;
  document_title: string;
  end_block_index: number;
  file_id: string;
  start_block_index: number;
  type: string;
}

/**
 * Maps to 'pub struct CitationsWebSearchResultLocation'
 */
export interface CitationsWebSearchResultLocation {
  cited_text: string;
  encrypted_index: string;
  title: string;
  type: string;
  url: string;
}

/**
 * Maps to 'pub struct CitationsSearchResultLocation'
 */
export interface CitationsSearchResultLocation {
  cited_text: string;
  end_block_index: number;
  search_result_index: number;
  source: string;
  start_block_index: number;
  title: string;
  type: string;
}

/**
 * Maps to 'pub enum TextCitation' (untagged)
 * Since it is untagged in Rust, TypeScript represents this as a union.
 */
export type TextCitation =
  | CitationCharLocation
  | CitationPageLocation
  | CitationContentBlockLocation
  | CitationsWebSearchResultLocation
  | CitationsSearchResultLocation;

/**
 * Maps to 'pub struct TextBlock'
 */
export interface TextBlock {
  text: string;
  citations?: TextCitation[]; // Option<Vec<TextCitation>> + skip_serializing_if
  type: string;
}

/**
 * Maps to 'pub struct ThinkingBlock'
 */
export interface ThinkingBlock {
  thinking: string;
  signature: string | null; // Option<String>
  type: string; // From #[serde(rename = "type")]
}

/**
 * Maps to 'pub struct RedactedThinkingBlock'
 */
export interface RedactedThinkingBlock {
  data: string;
  type: string;
}

/**
 * Maps to 'pub struct ToolUseBlock'
 */
export interface ToolUseBlock {
  id: string;
  name: string;
  input: JsonValue; // Value
  type: string;
}

/**
 * Maps to 'pub struct ServerToolUseBlock'
 */
export interface ServerToolUseBlock {
  id: string;
  name: string;
  input: JsonValue;
  type: string;
}

/**
 * Maps to 'pub struct WebSearchResultBlock'
 */
export interface WebSearchResultBlock {
  encrypted_content: string;
  page_age: string | null; // Option<String>
  title: string;
  type: string;
  url: string;
}

/**
 * Maps to 'pub struct WebSearchToolResultError'
 */
export interface WebSearchToolResultError {
  error_code: string;
  type: string;
}

/**
 * Maps to 'pub enum WebSearchToolResultBlockContent' (untagged)
 */
export type WebSearchToolResultBlockContent =
  | WebSearchToolResultError
  | WebSearchResultBlock[];

/**
 * Maps to 'pub struct WebSearchToolResultBlock'
 */
export interface WebSearchToolResultBlock {
  content: WebSearchToolResultBlockContent;
  tool_use_id: string;
  type: string;
}

/**
 * Maps to 'pub enum ResponseContentBlockInner' (untagged)
 */
export type ResponseContentBlockInner =
  | TextBlock
  | ThinkingBlock
  | RedactedThinkingBlock
  | ToolUseBlock
  | ServerToolUseBlock
  | WebSearchToolResultBlock;

/**
 * Maps to 'pub struct ResponseContentBlock'
 * Since 'inner' is marked with #[serde(flatten)], this interface
 * effectively becomes the Union of its inner variants.
 */
export type ResponseContentBlock = ResponseContentBlockInner;

/**
 * Maps to 'pub enum StopReason'
 * Renamed to snake_case per #[serde(rename_all = "snake_case")]
 */
export type StopReason =
  | "end_turn"
  | "max_tokens"
  | "stop_sequence"
  | "tool_use";

/**
 * Maps to 'pub struct Usage' (AnthropicUsage)
 */
export interface AnthropicUsage {
  input_tokens: number; // i32
  output_tokens: number;
  cache_creation_input_tokens?: number | null; // skip_serializing_if Option::is_none
  cache_read_input_tokens?: number | null;
  service_tier?: string | null;
}

/**
 * Maps to 'pub struct AnthropicMessageResponse'
 */
export interface AnthropicMessageResponse {
  id: string;
  model: string;
  role: string;
  stop_reason: StopReason | null; // Option<StopReason>
  stop_sequence: string | null;
  type: string; // r#type mapped per #[serde(rename = "type")] in previous context
  usage: AnthropicUsage;
  content: ResponseContentBlock[];
}
