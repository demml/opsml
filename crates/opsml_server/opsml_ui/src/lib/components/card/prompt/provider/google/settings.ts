// Gemini Settings TypeScript Interfaces

export type SchemaType =
  | "TYPE_UNSPECIFIED"
  | "STRING"
  | "NUMBER"
  | "INTEGER"
  | "BOOLEAN"
  | "ARRAY"
  | "OBJECT"
  | "NULL";

export interface Schema {
  type?: SchemaType;
  format?: string;
  title?: string;
  description?: string;
  nullable?: boolean;
  default?: any;
  items?: Schema;
  minItems?: string;
  maxItems?: string;
  enum?: string[];
  properties?: Record<string, Schema>;
  propertyOrdering?: string[];
  required?: string[];
  minProperties?: string;
  maxProperties?: string;
  minimum?: number;
  maximum?: number;
  minLength?: string;
  maxLength?: string;
  pattern?: string;
  example?: any;
  anyOf?: Schema[];
  additionalProperties?: any;
  ref?: string;
  defs?: Record<string, Schema>;
}

export type HarmCategory =
  | "HARM_CATEGORY_UNSPECIFIED"
  | "HARM_CATEGORY_HATE_SPEECH"
  | "HARM_CATEGORY_DANGEROUS_CONTENT"
  | "HARM_CATEGORY_HARASSMENT"
  | "HARM_CATEGORY_SEXUALLY_EXPLICIT"
  | "HARM_CATEGORY_IMAGE_HATE"
  | "HARM_CATEGORY_IMAGE_DANGEROUS_CONTENT"
  | "HARM_CATEGORY_IMAGE_HARASSMENT"
  | "HARM_CATEGORY_IMAGE_SEXUALLY_EXPLICIT";

export type HarmBlockThreshold =
  | "HARM_BLOCK_THRESHOLD_UNSPECIFIED"
  | "BLOCK_LOW_AND_ABOVE"
  | "BLOCK_MEDIUM_AND_ABOVE"
  | "BLOCK_ONLY_HIGH"
  | "BLOCK_NONE"
  | "OFF";

export type HarmBlockMethod =
  | "HARM_BLOCK_METHOD_UNSPECIFIED"
  | "SEVERITY"
  | "PROBABILITY";

export interface SafetySetting {
  category: HarmCategory;
  threshold: HarmBlockThreshold;
  method?: HarmBlockMethod;
}

export type Modality = "MODALITY_UNSPECIFIED" | "TEXT" | "IMAGE" | "AUDIO";

export type MediaResolution =
  | "MEDIA_RESOLUTION_UNSPECIFIED"
  | "MEDIA_RESOLUTION_LOW"
  | "MEDIA_RESOLUTION_MEDIUM"
  | "MEDIA_RESOLUTION_HIGH";

export type ModelRoutingPreference =
  | "UNKNOWN"
  | "PRIORITIZE_QUALITY"
  | "BALANCED"
  | "PRIORITIZE_COST";

export interface ThinkingConfig {
  includeThoughts?: boolean;
  thinkingBudget?: number;
}

export interface AutoRoutingMode {
  modelRoutingPreference?: ModelRoutingPreference;
}

export interface ManualRoutingMode {
  modelName: string;
}

export type RoutingConfigMode = AutoRoutingMode | ManualRoutingMode;

export interface RoutingConfig {
  routingConfig: RoutingConfigMode;
}

export interface PrebuiltVoiceConfig {
  voiceName: string;
}

export type VoiceConfigMode = {
  prebuiltVoiceConfig: PrebuiltVoiceConfig;
};

export interface VoiceConfig {
  voiceConfig: VoiceConfigMode;
}

export interface SpeechConfig {
  voiceConfig?: VoiceConfig;
  languageCode?: string;
}

export interface GenerationConfig {
  stopSequences?: string[];
  responseMimeType?: string;
  responseModalities?: Modality[];
  thinkingConfig?: ThinkingConfig;
  temperature?: number;
  topP?: number;
  topK?: number;
  candidateCount?: number;
  maxOutputTokens?: number;
  responseLogprobs?: boolean;
  logprobs?: number;
  presencePenalty?: number;
  frequencyPenalty?: number;
  seed?: number;
  responseSchema?: Schema;
  responseJsonSchema?: any;
  routingConfig?: RoutingConfig;
  audioTimestamp?: boolean;
  mediaResolution?: MediaResolution;
  speechConfig?: SpeechConfig;
  enableAffectiveDialog?: boolean;
}

export interface ModelArmorConfig {
  promptTemplateName?: string;
  responseTemplateName?: string;
}

export type Mode = "MODE_UNSPECIFIED" | "ANY" | "AUTO" | "NONE";

export interface FunctionCallingConfig {
  mode?: Mode;
  allowedFunctionNames?: string[];
}

export interface LatLng {
  latitude: number;
  longitude: number;
}

export interface RetrievalConfig {
  latLng: LatLng;
  languageCode: string;
}

export interface ToolConfig {
  functionCallingConfig?: FunctionCallingConfig;
  retrievalConfig?: RetrievalConfig;
}

export interface GeminiSettings {
  labels?: Record<string, string>;
  toolConfig?: ToolConfig;
  generationConfig?: GenerationConfig;
  safetySettings?: SafetySetting[];
  modelArmorConfig?: ModelArmorConfig;
  extraBody?: Record<string, any>;
}

/**
 * Interface for Pill component props
 */
export interface PillData {
  key: string;
  value: string | number | boolean;
  textSize?: string;
}

/**
 * Checks if Gemini settings object is empty or undefined
 * @param settings - The Gemini settings object
 * @returns true if settings is empty or all values are undefined/null
 */
export function isGeminiSettingsEmpty(settings?: GeminiSettings): boolean {
  if (!settings) return true;

  return Object.values(settings).every(
    (value) =>
      value === undefined ||
      value === null ||
      (Array.isArray(value) && value.length === 0) ||
      (typeof value === "object" && Object.keys(value).length === 0)
  );
}

/**
 * Extracts simple string, number, and boolean values from Gemini generation config
 * and formats them for Pill components
 * @param settings - The Gemini settings object
 * @param textSize - Optional text size for pills (default: "text-sm")
 * @returns Array of PillData objects for simple values
 */
export function extractGeminiSettingsPills(
  settings: GeminiSettings,
  textSize: string = "text-sm"
): PillData[] {
  const pills: PillData[] = [];

  // Extract generation config simple fields
  if (settings.generationConfig) {
    const genConfig = settings.generationConfig;

    const simpleGenFields: Array<{
      key: keyof GenerationConfig;
      displayName: string;
    }> = [
      { key: "temperature", displayName: "Temperature" },
      { key: "topP", displayName: "Top P" },
      { key: "topK", displayName: "Top K" },
      { key: "candidateCount", displayName: "Candidate Count" },
      { key: "maxOutputTokens", displayName: "Max Output Tokens" },
      { key: "responseLogprobs", displayName: "Response Log Probs" },
      { key: "logprobs", displayName: "Log Probs" },
      { key: "presencePenalty", displayName: "Presence Penalty" },
      { key: "frequencyPenalty", displayName: "Frequency Penalty" },
      { key: "seed", displayName: "Seed" },
      { key: "responseMimeType", displayName: "Response MIME Type" },
      { key: "audioTimestamp", displayName: "Audio Timestamp" },
      { key: "enableAffectiveDialog", displayName: "Affective Dialog" },
    ];

    for (const field of simpleGenFields) {
      const value = genConfig[field.key];
      if (value !== undefined && value !== null) {
        pills.push({
          key: field.displayName,
          value: value,
          textSize,
        });
      }
    }

    // Handle enum fields
    if (genConfig.mediaResolution) {
      pills.push({
        key: "Media Resolution",
        value: genConfig.mediaResolution,
        textSize,
      });
    }
  }

  // Extract thinking config if present
  if (settings.generationConfig?.thinkingConfig) {
    const thinkingConfig = settings.generationConfig.thinkingConfig;

    if (thinkingConfig.includeThoughts !== undefined) {
      pills.push({
        key: "Include Thoughts",
        value: thinkingConfig.includeThoughts,
        textSize,
      });
    }

    if (thinkingConfig.thinkingBudget !== undefined) {
      pills.push({
        key: "Thinking Budget",
        value: thinkingConfig.thinkingBudget,
        textSize,
      });
    }
  }

  return pills;
}

/**
 * Gets count of complex fields that have values (for display purposes)
 * @param settings - The Gemini settings object
 * @returns Object with counts of complex field types
 */
export function getGeminiComplexFieldCounts(settings: GeminiSettings): {
  labelsCount: number;
  stopSequencesCount: number;
  responseModalitiesCount: number;
  safetySettingsCount: number;
  hasToolConfig: boolean;
  hasModelArmorConfig: boolean;
  hasSpeechConfig: boolean;
  hasRoutingConfig: boolean;
  hasResponseSchema: boolean;
  hasExtraBody: boolean;
} {
  return {
    labelsCount: settings.labels ? Object.keys(settings.labels).length : 0,
    stopSequencesCount: settings.generationConfig?.stopSequences?.length ?? 0,
    responseModalitiesCount:
      settings.generationConfig?.responseModalities?.length ?? 0,
    safetySettingsCount: settings.safetySettings?.length ?? 0,
    hasToolConfig: !!settings.toolConfig,
    hasModelArmorConfig: !!settings.modelArmorConfig,
    hasSpeechConfig: !!settings.generationConfig?.speechConfig,
    hasRoutingConfig: !!settings.generationConfig?.routingConfig,
    hasResponseSchema: !!(
      settings.generationConfig?.responseSchema ||
      settings.generationConfig?.responseJsonSchema
    ),
    hasExtraBody:
      !!settings.extraBody && Object.keys(settings.extraBody).length > 0,
  };
}

// Utility functions for loading from JSON
export function loadGeminiSettings(json: string): GeminiSettings {
  return JSON.parse(json) as GeminiSettings;
}

export function loadGeminiSettingsFromObject(obj: any): GeminiSettings {
  return obj as GeminiSettings;
}

// Type guards for discriminated unions
export function isAutoRoutingMode(
  mode: RoutingConfigMode
): mode is AutoRoutingMode {
  return "modelRoutingPreference" in mode;
}

export function isManualRoutingMode(
  mode: RoutingConfigMode
): mode is ManualRoutingMode {
  return "modelName" in mode;
}

export function isSchemaTypeString(type: SchemaType): type is "STRING" {
  return type === "STRING";
}

export function isSchemaTypeNumber(type: SchemaType): type is "NUMBER" {
  return type === "NUMBER";
}

export function isSchemaTypeArray(type: SchemaType): type is "ARRAY" {
  return type === "ARRAY";
}

export function isSchemaTypeObject(type: SchemaType): type is "OBJECT" {
  return type === "OBJECT";
}
