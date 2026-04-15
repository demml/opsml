/**
 * Google Gemini / Vertex AI Type Definitions
 * Logic: Enums use SCREAMING_SNAKE_CASE; Structs use camelCase.
 */

import type { MessageNum } from "../../../types";

// --- Enums: Core Configuration & Safety ---

export enum SchemaType {
  TYPE_UNSPECIFIED = "TYPE_UNSPECIFIED",
  STRING = "STRING",
  NUMBER = "NUMBER",
  INTEGER = "INTEGER",
  BOOLEAN = "BOOLEAN",
  ARRAY = "ARRAY",
  OBJECT = "OBJECT",
  NULL = "NULL",
}

export enum HarmCategory {
  HARM_CATEGORY_UNSPECIFIED = "HARM_CATEGORY_UNSPECIFIED",
  HARM_CATEGORY_DEROGATORY = "HARM_CATEGORY_DEROGATORY",
  HARM_CATEGORY_TOXICITY = "HARM_CATEGORY_TOXICITY",
  HARM_CATEGORY_VIOLENCE = "HARM_CATEGORY_VIOLENCE",
  HARM_CATEGORY_SEXUAL = "HARM_CATEGORY_SEXUAL",
  HARM_CATEGORY_MEDICAL = "HARM_CATEGORY_MEDICAL",
  HARM_CATEGORY_DANGEROUS = "HARM_CATEGORY_DANGEROUS",
  HARM_CATEGORY_HARASSMENT = "HARM_CATEGORY_HARASSMENT",
  HARM_CATEGORY_HATE_SPEECH = "HARM_CATEGORY_HATE_SPEECH",
  HARM_CATEGORY_SEXUALLY_EXPLICIT = "HARM_CATEGORY_SEXUALLY_EXPLICIT",
  HARM_CATEGORY_DANGEROUS_CONTENT = "HARM_CATEGORY_DANGEROUS_CONTENT",
}

export enum HarmBlockThreshold {
  HARM_BLOCK_THRESHOLD_UNSPECIFIED = "HARM_BLOCK_THRESHOLD_UNSPECIFIED",
  BLOCK_LOW_AND_ABOVE = "BLOCK_LOW_AND_ABOVE",
  BLOCK_MEDIUM_AND_ABOVE = "BLOCK_MEDIUM_AND_ABOVE",
  BLOCK_ONLY_HIGH = "BLOCK_ONLY_HIGH",
  BLOCK_NONE = "BLOCK_NONE",
  OFF = "OFF",
}

export enum HarmBlockMethod {
  HARM_BLOCK_METHOD_UNSPECIFIED = "HARM_BLOCK_METHOD_UNSPECIFIED",
  SEVERITY = "SEVERITY",
  PROBABILITY = "PROBABILITY",
}

export enum Modality {
  MODALITY_UNSPECIFIED = "MODALITY_UNSPECIFIED",
  TEXT = "TEXT",
  IMAGE = "IMAGE",
  AUDIO = "AUDIO",
  VIDEO = "VIDEO",
  DOCUMENT = "DOCUMENT",
}

export enum MediaResolution {
  MEDIA_RESOLUTION_UNSPECIFIED = "MEDIA_RESOLUTION_UNSPECIFIED",
  MEDIA_RESOLUTION_LOW = "MEDIA_RESOLUTION_LOW",
  MEDIA_RESOLUTION_MEDIUM = "MEDIA_RESOLUTION_MEDIUM",
  MEDIA_RESOLUTION_HIGH = "MEDIA_RESOLUTION_HIGH",
}

export enum ModelRoutingPreference {
  UNKNOWN = "UNKNOWN",
  PRIORITIZE_QUALITY = "PRIORITIZE_QUALITY",
  BALANCED = "BALANCED",
  PRIORITIZE_COST = "PRIORITIZE_COST",
}

export enum ThinkingLevel {
  THINKING_LEVEL_UNSPECIFIED = "THINKING_LEVEL_UNSPECIFIED",
  LOW = "LOW",
  HIGH = "HIGH",
}

// --- Structs: Schema & Configuration ---

/**
 * Recursive JSON Schema mapping for tool parameters and structured outputs.
 */
export interface Schema {
  type?: SchemaType;
  format?: string;
  title?: string;
  description?: string;
  nullable?: boolean;
  enum?: string[];
  maxItems?: string;
  minItems?: string;
  properties?: Record<string, Schema>;
  required?: string[];
  minProperties?: string;
  maxProperties?: string;
  minLength?: string;
  maxLength?: string;
  pattern?: string;
  example?: any;
  anyOf?: Schema[];
  propertyOrdering?: string[];
  default?: any;
  items?: Schema; // Maps to Rust's Option<Box<Schema>>
  minimum?: number;
  maximum?: number;
}

export interface SafetySetting {
  category: HarmCategory;
  threshold: HarmBlockThreshold;
}

export interface ThinkingConfig {
  includeThoughts?: boolean;
  thinkingBudget?: number;
  thinkingLevel?: ThinkingLevel;
}

/**
 * Google Gemini / Vertex AI Type Definitions
 * Logic: Precise mapping of untagged enums and flattened structs.
 */

// --- Routing Configuration ---

export interface ImageConfig {
  aspectRatio?: string;
  imageSize?: string;
}

export interface AutoRoutingMode {
  modelRoutingPreference?: ModelRoutingPreference;
}

export interface ManualRoutingMode {
  modelName: string;
}

/**
 * Mirrors Rust: RoutingConfigMode (untagged)
 */
export type RoutingConfigMode = AutoRoutingMode | ManualRoutingMode;

/**
 * Mirrors Rust: RoutingConfig (flattened)
 */
export type RoutingConfig = RoutingConfigMode;

// --- Speech and Voice Configuration ---

export interface PrebuiltVoiceConfig {
  voiceName: string;
}

export interface VoiceConfig {
  prebuiltVoiceConfig: PrebuiltVoiceConfig;
}

export interface SpeakerVoiceConfig {
  speaker: string;
  voiceConfig: VoiceConfig;
}

export interface MultiSpeakerVoiceConfig {
  speakerVoiceConfigs: SpeakerVoiceConfig[];
}

export interface SpeechConfig {
  voiceConfig?: VoiceConfig;
  multiSpeakerVoiceConfig?: MultiSpeakerVoiceConfig;
  languageCode?: string;
}

// --- Generation Configuration ---

export interface GenerationConfig {
  stopSequences?: string[];
  responseMimeType?: string;
  /** Maps to serde_json::Value */
  responseJsonSchema?: Record<string, any>;
  responseModalities?: Modality[];
  candidateCount?: number;
  maxOutputTokens?: number;
  temperature?: number;
  topP?: number;
  topK?: number;
  presencePenalty?: number;
  frequencyPenalty?: number;
  seed?: number;
  responseLogprobs?: boolean;
  logprobs?: number;
  enableEnhancedCivicAnswers?: boolean;
  speechConfig?: SpeechConfig;
  thinkingConfig?: ThinkingConfig;
  imageConfig?: ImageConfig;
  mediaResolution?: MediaResolution;
  audioTimestamp?: boolean;
  enableAffectiveDialog?: boolean;
}

/**
 * Google Gemini / Vertex AI Type Definitions
 * Logic: Model Armor, Tooling, and Function Calling mapping.
 */

// --- Security & Guardrails ---

export interface ModelArmorConfig {
  promptTemplateName?: string;
  responseTemplateName?: string;
}

// --- Tooling & Function Calling Enums ---

export enum Mode {
  MODE_UNSPECIFIED = "MODE_UNSPECIFIED",
  VALIDATED = "VALIDATED",
  ANY = "ANY",
  AUTO = "AUTO",
  NONE = "NONE",
}

export enum Language {
  LANGUAGE_UNSPECIFIED = "LANGUAGE_UNSPECIFIED",
  PYTHON = "PYTHON",
}

export enum Outcome {
  OUTCOME_UNSPECIFIED = "OUTCOME_UNSPECIFIED",
  OUTCOME_OK = "OUTCOME_OK",
  OUTCOME_FAILED = "OUTCOME_FAILED",
  OUTCOME_DEADLINE_EXCEEDED = "OUTCOME_DEADLINE_EXCEEDED",
}

// --- Location & Retrieval ---

export interface LatLng {
  latitude: number;
  longitude: number;
}

export interface RetrievalConfig {
  latLng: LatLng;
  languageCode: string;
}

export interface FunctionCallingConfig {
  mode?: Mode;
  allowedFunctionNames?: string[];
}

export interface ToolConfig {
  functionCallingConfig?: FunctionCallingConfig;
  retrievalConfig?: RetrievalConfig;
}

// --- Main Settings Container ---

export interface GeminiSettings {
  labels?: Record<string, string>;
  toolConfig?: ToolConfig;
  safetySettings?: SafetySetting[]; // SafetySetting defined in Part 1
  generationConfig?: GenerationConfig; // GenerationConfig defined in Part 2
  modelArmorConfig?: ModelArmorConfig;
  extraBody?: Record<string, any>; // Maps to serde_json::Value
  cachedContent?: string;
  tools?: Tool[]; // Tool definition expected in next batch
}

// --- Data & Function Execution ---

export interface FileData {
  mimeType: string;
  fileUri: string;
  displayName?: string;
}

export interface PartialArgs {
  jsonPath: string;
  willContinue?: boolean;
  nullValue?: boolean;
  numberValue?: number;
  stringValue?: string;
  boolValue?: boolean;
}

export interface FunctionCall {
  name: string;
  id?: string;
  /** Maps to serde_json::Map<String, Value> */
  args?: Record<string, any>;
  willContinue?: boolean;
  partialArgs?: PartialArgs[];
}

/**
 * Google Gemini / Vertex AI Type Definitions
 * Logic: Multi-modal Parts, Data Unions, and Search Specifications.
 */

// --- Content Data Structures ---

export interface Blob {
  mimeType: string;
  data: string; // Base64 encoded bytes
  displayName?: string;
}

export interface FunctionResponse {
  name: string;
  response: Record<string, any>;
}

export interface ExecutableCode {
  language: Language;
  code: string;
}

export interface CodeExecutionResult {
  outcome: Outcome;
  output?: string;
}

export interface VideoMetadata {
  startOffset?: string;
  endOffset?: string;
}

/**
 * Mirrors Rust: PartMetadata (flattened map)
 */
export type PartMetadata = Record<string, any>;

// --- Part & Data Union Mapping ---

/**
 * Mirrors Rust: DataNum (Untagged Enum)
 * In JSON, the key (e.g., "text", "inlineData") determines the variant.
 */
export type DataNum =
  | { inlineData: Blob }
  | { fileData: FileData }
  | { functionCall: FunctionCall }
  | { functionResponse: FunctionResponse }
  | { executableCode: ExecutableCode }
  | { codeExecutionResult: CodeExecutionResult }
  | { text: string };

/**
 * Mirrors Rust: Part (Flattened DataNum)
 * Intersection type allows metadata and data to coexist at the top level.
 */
export type Part = {
  thought?: boolean;
  thoughtSignature?: string;
  partMetadata?: PartMetadata;
  mediaResolution?: MediaResolution;
  videoMetadata?: VideoMetadata;
} & DataNum;

export interface GeminiContent {
  role: string; // 'user' or 'model'
  parts: Part[];
}

// --- Tools & Search Specifications ---

export enum Behavior {
  UNSPECIFIED = "UNSPECIFIED",
  BLOCKING = "BLOCKING",
  NON_BLOCKING = "NON_BLOCKING",
}

export interface FunctionDeclaration {
  name: string;
  description: string;
  behavior?: Behavior;
  parameters?: Schema;
  parametersJsonSchema?: Record<string, any>;
  response?: Schema;
  responseJsonSchema?: Record<string, any>;
}

export interface DataStoreSpec {
  dataStore: string;
  filter?: string;
}

export interface VertexAISearch {
  datastore?: string;
  engine?: string;
  maxResults?: number;
  filter?: string;
  dataStoreSpecs?: DataStoreSpec[];
}

/**
 * Google Gemini / Vertex AI Type Definitions
 * Logic: RAG Store, Ranking Configs, and External API Authentication.
 */

// --- Vertex RAG (Retrieval Augmented Generation) ---

export interface RagResource {
  ragCorpus?: string;
  ragFileIds?: string[];
}

export interface Filter {
  metadataFilter?: string;
  vectorDistanceThreshold?: number;
  vectorSimilarityThreshold?: number;
}

export interface RankService {
  modelName?: string;
}

export interface LlmRanker {
  modelName?: string;
}

/**
 * Mirrors Rust: RankingConfig (untagged)
 */
export type RankingConfig = RankService | LlmRanker;

/**
 * Mirrors Rust: Ranking (flattened)
 */
export type Ranking = RankingConfig;

export interface RagRetrievalConfig {
  topK?: number;
  filter?: Filter;
  ranking?: Ranking;
}

export interface VertexRagStore {
  ragResources?: RagResource[];
  ragRetrievalConfig?: RagRetrievalConfig;
  similarityTopK?: number;
  vectorDistanceThreshold?: number;
}

// --- External API Specifications & Auth ---

export enum ApiSpecType {
  API_SPEC_UNSPECIFIED = "API_SPEC_UNSPECIFIED",
  SIMPLE_SEARCH = "SIMPLE_SEARCH",
  ELASTIC_SEARCH = "ELASTIC_SEARCH",
}

export enum AuthType {
  AUTH_TYPE_UNSPECIFIED = "AUTH_TYPE_UNSPECIFIED",
  NO_AUTH = "NO_AUTH",
  API_KEY_AUTH = "API_KEY_AUTH",
  HTTP_BASIC_AUTH = "HTTP_BASIC_AUTH",
  GOOGLE_SERVICE_ACCOUNT_AUTH = "GOOGLE_SERVICE_ACCOUNT_AUTH",
  OAUTH = "OAUTH",
  OIDC_AUTH = "OIDC_AUTH",
}

export enum HttpElementLocation {
  HTTP_IN_UNSPECIFIED = "HTTP_IN_UNSPECIFIED",
  HTTP_IN_QUERY = "HTTP_IN_QUERY",
  HTTP_IN_HEADER = "HTTP_IN_HEADER",
  HTTP_IN_PATH = "HTTP_IN_PATH",
  HTTP_IN_BODY = "HTTP_IN_BODY",
  HTTP_IN_COOKIE = "HTTP_IN_COOKIE",
}

export interface SimpleSearchParams {}

export interface ElasticSearchParams {
  index: string;
  searchTemplate: string;
  numHits?: number;
}

/**
 * Mirrors Rust: ExternalApiParams (untagged)
 */
export type ExternalApiParams = SimpleSearchParams | ElasticSearchParams;

export interface ApiKeyConfig {
  name?: string;
  apiKeySecret?: string;
  apiKeyString?: string;
  httpElementLocation?: HttpElementLocation;
}

/**
 * Google Gemini / Vertex AI Type Definitions
 * Logic: Authentication nesting, Retrieval flattening, and Google Search filters.
 */

// --- Authentication Configurations ---

export interface HttpBasicAuthConfig {
  credentialSecret: string;
}

export interface GoogleServiceAccountConfig {
  serviceAccount?: string;
}

/** * Mirrors Rust: OauthConfigValue (untagged)
 */
export type OauthConfigValue = string; // In Rust, these wrap a single String

/** * Mirrors Rust: OauthConfig (flattened)
 * Note: Since OauthConfigValue is untagged and wraps strings,
 * serialization depends on which variant is picked.
 */
export type OauthConfig = { accessToken: string } | { serviceAccount: string };

/** * Mirrors Rust: OidcConfigValue (untagged)
 */
export type OidcConfig = { idToken: string } | { serviceAccount: string };

/**
 * Mirrors Rust: AuthConfigValue (untagged)
 */
export type AuthConfigValue =
  | ApiKeyConfig
  | HttpBasicAuthConfig
  | GoogleServiceAccountConfig
  | OauthConfig
  | OidcConfig;

export interface AuthConfig {
  authType: AuthType;
  /** Flattened AuthConfigValue */
}

// Resulting Flattened AuthConfig for TS
export type FullAuthConfig = { authType: AuthType } & AuthConfigValue;

// --- External API & Retrieval ---

export interface ExternalApi {
  apiSpec: ApiSpecType;
  endpoint: string;
  authConfig?: FullAuthConfig;
  /** Flattened ExternalApiParams */
}

export type FullExternalApi = ExternalApi & ExternalApiParams;

/**
 * Mirrors Rust: RetrievalSource (untagged)
 */
export type RetrievalSource = VertexAISearch | VertexRagStore | FullExternalApi;

/**
 * Mirrors Rust: Retrieval (flattened)
 */
export type Retrieval = {
  disableAttribution?: boolean;
} & RetrievalSource;

// --- Search & Filtering ---

export interface Interval {
  startTime: string;
  endTime: string;
}

export interface GoogleSearch {
  timeRangeFilter: Interval;
}

export enum PhishBlockThreshold {
  PHISH_BLOCK_THRESHOLD_UNSPECIFIED = "PHISH_BLOCK_THRESHOLD_UNSPECIFIED",
  BLOCK_LOW_AND_ABOVE = "BLOCK_LOW_AND_ABOVE",
  BLOCK_MEDIUM_AND_ABOVE = "BLOCK_MEDIUM_AND_ABOVE",
  BLOCK_HIGH_AND_ABOVE = "BLOCK_HIGH_AND_ABOVE",
  BLOCK_HIGHER_AND_ABOVE = "BLOCK_HIGHER_AND_ABOVE",
  BLOCK_VERY_HIGH_AND_ABOVE = "BLOCK_VERY_HIGH_AND_ABOVE",
  BLOCK_ONLY_EXTREMELY_HIGH = "BLOCK_ONLY_EXTREMELY_HIGH",
}

export interface VertexGoogleSearch {
  excludeDomains?: string[];
  blockingConfidence?: PhishBlockThreshold;
}

/**
 * Google Gemini / Vertex AI Type Definitions
 * Logic: Enterprise Search, Tool definitions, and Computer Use environments.
 */

// --- Search & Grounding ---

export interface EnterpriseWebSearch {
  excludeDomains?: string[];
  blockingConfidence?: PhishBlockThreshold;
}

export interface ParallelAiSearch {
  apiKey?: string;
  /** Maps to serde_json::Map<String, Value> */
  customConfigs?: Record<string, any>;
}

/** * Mirrors Rust: GoogleSearchNum (untagged)
 * Differentiates between standard Gemini and Vertex Search variants.
 */
export type GoogleSearchNum = GoogleSearch | VertexGoogleSearch;

export enum DynamicRetrievalMode {
  MODE_UNSPECIFIED = "MODE_UNSPECIFIED",
  MODE_DYNAMIC = "MODE_DYNAMIC",
}

export interface DynamicRetrievalConfig {
  mode?: DynamicRetrievalMode;
  dynamicThreshold?: number;
}

export interface GoogleSearchRetrieval {
  dynamicRetrievalConfig?: DynamicRetrievalConfig;
}

// --- Extended Capabilities ---

export interface GoogleMaps {
  enableWidget: boolean;
}

export interface CodeExecution {}

export enum ComputerUseEnvironment {
  ENVIRONMENT_UNSPECIFIED = "ENVIRONMENT_UNSPECIFIED",
  ENVIRONMENT_BROWSER = "ENVIRONMENT_BROWSER",
}

export interface ComputerUse {
  environment: ComputerUseEnvironment;
  excludedPredefinedFunctions: string[];
}

export interface UrlContext {}

export interface FileSearch {
  fileSearchStoreNames: string[];
  metadataFilter: string;
  topK: number;
}

// --- Top-Level Tool Container ---

/**
 * Mirrors Rust: Tool (GeminiTool)
 * Logic: A collection of optional capabilities.
 */
export interface Tool {
  functionDeclarations?: FunctionDeclaration[];
  retrieval?: Retrieval;
  googleSearchRetrieval?: GoogleSearchRetrieval;
  codeExecution?: CodeExecution;
  /** * Note: Untagged serialization means the object will
   * match either GoogleSearch or VertexGoogleSearch structure.
   */
  googleSearch?: GoogleSearchNum;
  googleMaps?: GoogleMaps;
  enterpriseWebSearch?: EnterpriseWebSearch;
  parallelAiSearch?: ParallelAiSearch;
  computerUse?: ComputerUse;
  urlContext?: UrlContext;
  fileSearch?: FileSearch;
}

/**
 * Google Gemini / Vertex AI Final Request Mapping
 * Logic: Handles high-level request wrapping with flattened settings.
 */

/**
 * Mirrors Rust: GeminiGenerateContentRequestV1
 * * Logic:
 * 1. 'contents' and 'systemInstruction' use MessageNum (internal IDs).
 * 2. 'settings' is flattened via Intersection Type (&).
 */
export type GeminiGenerateContentRequestV1 = {
  /** Required. The content of the current conversation. */
  contents: MessageNum[];

  /** Optional. Developer-provided instructions to steer model behavior. */
  systemInstruction?: MessageNum;
} & GeminiSettings; // Properties from GeminiSettings are flattened into this object
