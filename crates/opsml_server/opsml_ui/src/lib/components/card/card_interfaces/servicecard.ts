import type { RegistryType } from "$lib/utils";

export interface Card {
  name: string;
  space: string;
  version: string;
  uid: string;
  registry_type: string;
  alias: string;
}

export interface CardList {
  cards: Card[];
}

export enum ServiceType {
  Api = "Api",
  Mcp = "Mcp",
  Agent = "Agent",
}

export enum McpCapability {
  Resources = "Resources",
  Tools = "Tools",
  Prompts = "Prompts",
}

export enum McpTransport {
  Http = "Http",
  Stdio = "Stdio",
}

export interface McpConfig {
  capabilities: McpCapability[];
  transport: McpTransport;
}

export interface GpuConfig {
  type: string; // corresponds to gpu_type in Rust
  count: number;
  memory: string;
}

export interface Resources {
  cpu: number;
  memory: string;
  storage: string;
  gpu?: GpuConfig;
}

export interface DeploymentConfig {
  environment: string;
  provider?: string;
  location?: string[];
  endpoints: string[];
  resources?: Resources;
  links?: Record<string, string>;
}

export interface ServiceMetadata {
  description: string;
  language?: string;
  tags: string[];
}

export interface ServiceConfig {
  version?: string;
  cards?: Card[];
  write_dir?: string;
  mcp?: McpConfig;
}

export interface ServiceCard {
  name: string;
  space: string;
  version: string;
  uid: string;
  created_at: string; // ISO datetime string
  cards: CardList;
  opsml_version: string;
  app_env: string;
  is_card: boolean;
  registry_type: RegistryType;
  experimentcard_uid?: string;
  service_type: ServiceType;
  metadata?: ServiceMetadata;
  deploy?: DeploymentConfig[];
  service_config: ServiceConfig;
  tags: string[];
}
