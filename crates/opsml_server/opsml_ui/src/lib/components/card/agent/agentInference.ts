/**
 * Agent Route and Contract Inference
 *
 * Automatically infers API routes, request/response contracts, and interaction patterns
 * from AgentSpec based on the A2A (Agent-to-Agent) protocol specification.
 */

import type { DeploymentConfig } from "../card_interfaces/servicecard";
import type {
  AgentSpec,
  AgentInterface,
  AgentSkill,
  SkillFormat,
  SecurityScheme,
} from "./types";

/**
 * Supported input/output modalities
 */
export type Modality = "text" | "image" | "audio" | "video" | "json" | "binary";

/**
 * Inferred endpoint for agent interaction
 */
export interface InferredEndpoint {
  /** HTTP method (GET, POST, etc.) */
  method: "GET" | "POST" | "PUT" | "DELETE" | "PATCH";

  /** Full URL path */
  path: string;

  /** Protocol binding identifier (jsonrpc, http+json, grpc, websocket) */
  protocol: string;

  /** Supported request content types */
  requestContentTypes: string[];

  /** Supported response content types */
  responseContentTypes: string[];

  /** Whether this endpoint supports streaming */
  streaming: boolean;

  /** Description of what this endpoint does */
  description: string;

  /** Example request payloads */
  examples?: unknown[];
}

/**
 * Complete contract for interacting with an agent skill
 */
export interface AgentSkillContract {
  /** Skill identifier */
  skillId: string;

  /** Skill name (human-readable) */
  name: string;

  /** Description of what the skill does */
  description: string;

  /** Inferred endpoints for this skill */
  endpoints: InferredEndpoint[];

  /** Input modalities supported */
  inputModes: Modality[];

  /** Output modalities returned */
  outputModes: Modality[];

  /** Required authentication schemes */
  requiredAuth: string[];

  /** Example inputs for testing */
  examples: string[];

  /** Tags for categorization */
  tags: string[];
}

/**
 * Complete agent interaction contract
 */
export interface AgentContract {
  /** Base URLs for different interfaces */
  interfaces: AgentInterface[];

  /** Contracts for each skill the agent supports */
  skills: AgentSkillContract[];

  /** Global capabilities */
  capabilities: {
    streaming: boolean;
    pushNotifications: boolean;
    extendedAgentCard: boolean;
  };

  /** Security configuration */
  security: {
    schemes: Record<string, SecurityScheme>;
    requirements: string[][];
  };

  /** Default input/output modes if not skill-specific */
  defaultInputModes: Modality[];
  defaultOutputModes: Modality[];
}

/**
 * Standard A2A protocol endpoint paths per spec section 5.3 (Method Mapping Reference)
 * and section 11.3 (HTTP+JSON/REST URL Patterns).
 */
const A2A_ENDPOINTS = {
  // HTTP+JSON/REST binding (Section 11.3)
  httpJson: {
    send: "/message:send",
    stream: "/message:stream",
    getTask: "/tasks",
    health: "/health",
  },
  // JSON-RPC 2.0 binding (Section 9) — single base URL, method name differentiates
  jsonrpc: {
    sendMethod: "SendMessage",
    streamMethod: "SendStreamingMessage",
    getTaskMethod: "GetTask",
  },
  // gRPC binding (Section 10)
  grpc: {
    send: "AgentService/SendMessage",
    stream: "AgentService/SendStreamingMessage",
    getTask: "AgentService/GetTask",
  },
};

export function inferHealthEndpoint(config: DeploymentConfig[]): string[] {
  // build health endpoint based on deployment config, default to /health if not specified
  // iterate through config, get url and healthcheck path, return first valid healthcheck url
  let healthcheckUrls: string[] = [];
  for (const deploy of config) {
    if (deploy.healthcheck) {
      // combine url and healthcheck path, handle trailing slashes
      let baseUrl = deploy.urls[0]; // use first url for healthcheck
      if (baseUrl.endsWith("/")) {
        baseUrl = baseUrl.slice(0, -1);
      }
      let healthcheckPath = deploy.healthcheck.startsWith("/")
        ? deploy.healthcheck
        : `/${deploy.healthcheck}`;
      healthcheckUrls.push(`${baseUrl}${healthcheckPath}`);
    }
  }
  return healthcheckUrls;
}

/**
 * Normalise a protocolBinding string to a canonical key.
 * The spec defines open-form strings; common values are "JSONRPC", "HTTP+JSON", "GRPC".
 */
function normaliseBinding(
  binding: string,
): "jsonrpc" | "http+json" | "grpc" | "websocket" | "unknown" {
  const b = binding.toLowerCase();
  if (b === "jsonrpc" || b === "json-rpc" || b === "json_rpc") return "jsonrpc";
  if (b === "http+json" || b === "http" || b === "https" || b === "rest")
    return "http+json";
  if (b === "grpc" || b === "grpc+proto") return "grpc";
  if (b === "websocket" || b === "ws" || b === "wss") return "websocket";
  return "unknown";
}

/**
 * Strip a trailing slash from a URL.
 */
function trimTrailingSlash(url: string): string {
  return url.endsWith("/") ? url.slice(0, -1) : url;
}

/**
 * Infer endpoints from an agent interface.
 * Per the A2A spec (Section 5.3), ALL skills share the same message endpoints:
 *   HTTP+JSON: POST /message:send  |  POST /message:stream
 *   JSON-RPC:  POST <baseUrl>  (method distinguished by JSON-RPC method name)
 *   gRPC:      AgentService/SendMessage  |  AgentService/SendStreamingMessage
 */
function inferEndpointsForSkill(
  agentInterface: AgentInterface,
  skill: AgentSkill,
  capabilities: AgentSpec["capabilities"],
): InferredEndpoint[] {
  const endpoints: InferredEndpoint[] = [];
  const binding = normaliseBinding(agentInterface.protocolBinding);
  const baseUrl = trimTrailingSlash(agentInterface.url);

  if (binding === "jsonrpc") {
    // JSON-RPC 2.0 — single URL, method name in the body
    endpoints.push({
      method: "POST",
      path: baseUrl,
      protocol: "jsonrpc",
      requestContentTypes: ["application/json"],
      responseContentTypes: ["application/json"],
      streaming: false,
      description: `Send message to ${skill.name} (JSON-RPC SendMessage)`,
      examples: skill.examples,
    });
    if (capabilities.streaming) {
      endpoints.push({
        method: "POST",
        path: baseUrl,
        protocol: "jsonrpc",
        requestContentTypes: ["application/json"],
        responseContentTypes: ["text/event-stream"],
        streaming: true,
        description: `Stream messages to ${skill.name} (JSON-RPC SendStreamingMessage)`,
        examples: skill.examples,
      });
    }
  } else if (binding === "http+json" || binding === "unknown") {
    // HTTP+JSON/REST — standardised subpaths per Section 11.3.1
    endpoints.push({
      method: "POST",
      path: `${baseUrl}${A2A_ENDPOINTS.httpJson.send}`,
      protocol: "http+json",
      requestContentTypes: ["application/json"],
      responseContentTypes: ["application/json"],
      streaming: false,
      description: `Send message to ${skill.name} (POST /message:send)`,
      examples: skill.examples,
    });
    if (capabilities.streaming) {
      endpoints.push({
        method: "POST",
        path: `${baseUrl}${A2A_ENDPOINTS.httpJson.stream}`,
        protocol: "http+json",
        requestContentTypes: ["application/json"],
        responseContentTypes: ["text/event-stream"],
        streaming: true,
        description: `Stream messages to ${skill.name} (POST /message:stream)`,
        examples: skill.examples,
      });
    }
  } else if (binding === "grpc") {
    endpoints.push({
      method: "POST",
      path: `${baseUrl}/${A2A_ENDPOINTS.grpc.send}`,
      protocol: "grpc",
      requestContentTypes: ["application/grpc+proto"],
      responseContentTypes: ["application/grpc+proto"],
      streaming: false,
      description: `Send message to ${skill.name} via gRPC`,
      examples: skill.examples,
    });
    if (capabilities.streaming) {
      endpoints.push({
        method: "POST",
        path: `${baseUrl}/${A2A_ENDPOINTS.grpc.stream}`,
        protocol: "grpc",
        requestContentTypes: ["application/grpc+proto"],
        responseContentTypes: ["application/grpc+proto"],
        streaming: true,
        description: `Stream messages to ${skill.name} via gRPC`,
        examples: skill.examples,
      });
    }
  } else if (binding === "websocket") {
    endpoints.push({
      method: "GET",
      path: baseUrl,
      protocol: "websocket",
      requestContentTypes: ["application/json"],
      responseContentTypes: ["application/json"],
      streaming: true,
      description: `Connect to ${skill.name} via WebSocket`,
      examples: skill.examples,
    });
  }

  return endpoints;
}

/**
 * Extract A2A skill from SkillFormat union type
 */
function extractA2ASkill(skillFormat: SkillFormat): AgentSkill | null {
  if (skillFormat.format === "a2a") {
    return skillFormat;
  }
  return null;
}

/**
 * Infer complete agent contract from AgentSpec.
 * By the time AgentSpec reaches the frontend, supportedInterfaces URLs are already
 * populated by the Rust backend (from deploy config if needed).
 */
export function inferAgentContract(spec: AgentSpec): AgentContract {
  const skills: AgentSkillContract[] = [];

  for (const skillFormat of spec.skills) {
    const skill = extractA2ASkill(skillFormat);
    if (!skill) continue;

    const inputModes = (skill.inputModes ||
      spec.defaultInputModes) as Modality[];
    const outputModes = (skill.outputModes ||
      spec.defaultOutputModes) as Modality[];

    const endpoints: InferredEndpoint[] = [];
    for (const iface of spec.supportedInterfaces) {
      endpoints.push(
        ...inferEndpointsForSkill(iface, skill, spec.capabilities),
      );
    }

    // Extract required auth schemes for this skill
    const requiredAuth =
      skill.securityRequirements?.flatMap((req) => req.schemes) || [];

    skills.push({
      skillId: skill.id,
      name: skill.name,
      description: skill.description,
      endpoints,
      inputModes,
      outputModes,
      requiredAuth,
      examples: skill.examples,
      tags: skill.tags,
    });
  }

  // Extract global security requirements
  const globalRequiredAuth =
    spec.securityRequirements?.map((req) => req.schemes) || [];

  return {
    interfaces: spec.supportedInterfaces,
    skills,
    capabilities: {
      streaming: spec.capabilities.streaming,
      pushNotifications: spec.capabilities.pushNotifications,
      extendedAgentCard: spec.capabilities.extendedAgentCard,
    },
    security: {
      schemes: spec.securitySchemes || {},
      requirements: globalRequiredAuth,
    },
    defaultInputModes: spec.defaultInputModes as Modality[],
    defaultOutputModes: spec.defaultOutputModes as Modality[],
  };
}

/**
 * Build headers with authentication
 */
export function buildAuthHeaders(
  securitySchemes: Record<string, SecurityScheme>,
  authConfig: Record<string, string>,
): Record<string, string> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };

  for (const [schemeName, scheme] of Object.entries(securitySchemes)) {
    const authValue = authConfig[schemeName];
    if (!authValue) continue;

    // API Key
    if ("location" in scheme && "name" in scheme) {
      if (scheme.location === "header") {
        headers[scheme.name] = authValue;
      }
    }

    // HTTP Bearer Auth
    if ("scheme" in scheme && scheme.scheme === "bearer") {
      headers["Authorization"] = `Bearer ${authValue}`;
    }

    // Basic Auth
    if ("scheme" in scheme && scheme.scheme === "basic") {
      headers["Authorization"] = `Basic ${authValue}`;
    }
  }

  return headers;
}

/**
 * Format examples for UI display
 */
export function formatExamplesForDisplay(
  examples: string[],
): Array<{ label: string; value: string }> {
  return examples.map((example, idx) => ({
    label: `Example ${idx + 1}`,
    value: example,
  }));
}
