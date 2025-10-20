/**
 * Gemini model settings and supporting types.
 * Strictly typed for SSR, hydration, and maintainability in SvelteKit.
 */

export enum SchemaType {
  TypeUnspecified = "TypeUnspecified",
  String = "String",
  Number = "Number",
  Integer = "Integer",
  Boolean = "Boolean",
  Array = "Array",
  Object = "Object",
  Null = "Null",
}

export interface Schema {
  type?: SchemaType;
  format?: string;
  title?: string;
  description?: string;
  nullable?: boolean;
  default?: unknown;
  items?: Schema;
  min_items?: string;
  max_items?: string;
  enum?: string[];
  properties?: Record<string, Schema>;
  property_ordering?: string[];
  required?: string[];
  min_properties?: string;
  max_properties?: string;
  minimum?: number;
  maximum?: number;
  min_length?: string;
  max_length?: string;
  pattern?: string;
  example?: unknown;
  any_of?: Schema[];
  additional_properties?: unknown;
  ref_path?: string;
  defs?: Record<string, Schema>;
}

export enum HarmCategory {
  HarmCategoryUnspecified = "HarmCategoryUnspecified",
  HarmCategoryHateSpeech = "HarmCategoryHateSpeech",
  HarmCategoryDangerousContent = "HarmCategoryDangerousContent",
  HarmCategoryHarassment = "HarmCategoryHarassment",
  HarmCategorySexuallyExplicit = "HarmCategorySexuallyExplicit",
  HarmCategoryImageHate = "HarmCategoryImageHate",
  HarmCategoryImageDangerousContent = "HarmCategoryImageDangerousContent",
  HarmCategoryImageHarassment = "HarmCategoryImageHarassment",
  HarmCategoryImageSexuallyExplicit = "HarmCategoryImageSexuallyExplicit",
}

export enum HarmBlockThreshold {
  HarmBlockThresholdUnspecified = "HarmBlockThresholdUnspecified",
  BlockLowAndAbove = "BlockLowAndAbove",
  BlockMediumAndAbove = "BlockMediumAndAbove",
  BlockOnlyHigh = "BlockOnlyHigh",
  BlockNone = "BlockNone",
  Off = "Off",
}

export enum HarmBlockMethod {
  HarmBlockMethodUnspecified = "HarmBlockMethodUnspecified",
  Severity = "Severity",
  Probability = "Probability",
}

export interface SafetySetting {
  category: HarmCategory;
  threshold: HarmBlockThreshold;
  method?: HarmBlockMethod;
}

export enum Modality {
  ModalityUnspecified = "ModalityUnspecified",
  Text = "Text",
  Image = "Image",
  Audio = "Audio",
}

export enum MediaResolution {
  MediaResolutionUnspecified = "MediaResolutionUnspecified",
  MediaResolutionLow = "MediaResolutionLow",
  MediaResolutionMedium = "MediaResolutionMedium",
  MediaResolutionHigh = "MediaResolutionHigh",
}

export enum ModelRoutingPreference {
  Unknown = "Unknown",
  PrioritizeQuality = "PrioritizeQuality",
  Balanced = "Balanced",
  PrioritizeCost = "PrioritizeCost",
}

export interface ThinkingConfig {
  include_thoughts?: boolean;
  thinking_budget?: number;
}

export interface AutoRoutingMode {
  model_routing_preference?: ModelRoutingPreference;
}

export interface ManualRoutingMode {
  model_name: string;
}

export type RoutingConfigMode = AutoRoutingMode | ManualRoutingMode;

export interface RoutingConfig {
  routing_config: RoutingConfigMode;
}

export interface PrebuiltVoiceConfig {
  voice_name: string;
}

export type VoiceConfigMode = PrebuiltVoiceConfig;

export interface VoiceConfig {
  voice_config: VoiceConfigMode;
}

export interface SpeechConfig {
  voice_config?: VoiceConfig;
  language_code?: string;
}

export interface GenerationConfig {
  stop_sequences?: string[];
  response_mime_type?: string;
  response_modalities?: Modality[];
  thinking_config?: ThinkingConfig;
  temperature?: number;
  top_p?: number;
  top_k?: number;
  candidate_count?: number;
  max_output_tokens?: number;
  response_logprobs?: boolean;
  logprobs?: number;
  presence_penalty?: number;
  frequency_penalty?: number;
  seed?: number;
  response_schema?: Schema;
  response_json_schema?: unknown;
  routing_config?: RoutingConfig;
  audio_timestamp?: boolean;
  media_resolution?: MediaResolution;
  speech_config?: SpeechConfig;
  enable_affective_dialog?: boolean;
}

export interface ModelArmorConfig {
  prompt_template_name?: string;
  response_template_name?: string;
}

export enum Mode {
  ModeUnspecified = "ModeUnspecified",
  Any = "Any",
  Auto = "Auto",
  None = "None",
}

export interface FunctionCallingConfig {
  mode?: Mode;
  allowed_function_names?: string[];
}

export interface LatLng {
  latitude: number;
  longitude: number;
}

export interface RetrievalConfig {
  lat_lng: LatLng;
  language_code: string;
}

export interface ToolConfig {
  function_calling_config?: FunctionCallingConfig;
  retrieval_config?: RetrievalConfig;
}

export interface GeminiSettings {
  labels?: Record<string, string>;
  tool_config?: ToolConfig;
  generation_config?: GenerationConfig;
  safety_settings?: SafetySetting[];
  model_armor_config?: ModelArmorConfig;
  extra_body?: unknown;
}
