/**
 * OpenAI V1 Settings & Tooling Stubs
 * Logic: Precise mapping of untagged content and tool choice constraints.
 */

// --- Audio & Predictions ---

export interface AudioParam {
  format: string; // e.g., "wav", "mp3", "flac"
  voice: string; // e.g., "alloy", "echo", "shimmer"
}

export interface PredictionContentPart {
  type: string;
  text: string;
}

/** * Mirrors Rust: enum Content (untagged)
 */
export type PredictionContent = string | PredictionContentPart[];

export interface Prediction {
  type: string;
  content: PredictionContent;
}

export interface StreamOptions {
  include_obfuscation?: boolean;
  include_usage?: boolean;
}

// --- Tool Choice Logic ---

export enum ToolChoiceMode {
  NONE = "none",
  AUTO = "auto",
  REQUIRED = "required",
}

export interface FunctionChoice {
  name: string;
}

export interface FunctionToolChoice {
  type: "function";
  function: FunctionChoice;
}

export interface CustomChoice {
  name: string;
}

export interface CustomToolChoice {
  type: string;
  custom: CustomChoice;
}

/**
 * Union for specific tool selection
 */
export type ToolChoiceOption =
  | ToolChoiceMode
  | FunctionToolChoice
  | CustomToolChoice;

// --- Allowed Tools Constraints ---

export enum AllowedToolsMode {
  AUTO = "auto",
  REQUIRED = "required",
}

export interface ToolDefinition {
  type: string;
  function: FunctionChoice;
}

export interface InnerAllowedTools {
  mode: AllowedToolsMode;
  tools: ToolDefinition[];
}

export interface AllowedTools {
  type: "allowed_tools";
  allowed_tools: InnerAllowedTools;
}

/**
 * OpenAI V1 Tool & Format Stubs
 * Logic: Exhaustive mapping of untagged unions for Function and Custom tools.
 */

// --- Tool Choice ---

/**
 * Mirrors Rust: enum ToolChoice (untagged)
 */
export type ToolChoice =
  | ToolChoiceMode
  | FunctionToolChoice
  | CustomToolChoice
  | AllowedTools;

// --- Function Tooling ---

export interface FunctionDefinition {
  name: string;
  description?: string;
  /** Maps to serde_json::Value - JSON Schema for parameters */
  parameters?: Record<string, any>;
  strict?: boolean;
}

export interface FunctionTool {
  type: "function";
  function: FunctionDefinition;
}

// --- Custom Tooling & Grammars ---

export interface TextFormat {
  type: "text";
}

export interface Grammar {
  definition: string;
  syntax: "lark" | "regex" | string;
}

export interface GrammarFormat {
  type: "grammar";
  grammar: Grammar;
}

/**
 * Mirrors Rust: enum CustomToolFormat (untagged)
 */
export type CustomToolFormat = TextFormat | GrammarFormat;

export interface CustomDefinition {
  name: string;
  description?: string;
  format?: CustomToolFormat;
}

export interface CustomTool {
  type: "custom"; // Or specific custom type string
  custom: CustomDefinition;
}

// --- Top-Level Tool Mapping ---

/**
 * Mirrors Rust: enum Tool (untagged)
 */
export type Tool = FunctionTool | CustomTool;

/**
 * OpenAI Chat Settings Mapping
 * Logic: Direct 1-to-1 parity with OpenAIChatSettings struct.
 * Usage: Intersection with OpenAIChatCompletionRequestV1 for full request payload.
 */

export interface OpenAIChatSettings {
  max_completion_tokens?: number; // Maps to usize
  temperature?: number; // Maps to f32
  top_p?: number; // Maps to f32
  top_k?: number; // Maps to i32
  frequency_penalty?: number; // Maps to f32
  timeout?: number; // Maps to f32 (seconds)
  parallel_tool_calls?: boolean;
  seed?: number; // Maps to u64

  /** Maps to HashMap<String, i32> */
  logit_bias?: Record<string, number>;

  stop_sequences?: string[];
  logprobs?: boolean;

  /** AudioParam mapped in previous step */
  audio?: AudioParam;

  /** Maps to HashMap<String, String> */
  metadata?: Record<string, string>;

  modalities?: string[]; // e.g., ["text", "audio"]
  n?: number; // Maps to usize

  /** Prediction mapped in previous step */
  prediction?: Prediction;

  presence_penalty?: number; // Maps to f32
  prompt_cache_key?: string;

  /** Reasoning effort for o1/o3 series models: "low", "medium", "high" */
  reasoning_effort?: string;

  safety_identifier?: string;
  service_tier?: string; // e.g., "scale" or "default"
  store?: boolean;
  stream?: boolean;

  /** StreamOptions mapped in previous step */
  stream_options?: StreamOptions;

  /** ToolChoice mapped in previous step (Untagged Union) */
  tool_choice?: ToolChoice;

  /** Tool mapped in previous step (Untagged Union) */
  tools?: Tool[];

  top_logprobs?: number; // Maps to i32
  verbosity?: string;

  /** Maps to serde_json::Value - for experimental parameters */
  extra_body?: Record<string, any>;
}
