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
