// OpenAI Chat Settings TypeScript Interfaces

export interface AudioParam {
  format: string;
  voice: string;
}

export interface ContentPart {
  type: string;
  text: string;
}

export type Content = string | ContentPart[];

export interface Prediction {
  type: string;
  content: Content;
}

export interface StreamOptions {
  include_obfuscation?: boolean;
  include_usage?: boolean;
}

export type ToolChoiceMode = "none" | "auto" | "required";

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
  type: "custom";
  custom: CustomChoice;
}

export interface ToolDefinition {
  type: "function";
  function: FunctionChoice;
}

export type AllowedToolsMode = "auto" | "required";

export interface InnerAllowedTools {
  mode: AllowedToolsMode;
  tools: ToolDefinition[];
}

export interface AllowedTools {
  type: "allowed_tools";
  allowed_tools: InnerAllowedTools;
}

export type ToolChoice =
  | ToolChoiceMode
  | FunctionToolChoice
  | CustomToolChoice
  | AllowedTools;

export interface FunctionDefinition {
  name: string;
  description?: string;
  parameters?: Record<string, any>;
  strict?: boolean;
}

export interface FunctionTool {
  type: string;
  function: FunctionDefinition;
}

export interface TextFormat {
  type: string;
}

export interface Grammar {
  definition: string;
  syntax: string;
}

export interface GrammarFormat {
  type: string;
  grammar: Grammar;
}

export type CustomToolFormat = TextFormat | GrammarFormat;

export interface CustomDefinition {
  name: string;
  description?: string;
  format?: CustomToolFormat;
}

export interface CustomTool {
  type: string;
  custom: CustomDefinition;
}

export type Tool = FunctionTool | CustomTool;

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
  extra_body?: Record<string, any>;
}

export function isOpenAIChatSettingsEmpty(
  settings?: OpenAIChatSettings
): boolean {
  if (!settings) return true;

  return Object.values(settings).every(
    (value) =>
      value === undefined ||
      value === null ||
      (Array.isArray(value) && value.length === 0) ||
      (typeof value === "object" && Object.keys(value).length === 0)
  );
}

export interface PillData {
  key: string;
  value: any;
  textSize?: string;
}

export function extractOpenAISettingsPills(
  settings: OpenAIChatSettings,
  textSize: string = "text-sm"
): PillData[] {
  const pills: PillData[] = [];

  // Define which fields to extract (simple values only)
  const simpleFields: Array<{
    key: keyof OpenAIChatSettings;
    displayName: string;
  }> = [
    { key: "max_completion_tokens", displayName: "Max Completion Tokens" },
    { key: "temperature", displayName: "Temperature" },
    { key: "top_p", displayName: "Top P" },
    { key: "top_k", displayName: "Top K" },
    { key: "frequency_penalty", displayName: "Frequency Penalty" },
    { key: "timeout", displayName: "Timeout" },
    { key: "parallel_tool_calls", displayName: "Parallel Tool Calls" },
    { key: "seed", displayName: "Seed" },
    { key: "logprobs", displayName: "Log Probs" },
    { key: "n", displayName: "N" },
    { key: "presence_penalty", displayName: "Presence Penalty" },
    { key: "prompt_cache_key", displayName: "Prompt Cache Key" },
    { key: "reasoning_effort", displayName: "Reasoning Effort" },
    { key: "safety_identifier", displayName: "Safety Identifier" },
    { key: "service_tier", displayName: "Service Tier" },
    { key: "store", displayName: "Store" },
    { key: "stream", displayName: "Stream" },
    { key: "top_logprobs", displayName: "Top Log Probs" },
    { key: "verbosity", displayName: "Verbosity" },
  ];

  // Extract simple field values
  for (const field of simpleFields) {
    const value = settings[field.key];
    if (value !== undefined && value !== null) {
      pills.push({
        key: field.displayName,
        value: value,
        textSize,
      });
    }
  }

  return pills;
}

// Utility functions for loading from JSON
export function loadOpenAIChatSettings(json: string): OpenAIChatSettings {
  return JSON.parse(json) as OpenAIChatSettings;
}

export function loadOpenAIChatSettingsFromObject(obj: any): OpenAIChatSettings {
  return obj as OpenAIChatSettings;
}

// Type guards for discriminated unions
export function isTextContent(content: Content): content is string {
  return typeof content === "string";
}

export function isArrayContent(content: Content): content is ContentPart[] {
  return Array.isArray(content);
}

export function isToolChoiceMode(choice: ToolChoice): choice is ToolChoiceMode {
  return typeof choice === "string";
}

export function isFunctionToolChoice(
  choice: ToolChoice
): choice is FunctionToolChoice {
  return (
    typeof choice === "object" && "type" in choice && choice.type === "function"
  );
}

export function isCustomToolChoice(
  choice: ToolChoice
): choice is CustomToolChoice {
  return (
    typeof choice === "object" && "type" in choice && choice.type === "custom"
  );
}

export function isAllowedTools(choice: ToolChoice): choice is AllowedTools {
  return (
    typeof choice === "object" &&
    "type" in choice &&
    choice.type === "allowed_tools"
  );
}

export function isFunctionTool(tool: Tool): tool is FunctionTool {
  return "function" in tool;
}

export function isCustomTool(tool: Tool): tool is CustomTool {
  return "custom" in tool;
}

export function isTextFormat(format: CustomToolFormat): format is TextFormat {
  return "type" in format && !("grammar" in format);
}

export function isGrammarFormat(
  format: CustomToolFormat
): format is GrammarFormat {
  return "grammar" in format;
}
