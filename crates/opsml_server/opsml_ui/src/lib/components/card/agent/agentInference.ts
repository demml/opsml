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

  /** Protocol (http, https, ws, wss, grpc) */
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
 * Standard A2A protocol endpoints based on protocol binding
 */
const A2A_ENDPOINTS = {
  http: {
    invoke: "/v1/agent/invoke",
    tasks: "/v1/agent/tasks",
    stream: "/v1/agent/stream",
    health: "/health",
  },
  grpc: {
    invoke: "agent.v1.AgentService/Invoke",
    tasks: "agent.v1.AgentService/GetTask",
    stream: "agent.v1.AgentService/InvokeStream",
  },
  websocket: {
    connect: "/v1/agent/ws",
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
 * Map modality strings to MIME types
 */
function modalityToContentType(modality: string): string[] {
  const mapping: Record<string, string[]> = {
    text: ["text/plain", "application/json"],
    json: ["application/json"],
    image: ["image/png", "image/jpeg", "image/webp", "image/gif"],
    audio: ["audio/mpeg", "audio/wav", "audio/ogg"],
    video: ["video/mp4", "video/webm"],
    binary: ["application/octet-stream"],
  };

  return mapping[modality.toLowerCase()] || ["application/json"];
}

/**
 * Infer endpoints from an agent interface and skill
 */
function inferEndpointsForSkill(
  agentInterface: AgentInterface,
  skill: AgentSkill,
  capabilities: AgentSpec["capabilities"],
): InferredEndpoint[] {
  const endpoints: InferredEndpoint[] = [];
  const protocol = agentInterface.protocolBinding.toLowerCase();
  const baseUrl = agentInterface.url;

  // Determine input/output content types from modes
  const inputModes = skill.inputModes || [];
  const outputModes = skill.outputModes || [];

  const requestContentTypes = inputModes.flatMap(modalityToContentType);
  const responseContentTypes = outputModes.flatMap(modalityToContentType);

  // Standard invocation endpoint (JSON-RPC 2.0 for A2A)
  if (protocol === "http" || protocol === "https") {
    endpoints.push({
      method: "POST",
      path: baseUrl, // A2A uses base URL for JSON-RPC
      protocol,
      requestContentTypes: ["application/json"],
      responseContentTypes: ["application/json"],
      streaming: false,
      description: `Invoke ${skill.name} skill`,
      examples: skill.examples,
    });

    // Streaming endpoint if supported
    if (capabilities.streaming && outputModes.includes("text")) {
      endpoints.push({
        method: "POST",
        path: `${baseUrl}${A2A_ENDPOINTS.http.stream}`,
        protocol,
        requestContentTypes:
          requestContentTypes.length > 0
            ? requestContentTypes
            : ["application/json"],
        responseContentTypes: ["text/event-stream", "application/x-ndjson"],
        streaming: true,
        description: `Stream ${skill.name} skill responses`,
        examples: skill.examples,
      });
    }

    // Task status endpoint for async operations
    endpoints.push({
      method: "GET",
      path: `${baseUrl}${A2A_ENDPOINTS.http.tasks}/{taskId}`,
      protocol,
      requestContentTypes: [],
      responseContentTypes: ["application/json"],
      streaming: false,
      description: `Get status of async ${skill.name} task`,
    });
  } else if (protocol === "grpc") {
    endpoints.push({
      method: "POST",
      path: `${baseUrl}/${A2A_ENDPOINTS.grpc.invoke}`,
      protocol,
      requestContentTypes: ["application/grpc+proto"],
      responseContentTypes: ["application/grpc+proto"],
      streaming: false,
      description: `Invoke ${skill.name} skill via gRPC`,
      examples: skill.examples,
    });

    if (capabilities.streaming) {
      endpoints.push({
        method: "POST",
        path: `${baseUrl}/${A2A_ENDPOINTS.grpc.stream}`,
        protocol,
        requestContentTypes: ["application/grpc+proto"],
        responseContentTypes: ["application/grpc+proto"],
        streaming: true,
        description: `Stream ${skill.name} skill responses via gRPC`,
        examples: skill.examples,
      });
    }
  } else if (
    protocol === "websocket" ||
    protocol === "ws" ||
    protocol === "wss"
  ) {
    endpoints.push({
      method: "GET",
      path: `${baseUrl}${A2A_ENDPOINTS.websocket.connect}`,
      protocol,
      requestContentTypes: ["application/json"],
      responseContentTypes: ["application/json"],
      streaming: true,
      description: `Connect to ${skill.name} skill via WebSocket`,
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
 * Infer complete agent contract from AgentSpec
 */
export function inferAgentContract(spec: AgentSpec): AgentContract {
  const skills: AgentSkillContract[] = [];

  // Process each skill and infer its contract
  for (const skillFormat of spec.skills) {
    const skill = extractA2ASkill(skillFormat);
    if (!skill) continue; // Skip non-A2A skills for now

    const inputModes = (skill.inputModes ||
      spec.defaultInputModes) as Modality[];
    const outputModes = (skill.outputModes ||
      spec.defaultOutputModes) as Modality[];

    // Infer endpoints for each supported interface
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
