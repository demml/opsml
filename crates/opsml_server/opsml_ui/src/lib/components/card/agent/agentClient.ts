/**
 * Agent Client for A2A Protocol
 *
 * Provides a type-safe client for interacting with agents based on inferred contracts.
 */

import type {
  AgentContract,
  AgentSkillContract,
  InferredEndpoint,
  A2ARequest,
  A2AResponse,
} from "./agentInference";
import { buildAuthHeaders } from "./agentInference";

export interface AgentClientConfig {
  /** Authentication tokens/keys for each security scheme */
  authConfig: Record<string, string>;

  /** Request timeout in milliseconds */
  timeout?: number;

  /** Custom headers to include in all requests */
  customHeaders?: Record<string, string>;

  /** Tenant ID for multi-tenancy */
  tenant?: string;
}

export interface InvokeSkillOptions {
  /** Skill to invoke */
  skill: AgentSkillContract;

  /** Task description or prompt */
  task: string;

  /** Input data (text, image URL, etc.) */
  input?: unknown;

  /** Additional context */
  context?: Record<string, unknown>;

  /** Whether to stream the response */
  stream?: boolean;

  /** Abort signal for cancellation */
  signal?: AbortSignal;
}

export interface StreamChunk {
  /** Chunk data */
  data: string;

  /** Whether this is the final chunk */
  done: boolean;

  /** Metadata about the chunk */
  metadata?: Record<string, unknown>;
}

/**
 * Agent client for executing skills based on inferred contracts
 */
export class AgentClient {
  private contract: AgentContract;
  private config: AgentClientConfig;

  constructor(contract: AgentContract, config: AgentClientConfig) {
    this.contract = contract;
    this.config = {
      timeout: 30000,
      ...config,
    };
  }

  /**
   * Select the best endpoint for a skill based on capabilities
   */
  private selectEndpoint(
    skill: AgentSkillContract,
    streaming: boolean,
  ): InferredEndpoint | null {
    if (streaming) {
      return skill.endpoints.find((e) => e.streaming) || null;
    }
    return skill.endpoints.find((e) => !e.streaming) || null;
  }

  /**
   * Build complete headers with auth and custom headers
   */
  private buildHeaders(): Record<string, string> {
    const authHeaders = buildAuthHeaders(
      this.contract.security.schemes,
      this.config.authConfig,
    );

    return {
      ...authHeaders,
      ...this.config.customHeaders,
    };
  }

  /**
   * Invoke a skill and get a response
   */
  async invokeSkill(options: InvokeSkillOptions): Promise<A2AResponse> {
    const { skill, task, input, context, signal } = options;
    const stream = options.stream || false;

    const endpoint = this.selectEndpoint(skill, stream);
    if (!endpoint) {
      throw new Error(`No suitable endpoint found for skill: ${skill.name}`);
    }

    // Build request payload
    const payload: A2ARequest = {
      skillId: skill.skillId,
      task,
      input,
      context,
      stream,
      tenant: this.config.tenant,
    };

    // Make fetch request
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.config.timeout);

    try {
      const response = await fetch(endpoint.path, {
        method: endpoint.method,
        headers: this.buildHeaders(),
        body: JSON.stringify(payload),
        signal: signal || controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({
          message: response.statusText,
        }));

        return {
          status: "failed",
          error: {
            code: `HTTP_${response.status}`,
            message: errorData.message || response.statusText,
            details: errorData,
          },
        };
      }

      const data: A2AResponse = await response.json();
      return data;
    } catch (error) {
      clearTimeout(timeoutId);

      if (error instanceof Error) {
        if (error.name === "AbortError") {
          return {
            status: "failed",
            error: {
              code: "TIMEOUT",
              message: "Request timed out",
            },
          };
        }

        return {
          status: "failed",
          error: {
            code: "NETWORK_ERROR",
            message: error.message,
          },
        };
      }

      throw error;
    }
  }

  /**
   * Invoke a skill with streaming response
   */
  async *invokeSkillStream(
    options: InvokeSkillOptions,
  ): AsyncGenerator<StreamChunk> {
    const { skill, task, input, context, signal } = options;

    const endpoint = this.selectEndpoint(skill, true);
    if (!endpoint) {
      throw new Error(`No streaming endpoint found for skill: ${skill.name}`);
    }

    // Build request payload
    const payload: A2ARequest = {
      skillId: skill.skillId,
      task,
      input,
      context,
      stream: true,
      tenant: this.config.tenant,
    };

    const response = await fetch(endpoint.path, {
      method: endpoint.method,
      headers: this.buildHeaders(),
      body: JSON.stringify(payload),
      signal,
    });

    if (!response.ok) {
      throw new Error(`Request failed: ${response.statusText}`);
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error("Response body is not readable");
    }

    const decoder = new TextDecoder();
    let buffer = "";

    try {
      while (true) {
        const { done, value } = await reader.read();

        if (done) {
          if (buffer.trim()) {
            yield {
              data: buffer.trim(),
              done: true,
            };
          }
          break;
        }

        buffer += decoder.decode(value, { stream: true });

        // Process complete lines (for SSE or NDJSON)
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          const trimmed = line.trim();
          if (!trimmed) continue;

          // Handle Server-Sent Events format
          if (trimmed.startsWith("data: ")) {
            const data = trimmed.slice(6);
            if (data === "[DONE]") {
              yield { data: "", done: true };
              return;
            }

            try {
              const parsed = JSON.parse(data);
              yield {
                data: parsed.content || parsed.data || data,
                done: false,
                metadata: parsed.metadata,
              };
            } catch {
              yield { data, done: false };
            }
          }
          // Handle NDJSON format
          else {
            try {
              const parsed = JSON.parse(trimmed);
              yield {
                data: parsed.content || parsed.data || trimmed,
                done: false,
                metadata: parsed.metadata,
              };
            } catch {
              yield { data: trimmed, done: false };
            }
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
  }

  /**
   * Get task status (for async operations)
   */
  async getTaskStatus(taskId: string): Promise<A2AResponse> {
    // Find a task status endpoint
    const endpoint = this.contract.skills[0]?.endpoints.find((e) =>
      e.path.includes("/tasks/"),
    );

    if (!endpoint) {
      throw new Error("No task status endpoint available");
    }

    const path = endpoint.path.replace("{taskId}", taskId);

    const response = await fetch(path, {
      method: "GET",
      headers: this.buildHeaders(),
    });

    if (!response.ok) {
      throw new Error(`Failed to get task status: ${response.statusText}`);
    }

    return await response.json();
  }

  /**
   * List all available skills
   */
  getSkills(): AgentSkillContract[] {
    return this.contract.skills;
  }

  /**
   * Find skill by ID
   */
  findSkill(skillId: string): AgentSkillContract | undefined {
    return this.contract.skills.find((s) => s.skillId === skillId);
  }

  /**
   * Find skills by tag
   */
  findSkillsByTag(tag: string): AgentSkillContract[] {
    return this.contract.skills.filter((s) => s.tags.includes(tag));
  }
}

/**
 * Create an agent client from an inferred contract
 */
export function createAgentClient(
  contract: AgentContract,
  config: AgentClientConfig,
): AgentClient {
  return new AgentClient(contract, config);
}
