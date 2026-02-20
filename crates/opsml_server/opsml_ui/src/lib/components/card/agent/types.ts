export interface AgentExtension {
  description?: string;
  params?: Record<string, unknown>; // Value in Rust -> arbitrary JSON object
  required: boolean;
  uri: string;
}

export interface AgentCapabilities {
  streaming: boolean;
  pushNotifications: boolean;
  extendedAgentCard: boolean;
  extensions: AgentExtension[];
}

export interface AgentProvider {
  organization: string;
  url: string;
}

export interface SecurityRequirement {
  schemes: string[];
}

// OAuth Flow Types
export interface AuthorizationCodeFlow {
  authorizationUrl: string;
  pkceRequired: boolean;
  refreshUrl: string;
  scopes: Record<string, string>;
  tokenUrl: string;
}

export interface ClientCredentialsFlow {
  refreshUrl: string;
  scopes: Record<string, string>;
  tokenUrl: string;
}

export interface DeviceCodeFlow {
  deviceAuthorizationUrl: string;
  refreshUrl: string;
  scopes: Record<string, string>;
  tokenUrl: string;
}

export interface ImplicitAuthFlow {
  authorizationUrl: string;
  refreshUrl: string;
  scopes: Record<string, string>;
}

export interface PassWordAuthFlow {
  refreshUrl: string;
  scopes: Record<string, string>;
  tokenUrl: string;
}

export interface OAuthFlows {
  authorizationCode?: AuthorizationCodeFlow;
  clientCredentials?: ClientCredentialsFlow;
  deviceCode?: DeviceCodeFlow;
  implicit?: ImplicitAuthFlow;
  password?: PassWordAuthFlow;
}

// Security Scheme Variants
export interface ApiKeySecurityScheme {
  description?: string;
  location: string;
  name: string;
}

export interface HttpAuthSecurityScheme {
  scheme: string;
  bearerFormat: string;
  description: string;
}

export interface MtlsSecurityScheme {
  description: string;
}

export interface Oauth2SecurityScheme {
  description?: string;
  flows: OAuthFlows;
  oauth2MetadataUrl?: string;
}

export interface OpenIdConnectSecurityScheme {
  description?: string;
  openIdConnectUrl?: string;
}

export type SecurityScheme =
  | ApiKeySecurityScheme
  | HttpAuthSecurityScheme
  | MtlsSecurityScheme
  | Oauth2SecurityScheme
  | OpenIdConnectSecurityScheme;

export interface AgentCardSignature {
  header?: Record<string, string>;
  protected: string;
  signature: string;
}

export interface AgentInterface {
  url: string;
  protocolBinding: string;
  protocolVersion: string;
  tenant: string;
}

export interface AgentSkillStandard {
  name: string;
  description: string;
  license?: string;
  compatibility?: string;
  metadata?: Record<string, string>;
  allowedTools?: string[];
  skillsPath?: string;
  body?: string;
}

export interface AgentSkill {
  description: string;
  examples: string[];
  id: string;
  inputModes?: string[];
  name: string;
  outputModes?: string[];
  securityRequirements?: SecurityRequirement[];
  tags: string[];
}

export type SkillFormat =
  | (AgentSkillStandard & { format: "standard" })
  | (AgentSkill & { format: "a2a" });

export interface AgentSpec {
  capabilities: AgentCapabilities;
  defaultOutputModes: string[];
  defaultInputModes: string[];
  description: string;
  documentationUrl?: string;
  iconUrl?: string;
  name: string;
  provider?: AgentProvider;
  securityRequirements?: SecurityRequirement[];
  securitySchemes?: Record<string, SecurityScheme>;
  signatures?: AgentCardSignature[];
  skills: SkillFormat[];
  supportedInterfaces: AgentInterface[];
  version: string;
}

// A2A Response Types
export interface A2APart {
  kind: "text" | "image" | "audio" | "video" | "file" | string;
  text?: string;
  data?: string;
  mimeType?: string;
  url?: string;
  metadata?: Record<string, unknown>;
}

export interface A2AArtifact {
  artifactId: string;
  parts: A2APart[];
  metadata?: Record<string, unknown>;
}

export interface A2AMessage {
  contextId?: string;
  kind: "message";
  messageId: string;
  parts: A2APart[];
  role: "user" | "agent" | "system";
  taskId?: string;
  timestamp?: string;
}

export interface A2ATaskStatus {
  state: "pending" | "in_progress" | "completed" | "failed" | "cancelled";
  message?: string;
  timestamp?: string;
}

export interface A2ATask {
  artifacts?: A2AArtifact[];
  contextId?: string;
  history?: A2AMessage[];
  id: string;
  metadata?: Record<string, unknown>;
  status?: A2ATaskStatus;
  kind?: "task";
}

export interface A2AResponse {
  result: A2ATask | string | Record<string, unknown>;
  status: "success" | "failed";
  error?: {
    message: string;
    code?: string;
  };
}

// Type guard functions
export function isA2ATask(result: unknown): result is A2ATask {
  return (
    typeof result === "object" &&
    result !== null &&
    "id" in result &&
    typeof (result as any).id === "string"
  );
}

export function isA2AResponse(response: unknown): response is A2AResponse {
  return (
    typeof response === "object" &&
    response !== null &&
    "result" in response &&
    "status" in response
  );
}

export function extractTextFromA2ATask(task: A2ATask): string {
  const textParts: string[] = [];

  // Extract from artifacts
  if (task.artifacts && Array.isArray(task.artifacts)) {
    for (const artifact of task.artifacts) {
      if (Array.isArray(artifact.parts)) {
        const artifactTexts = artifact.parts
          .filter((part) => part.kind === "text" && part.text)
          .map((part) => part.text!);
        textParts.push(...artifactTexts);
      }
    }
  }

  // If no artifacts, try extracting from history (last agent message)
  if (textParts.length === 0 && task.history && Array.isArray(task.history)) {
    const lastAgentMessage = [...task.history]
      .reverse()
      .find((msg) => msg.role === "agent");

    if (lastAgentMessage && Array.isArray(lastAgentMessage.parts)) {
      const messageTexts = lastAgentMessage.parts
        .filter((part) => part.kind === "text" && part.text)
        .map((part) => part.text!);
      textParts.push(...messageTexts);
    }
  }

  return textParts.join("\n\n");
}

export interface DebugPayload {
  messageId?: string;
  request?: unknown;
  response?: unknown;
  timestamp: Date;
}

export interface DebugMessage {
  index: number;
  messageId?: string;
  role: "user" | "agent" | "system";
  content: string;
  skillName?: string;
  timestamp: Date;
  debugPayload: DebugPayload;
}

export type MessageRole = "user" | "agent" | "system";

export interface ChatMessage {
  role: MessageRole;
  content: string; // Clean display content
  timestamp: Date;
  skillName?: string;
  messageId?: string;
  debugPayload?: DebugPayload; // Full request/response for debugging
}
