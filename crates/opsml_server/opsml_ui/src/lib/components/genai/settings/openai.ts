/**
 * OpenAIChatSettings and supporting types.
 * Strictly typed for SvelteKit SSR and hydration.
 */

// Audio parameter settings for model
export interface AudioParam {
  format: string;
  voice: string;
}

// Content part for multi-part content
export interface ContentPart {
  type: string;
  text: string;
}

// Content can be a simple string or an array of parts
export type Content = string | ContentPart[];

// Prediction output type
export interface Prediction {
  type: string;
  content: Content;
}

// Streaming options for model output
export interface StreamOptions {
  include_obfuscation?: boolean;
  include_usage?: boolean;
}

// Tool choice modes
export type ToolChoiceMode = "none" | "auto" | "required";

// Function tool choice specification
export interface FunctionChoice {
  name: string;
}

// Function tool choice object
export interface FunctionToolChoice {
  type: "function";
  function: FunctionChoice;
}

// Custom tool choice specification
export interface CustomChoice {
  name: string;
}

// Custom tool choice object
export interface CustomToolChoice {
  type: "custom";
  custom: CustomChoice;
}

// Tool definition for allowed tools
export interface ToolDefinition {
  type: "function";
  function: FunctionChoice;
}

// Allowed tools mode
export type AllowedToolsMode = "auto" | "required";

// Inner allowed tools configuration
export interface InnerAllowedTools {
  mode: AllowedToolsMode;
  tools: ToolDefinition[];
}

// Allowed tools configuration
export interface AllowedTools {
  type: "allowed_tools";
  allowed_tools: InnerAllowedTools;
}

// Tool choice union
export type ToolChoice =
  | { mode: ToolChoiceMode }
  | FunctionToolChoice
  | CustomToolChoice
  | AllowedTools;

// Function definition for tool
export interface FunctionDefinition {
  name: string;
  description?: string;
  parameters?: unknown;
  strict?: boolean;
}

// Function tool for model
export interface FunctionTool {
  function: FunctionDefinition;
  type: "function";
}

// Text format for custom tool
export interface TextFormat {
  type: string;
}

// Grammar format for custom tool
export interface Grammar {
  definition: string;
  syntax: string;
}

export interface GrammarFormat {
  grammar: Grammar;
  type: string;
}

// Custom tool format union
export type CustomToolFormat = TextFormat | GrammarFormat;

// Custom tool definition
export interface CustomDefinition {
  name: string;
  description?: string;
  format?: CustomToolFormat;
}

// Custom tool for model
export interface CustomTool {
  custom: CustomDefinition;
  type: "custom";
}

// Tool union
export type Tool = FunctionTool | CustomTool;

// OpenAIChatSettings main interface
export interface OpenAIChatSettings {
  max_completion_tokens?: number;
  temperature?: number;
  top_p?: number;
  top_k?: number;
  frequency_penalty?: number;
  timeout?: number;
  parallel_tool_calls?: boolean;
  seed?: number;
  logit_bias?: Record<string, number>;
  stop_sequences?: string[];
  logprobs?: boolean;
  audio?: AudioParam;
  metadata?: Record<string, string>;
  modalities?: string[];
  n?: number;
  prediction?: Prediction;
  presence_penalty?: number;
  prompt_cache_key?: string;
  reasoning_effort?: string;
  safety_identifier?: string;
  service_tier?: string;
  store?: boolean;
  stream?: boolean;
  stream_options?: StreamOptions;
  tool_choice?: ToolChoice;
  tools?: Tool[];
  top_logprobs?: number;
  verbosity?: string;
  extra_body?: unknown;
}
