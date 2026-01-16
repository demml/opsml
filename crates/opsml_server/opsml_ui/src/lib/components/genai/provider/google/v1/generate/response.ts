import type {
  HarmBlockThreshold,
  HarmCategory,
  GeminiContent,
} from "./request";
/**
 * Maps to 'pub enum TrafficType'
 * Uses SCREAMING_SNAKE_CASE per #[serde(rename_all = "SCREAMING_SNAKE_CASE")]
 */
export type TrafficType =
  | "TRAFFIC_TYPE_UNSPECIFIED"
  | "ON_DEMAND"
  | "PROVISIONED_THROUGHPUT";

/**
 * Maps to 'pub struct ModalityTokenCount'
 * Note: 'Modality' should be defined based on your environment (e.g., TEXT, IMAGE)
 */
export interface ModalityTokenCount {
  modality?: string | null; // Option<Modality>
  tokenCount?: number | null; // Option<i32> mapped to camelCase
}

/**
 * Maps to 'pub struct UsageMetadata'
 */
export interface UsageMetadata {
  promptTokenCount?: number | null;
  candidatesTokenCount?: number | null;
  toolUsePromptTokenCount?: number | null;
  thoughtsTokenCount?: number | null;
  totalTokenCount?: number | null;
  cachedContentTokenCount?: number | null;
  promptTokensDetails?: ModalityTokenCount[] | null;
  cacheTokensDetails?: ModalityTokenCount[] | null;
  candidatesTokensDetails?: ModalityTokenCount[] | null;
  toolUsePromptTokensDetails?: ModalityTokenCount[] | null;
  trafficType?: TrafficType | null;
}
/**
 * Maps to 'pub enum BlockedReason'
 * Casing: SCREAMING_SNAKE_CASE
 */
export type BlockedReason =
  | "BLOCKED_REASON_UNSPECIFIED"
  | "SAFETY"
  | "OTHER"
  | "BLOCKLIST"
  | "MODEL_ARMOR"
  | "PROHIBITED_CONTENT"
  | "IMAGE_SAFETY"
  | "JAILBREAK";

/**
 * Maps to 'pub struct PromptFeedback'
 * Casing: camelCase
 */
export interface PromptFeedback {
  blockReason?: BlockedReason; // Option<T> + skip_serializing_if
  safetyRatings?: SafetyRating[];
  blockReasonMessage?: string;
}

/**
 * Maps to 'pub enum UrlRetrievalStatus'
 * Casing: SCREAMING_SNAKE_CASE
 */
export type UrlRetrievalStatus =
  | "URL_RETRIEVAL_STATUS_UNSPECIFIED"
  | "URL_RETRIEVAL_STATUS_SUCCESS"
  | "URL_RETRIEVAL_STATUS_ERROR";

/**
 * Maps to 'pub struct UrlMetadata'
 */
export interface UrlMetadata {
  retrievedUrl?: string;
  urlRetrievalStatus?: UrlRetrievalStatus;
}

/**
 * Maps to 'pub struct UrlContextMetadata'
 */
export interface UrlContextMetadata {
  urlMetadata?: UrlMetadata[];
}

/**
 * Maps to 'pub struct SourceFlaggingUri'
 */
export interface SourceFlaggingUri {
  sourceId: string;
  flagContentUri: string;
}

/**
 * Maps to 'pub struct RetrievalMetadata'
 */
export interface RetrievalMetadata {
  googleSearchDynamicRetrievalScore?: number; // f64
}

/**
 * Maps to 'pub struct SearchEntryPoint'
 */
export interface SearchEntryPoint {
  renderedContent?: string;
  sdkBlob?: string;
}

/**
 * Maps to 'pub struct Segment'
 */
export interface Segment {
  partIndex?: number; // i32
  startIndex?: number;
  endIndex?: number;
  text?: string;
}

/**
 * Maps to 'pub struct GroundingSupport'
 */
export interface GroundingSupport {
  groundingChunkIndices?: number[];
  confidenceScores?: number[]; // f32
  segment?: Segment;
}

/**
 * Maps to 'pub struct Web'
 */
export interface Web {
  uri?: string;
  title?: string;
  domain?: string;
}

/**
 * Maps to 'pub struct PageSpan'
 */
export interface PageSpan {
  firstPage: number;
  lastPage: number;
}

/**
 * Maps to 'pub struct RagChunk'
 */
export interface RagChunk {
  text: string;
  pageSpan?: PageSpan;
}

/**
 * Maps to 'pub struct RetrievedContext'
 */
export interface RetrievedContext {
  uri?: string;
  title?: string;
  text?: string;
  ragChunk?: RagChunk;
}

/**
 * Maps to 'pub struct Maps'
 */
export interface Maps {
  uri?: string;
  title?: string;
  text?: string;
  placeId?: string;
}

/**
 * Maps to 'pub enum GroundingChunkType'
 * Attribute: #[serde(untagged)]
 */
export type GroundingChunkType = Web | RetrievedContext | Maps;

/**
 * Maps to 'pub struct GroundingChunk'
 * Attribute: #[serde(flatten)]
 */
export type GroundingChunk = GroundingChunkType;

/**
 * Maps to 'pub struct GroundingMetadata'
 */
export interface GroundingMetadata {
  webSearchQueries?: string[];
  groundingChunks?: GroundingChunk[];
  groundingSupports?: GroundingSupport[];
  searchEntryPoint?: SearchEntryPoint;
  retrievalMetadata?: RetrievalMetadata;
  sourceFlaggingUris?: SourceFlaggingUri[];
  googleMapsWidgetContextToken?: string;
}

/**
 * Maps to 'pub enum HarmProbability'
 */
export type HarmProbability =
  | "HARM_PROBABILITY_UNSPECIFIED"
  | "NEGLIGIBLE"
  | "LOW"
  | "MEDIUM"
  | "HIGH";

/**
 * Maps to 'pub enum HarmSeverity'
 */
export type HarmSeverity =
  | "HARM_SEVERITY_UNSPECIFIED"
  | "HARM_SEVERITY_NEGLIGIBLE"
  | "HARM_SEVERITY_LOW"
  | "HARM_SEVERITY_MEDIUM"
  | "HARM_SEVERITY_HIGH";

/**
 * Maps to 'pub struct SafetyRating'
 */
export interface SafetyRating {
  category: HarmCategory; // Assuming HarmCategory is defined elsewhere
  probability: HarmProbability | null;
  probabilityScore?: number;
  severity: HarmSeverity | null;
  severityScore?: number;
  blocked?: boolean;
  overwrittenThreshold?: HarmBlockThreshold; // Assuming HarmBlockThreshold is defined
}

/**
 * Maps to 'pub enum FinishReason'
 * Casing: SCREAMING_SNAKE_CASE per #[serde(rename_all = "SCREAMING_SNAKE_CASE")]
 */
export type FinishReason =
  | "FINISH_REASON_UNSPECIFIED"
  | "STOP"
  | "MAX_TOKENS"
  | "SAFETY"
  | "RECITATION"
  | "OTHER"
  | "BLOCKLIST"
  | "PROHIBITED_CONTENT"
  | "SPII"
  | "MALFORMED_FUNCTION_CALL"
  | "MODEL_ARMOR"
  | "IMAGE_SAFETY"
  | "IMAGE_PROHIBITED_CONTENT"
  | "IMAGE_RECITATION"
  | "IMAGE_OTHER"
  | "UNEXPECTED_TOOL_CALL"
  | "NO_IMAGE";

/**
 * Maps to 'pub struct LogprobsCandidate'
 */
export interface LogprobsCandidate {
  token: string | null;
  tokenId: number | null; // i32
  logProbability: number | null; // f64
}

/**
 * Maps to 'pub struct TopCandidates'
 */
export interface TopCandidates {
  candidates: LogprobsCandidate[] | null;
}

/**
 * Maps to 'pub struct LogprobsResult'
 */
export interface LogprobsResult {
  topCandidates: TopCandidates[] | null;
  chosenCandidates: LogprobsCandidate[] | null;
}

/**
 * Maps to 'pub struct GoogleDate'
 */
export interface GoogleDate {
  year: number | null;
  month: number | null;
  day: number | null;
}

/**
 * Maps to 'pub struct Citation'
 */
export interface Citation {
  startIndex?: number | null;
  endIndex?: number | null;
  uri?: string | null;
  title?: string | null;
  license?: string | null;
  publicationDate?: GoogleDate | null;
}

/**
 * Maps to 'pub struct CitationMetadata'
 */
export interface CitationMetadata {
  citations?: Citation[] | null;
}

/**
 * Maps to 'pub struct Candidate'
 * This is the primary unit of a Gemini response.
 */
export interface Candidate {
  index?: number | null;
  content: GeminiContent; // Assuming GeminiContent is defined in your project
  avgLogprobs?: number | null;
  logprobsResult?: LogprobsResult | null;
  finishReason?: FinishReason | null;
  safetyRatings?: SafetyRating[] | null;
  citationMetadata?: CitationMetadata | null;
  groundingMetadata?: GroundingMetadata | null;
  urlContextMetadata?: UrlContextMetadata | null;
  finishMessage?: string | null;
}

/**
 * Maps to 'pub struct GenerateContentResponse'
 * The root response object for Gemini/Vertex AI Content Generation.
 * Casing: camelCase per #[serde(rename_all = "camelCase")]
 */
export interface GenerateContentResponse {
  candidates: Candidate[];

  modelVersion?: string | null;

  createTime?: string | null; // ISO-8601 String

  responseId?: string | null;

  promptFeedback?: PromptFeedback | null;

  usageMetadata?: UsageMetadata | null;
}
