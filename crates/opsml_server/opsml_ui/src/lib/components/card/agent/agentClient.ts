/**
 * Agent Client for A2A Protocol
 *
 * Provides a type-safe client for interacting with agents based on inferred contracts.
 */

import type {
  AgentContract,
  AgentSkillContract,
  InferredEndpoint,
  A2AResponse,
} from "./agentInference";
import { buildAuthHeaders } from "./agentInference";

/**
 * Message part types for A2A protocol
 */
export interface MessagePart {
  kind: "text" | "image" | "audio" | "video" | "data";
  text?: string;
  data?: string;
  mimeType?: string;
  url?: string;
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
   * Type guard to check if an object is a valid MessagePart
   */
  private isMessagePart(obj: unknown): obj is MessagePart {
    if (typeof obj !== "object" || obj === null) {
      return false;
    }

    const part = obj as Record<string, unknown>;

    // Must have a 'kind' property with valid value
    if (
      typeof part.kind !== "string" ||
      !["text", "image", "audio", "video", "data"].includes(part.kind)
    ) {
      return false;
    }

    // Additional validation based on kind
    if (part.kind === "text" && typeof part.text !== "string") {
      return false;
    }

    if (
      (part.kind === "image" ||
        part.kind === "audio" ||
        part.kind === "video") &&
      typeof part.url !== "string"
    ) {
      return false;
    }

    return true;
  }

  /**
   * Build message parts from input data based on skill's input modes
   */
  private buildMessageParts(
    task: string,
    input: unknown,
    skill: AgentSkillContract,
  ): MessagePart[] {
    const parts: MessagePart[] = [];

    // Always include the task as a text part
    if (task) {
      parts.push({
        kind: "text",
        text: task,
      });
    }

    // If no additional input, return just the task
    if (!input) {
      return parts;
    }

    // If input is already an array of message parts, validate and use it
    if (Array.isArray(input)) {
      const validParts = input.filter((item) =>
        this.isMessagePart(item),
      ) as MessagePart[];
      return [...parts, ...validParts];
    }

    // If input is a string, determine its type based on content or skill modes
    if (typeof input === "string") {
      const trimmedInput = input.trim();

      // Check if it's a URL
      const isUrl =
        trimmedInput.startsWith("http://") ||
        trimmedInput.startsWith("https://");

      if (isUrl) {
        // Determine type from URL or skill's input modes
        if (
          skill.inputModes.includes("image") &&
          this.looksLikeImage(trimmedInput)
        ) {
          parts.push({
            kind: "image",
            url: trimmedInput,
          });
        } else if (
          skill.inputModes.includes("audio") &&
          this.looksLikeAudio(trimmedInput)
        ) {
          parts.push({
            kind: "audio",
            url: trimmedInput,
          });
        } else if (
          skill.inputModes.includes("video") &&
          this.looksLikeVideo(trimmedInput)
        ) {
          parts.push({
            kind: "video",
            url: trimmedInput,
          });
        } else {
          // Default to data with URL
          parts.push({
            kind: "data",
            url: trimmedInput,
          });
        }
      } else {
        // It's plain text
        parts.push({
          kind: "text",
          text: trimmedInput,
        });
      }
    }
    // If input is an object with specific structure
    else if (typeof input === "object" && input !== null) {
      // Check for explicit message part structure
      if (this.isMessagePart(input)) {
        parts.push(input);
      }
      // Convert object to JSON text
      else {
        parts.push({
          kind: "data",
          data: JSON.stringify(input),
          mimeType: "application/json",
        });
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
   * Invoke a skill and get a response
   */
  async invokeSkill(options: InvokeSkillOptions): Promise<A2AResponse> {
    const { skill, task, input, context, signal } = options;
    const stream = options.stream || false;

    const endpoint = this.selectEndpoint(skill, stream);
    if (!endpoint) {
      throw new Error(`No suitable endpoint found for skill: ${skill.name}`);
    }

    // Build message parts based on input type and skill capabilities
    const messageParts = this.buildMessageParts(task, input, skill);

    // Use caller-supplied messageId if provided, otherwise generate one
    const messageId =
      options.messageId ?? crypto.randomUUID().replace(/-/g, "");
    const requestId = crypto.randomUUID();

    // Merge context with messageId and requestId for backend access
    const enrichedContext = {
      ...context,
      messageId, // Include messageId in context for A2A protocol
      requestId, // Include requestId for tracking
    };

    const jsonRpcPayload = {
      id: requestId,
      jsonrpc: "2.0",
      method: "message/send",
      params: {
        message: {
          kind: "message",
          messageId: messageId,
          parts: messageParts,
          role: "user",
          context: enrichedContext, // Use enriched context
        },
      },
    };

    // Make fetch request
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.config.timeout);

    try {
      const headers = {
        "Content-Type": "application/json",
        "X-Message-ID": messageId, // Also send as header for middleware access
        "X-Request-ID": requestId, // Also send as header for middleware access
        ...this.buildHeaders(),
      };

      const response = await fetch(endpoint.path, {
        method: "POST",
        headers,
        body: JSON.stringify(jsonRpcPayload),
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
          messageId,
        };
      }

      // Parse JSON-RPC response
      const jsonRpcResponse = await response.json();

      // Handle JSON-RPC error
      if (jsonRpcResponse.error) {
        return {
          status: "failed",
          error: {
            code: jsonRpcResponse.error.code?.toString() || "RPC_ERROR",
            message: jsonRpcResponse.error.message || "Unknown error",
            details: jsonRpcResponse.error.data,
          },
          messageId,
        };
      }

      // Extract the actual response from JSON-RPC result
      const result = jsonRpcResponse.result;

      return {
        status: "completed",
        result: result?.message?.parts?.[0]?.text || result,
        taskId: jsonRpcResponse.id,
        messageId, // Include messageId in response
      };
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
            messageId,
          };
        }

        return {
          status: "failed",
          error: {
            code: "NETWORK_ERROR",
            message: error.message,
          },
          messageId,
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

    // Build message parts based on input type and skill capabilities
    const messageParts = this.buildMessageParts(task, input, skill);

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
