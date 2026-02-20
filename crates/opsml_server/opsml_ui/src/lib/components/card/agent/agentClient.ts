/**
 * Agent Client for A2A Protocol
 *
 * Provides a type-safe client for interacting with agents based on inferred contracts.
 */

import type {
  AgentContract,
  AgentSkillContract,
  InferredEndpoint,
} from "./agentInference";
import { buildAuthHeaders } from "./agentInference";
import type {
  Part,
  SendMessageRequest,
  SendMessageResponse,
  Struct,
  Task,
} from "./a2a-types";

export interface InvokeSkillResult {
  request: SendMessageRequest;
  response: SendMessageResponse;
}

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

  /** Pre-generated message ID to associate this exchange */
  messageId?: string;

  /** Input data (text, image URL, audio URL, etc.) or array of message parts */
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
   * Check health of the agent by calling a healthcheck endpoint if available
   */
  async checkHealth(url: string): Promise<boolean> {
    try {
      const response = await fetch(url, {
        method: "GET",
        headers: this.buildHeaders(),
      });
      return response.ok;
    } catch {
      return false;
    }
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
   * Type guard to check if an object is a valid Part
   */
  private isPart(obj: unknown): obj is Part {
    if (typeof obj !== "object" || obj === null) {
      return false;
    }
    const p = obj as Record<string, unknown>;
    return (
      typeof p.text === "string" ||
      typeof p.url === "string" ||
      typeof p.raw === "string" ||
      p.data !== undefined
    );
  }

  /**
   * Build A2A spec Parts from task text and optional supplementary input.
   */
  private buildParts(
    task: string,
    input: unknown,
    skill: AgentSkillContract,
  ): Part[] {
    const parts: Part[] = [];

    if (task) {
      parts.push({ text: task });
    }

    if (!input) {
      return parts;
    }

    if (Array.isArray(input)) {
      const validParts = input.filter((item) => this.isPart(item)) as Part[];
      return [...parts, ...validParts];
    }

    if (typeof input === "string") {
      const trimmed = input.trim();
      const isUrl =
        trimmed.startsWith("http://") || trimmed.startsWith("https://");

      if (isUrl) {
        if (
          skill.inputModes.includes("image") &&
          this.looksLikeImage(trimmed)
        ) {
          parts.push({ url: trimmed, mediaType: "image/*" });
        } else if (
          skill.inputModes.includes("audio") &&
          this.looksLikeAudio(trimmed)
        ) {
          parts.push({ url: trimmed, mediaType: "audio/*" });
        } else if (
          skill.inputModes.includes("video") &&
          this.looksLikeVideo(trimmed)
        ) {
          parts.push({ url: trimmed, mediaType: "video/*" });
        } else {
          parts.push({ url: trimmed });
        }
      } else {
        parts.push({ text: trimmed });
      }
    } else if (typeof input === "object" && input !== null) {
      if (this.isPart(input)) {
        parts.push(input);
      } else {
        parts.push({ data: input, mediaType: "application/json" });
      }
    }

    return parts;
  }

  /**
   * Check if URL looks like an image
   */
  private looksLikeImage(url: string): boolean {
    const imageExtensions = [
      ".jpg",
      ".jpeg",
      ".png",
      ".gif",
      ".webp",
      ".svg",
      ".bmp",
    ];
    const lowerUrl = url.toLowerCase();
    return imageExtensions.some((ext) => lowerUrl.includes(ext));
  }

  /**
   * Check if URL looks like audio
   */
  private looksLikeAudio(url: string): boolean {
    const audioExtensions = [".mp3", ".wav", ".ogg", ".m4a", ".flac", ".aac"];
    const lowerUrl = url.toLowerCase();
    return audioExtensions.some((ext) => lowerUrl.includes(ext));
  }

  /**
   * Check if URL looks like video
   */
  private looksLikeVideo(url: string): boolean {
    const videoExtensions = [".mp4", ".webm", ".mov", ".avi", ".mkv"];
    const lowerUrl = url.toLowerCase();
    return videoExtensions.some((ext) => lowerUrl.includes(ext));
  }

  /**
   * Build the A2A SendMessageRequest from the given options
   * This can be used for debugging or for custom invocation scenarios
   */
  buildSendMessageRequest(options: InvokeSkillOptions): SendMessageRequest {
    const { skill, task, input, context } = options;
    const stream = options.stream || false;

    const endpoint = this.selectEndpoint(skill, stream);
    if (!endpoint) {
      throw new Error(`No suitable endpoint found for skill: ${skill.name}`);
    }

    const parts = this.buildParts(task, input, skill);
    const messageId =
      options.messageId ?? crypto.randomUUID().replace(/-/g, "");

    const sendRequest: SendMessageRequest = {
      message: {
        messageId,
        role: "user",
        parts,
        ...(context && { metadata: context as Record<string, unknown> }),
      },
      ...(this.config.tenant && { tenant: this.config.tenant }),
    };

    return sendRequest;
  }

  async invokeSkillWithRequest(
    sendRequest: SendMessageRequest,
    options: InvokeSkillOptions,
  ): Promise<SendMessageResponse> {
    const { skill, signal } = options;
    const stream = options.stream || false;
    const requestId = crypto.randomUUID();

    const jsonRpcPayload = {
      id: requestId,
      jsonrpc: "2.0",
      method: "message/send",
      params: sendRequest,
    };

    const endpoint = this.selectEndpoint(skill, stream);
    if (!endpoint) {
      throw new Error(`No suitable endpoint found for skill: ${skill.name}`);
    }

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.config.timeout);

    try {
      const response = await fetch(endpoint.path, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Message-ID": sendRequest.message.messageId,
          "X-Request-ID": requestId,
          ...this.buildHeaders(),
        },
        body: JSON.stringify(jsonRpcPayload),
        signal: signal || controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({
          message: response.statusText,
        }));
        throw new Error(
          errorData.message ||
            `HTTP ${response.status}: ${response.statusText}`,
        );
      }

      const jsonRpcResponse = await response.json();

      if (jsonRpcResponse.error) {
        throw new Error(
          jsonRpcResponse.error.message ||
            `RPC error ${jsonRpcResponse.error.code}`,
        );
      }

      return jsonRpcResponse.result as SendMessageResponse;
    } catch (error) {
      clearTimeout(timeoutId);
      if (error instanceof Error && error.name === "AbortError") {
        throw new Error("Request timed out");
      }
      throw error;
    }
  }

  /**
   * Invoke a skill and return the typed A2A request/response pair.
   * Throws on HTTP errors, JSON-RPC errors, and network failures.
   */
  async invokeSkill(options: InvokeSkillOptions): Promise<InvokeSkillResult> {
    const { skill, task, input, context, signal } = options;
    const stream = options.stream || false;

    const endpoint = this.selectEndpoint(skill, stream);
    if (!endpoint) {
      throw new Error(`No suitable endpoint found for skill: ${skill.name}`);
    }

    const parts = this.buildParts(task, input, skill);
    const messageId =
      options.messageId ?? crypto.randomUUID().replace(/-/g, "");
    const requestId = crypto.randomUUID();

    const sendRequest: SendMessageRequest = {
      message: {
        messageId,
        role: "user",
        parts,
        ...(context && { metadata: context as Record<string, unknown> }),
      },
      ...(this.config.tenant && { tenant: this.config.tenant }),
    };

    const jsonRpcPayload = {
      id: requestId,
      jsonrpc: "2.0",
      method: "message/send",
      params: sendRequest,
    };

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.config.timeout);

    try {
      const response = await fetch(endpoint.path, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Message-ID": messageId,
          "X-Request-ID": requestId,
          ...this.buildHeaders(),
        },
        body: JSON.stringify(jsonRpcPayload),
        signal: signal || controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({
          message: response.statusText,
        }));
        throw new Error(
          errorData.message ||
            `HTTP ${response.status}: ${response.statusText}`,
        );
      }

      const jsonRpcResponse = await response.json();

      if (jsonRpcResponse.error) {
        throw new Error(
          jsonRpcResponse.error.message ||
            `RPC error ${jsonRpcResponse.error.code}`,
        );
      }

      return {
        request: sendRequest,
        response: jsonRpcResponse.result as SendMessageResponse,
      };
    } catch (error) {
      clearTimeout(timeoutId);
      if (error instanceof Error && error.name === "AbortError") {
        throw new Error("Request timed out");
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

    // Build message parts based on input type and skill capabilities
    const messageParts = this.buildParts(task, input, skill);

    // Build JSON-RPC 2.0 request for A2A protocol (with streaming enabled)
    const messageId = crypto.randomUUID().replace(/-/g, "");
    const requestId = crypto.randomUUID();

    const jsonRpcPayload = {
      id: requestId,
      jsonrpc: "2.0",
      method: "message/send",
      params: {
        message: {
          kind: "message",
          message_id: messageId,
          parts: messageParts,
          role: "user",
          ...(context && { context }),
        },
        stream: true, // Enable streaming
      },
    };

    const response = await fetch(endpoint.path, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...this.buildHeaders(),
      },
      body: JSON.stringify(jsonRpcPayload),
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
  async getTaskStatus(taskId: string): Promise<Task> {
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

    const jsonRpcResponse = await response.json();
    return jsonRpcResponse.result as Task;
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

export interface PromptTokensDetails {
  modality: string;
  tokenCount: number;
}

export interface UsageMetadata {
  candidatesTokenCount: number;
  promptTokenCount: number;
  promptTokensDetails: PromptTokensDetails[];
  thoughtsTokenCount: number;
  totalTokenCount: number;
}

export interface AdkActions {
  stateDelta: Struct;
  artifactDelta: Struct;
  requestedAuthConfigs: Struct;
  requestedToolConfirmations: Struct;
}

export interface AdkMetadata extends Struct {
  adk_app_name: string;
  adk_user_id: string;
  adk_session_id: string;
  adk_invocation_id: string;
  adk_author: string;
  adk_event_id: string;
  adk_usage_metadata: UsageMetadata;
  adk_actions: AdkActions;
}

/** Checks if adk_ is found in metadata keys */
export function isAdkMetadata(metadata: Struct): metadata is AdkMetadata {
  if (typeof metadata !== "object" || metadata === null) {
    return false;
  }
  return Object.keys(metadata).some((key) => key.startsWith("adk_"));
}
