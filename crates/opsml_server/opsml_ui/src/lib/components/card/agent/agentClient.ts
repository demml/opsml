/**
 * Agent Client for A2A Protocol (spec v1.0)
 *
 * Implements the full A2A operation set per https://a2a-protocol.org/latest/specification/
 * Sections 3, 9 (JSON-RPC), and 11 (HTTP+JSON).
 */

import type {
  AgentContract,
  AgentSkillContract,
  InferredEndpoint,
} from "./agentInference";
import { buildAuthHeaders } from "./agentInference";
import type {
  CancelTaskRequest,
  GetTaskRequest,
  ListTasksRequest,
  ListTasksResponse,
  Part,
  SendMessageRequest,
  SendMessageResponse,
  StreamResponse,
  Struct,
  SubscribeToTaskRequest,
  Task,
} from "./a2a-types";

/** A2A protocol version sent in every request (§3.6.1). */
const A2A_VERSION = "1.0";

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

  /**
   * Server-generated task ID from a previous response.
   * Include this for multi-turn interactions to continue an existing task.
   * Per A2A spec §4.1.4: "If set, the message will be associated with the given task."
   */
  taskId?: string;

  /**
   * Context ID from a previous response.
   * Include this to continue a conversational context (A2A spec §3.4.1).
   */
  contextId?: string;

  /** Input data (text, image URL, audio URL, etc.) or array of message parts */
  input?: unknown;

  /** Additional context */
  context?: Record<string, unknown>;

  /** Whether to stream the response */
  stream?: boolean;

  /** Abort signal for cancellation */
  signal?: AbortSignal;
}

/**
 * Agent client implementing all A2A protocol operations (spec §3.1).
 * Supports JSON-RPC (§9) and HTTP+JSON/REST (§11) bindings.
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

  // ─── Health check ───────────────────────────────────────────────────────────

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

  // ─── Private utilities ───────────────────────────────────────────────────────

  private selectEndpoint(
    skill: AgentSkillContract,
    streaming: boolean,
  ): InferredEndpoint | null {
    return streaming
      ? (skill.endpoints.find((e) => e.streaming) ?? null)
      : (skill.endpoints.find((e) => !e.streaming) ?? null);
  }

  /**
   * Standard headers per spec §3.6.1 (A2A-Version) and §7.3 (auth).
   */
  private buildHeaders(extra?: Record<string, string>): Record<string, string> {
    const authHeaders = buildAuthHeaders(
      this.contract.security.schemes,
      this.config.authConfig,
    );
    return {
      "Content-Type": "application/json",
      "A2A-Version": A2A_VERSION,
      ...authHeaders,
      ...this.config.customHeaders,
      ...extra,
    };
  }

  /**
   * Resolve the first usable interface to a base URL and normalised binding.
   * Returns `{ baseUrl, isJsonRpc }` for task-level operations.
   */
  private resolveInterface(): { baseUrl: string; isJsonRpc: boolean } {
    const iface = this.contract.interfaces[0];
    if (!iface) throw new Error("No agent interface configured");
    const baseUrl = iface.url.endsWith("/")
      ? iface.url.slice(0, -1)
      : iface.url;
    const b = iface.protocolBinding.toLowerCase();
    const isJsonRpc = b === "jsonrpc" || b === "json-rpc" || b === "json_rpc";
    return { baseUrl, isJsonRpc };
  }

  private isJsonRpcEndpoint(endpoint: InferredEndpoint): boolean {
    return endpoint.protocol === "jsonrpc";
  }

  private buildSendBody(
    sendRequest: SendMessageRequest,
    endpoint: InferredEndpoint,
    requestId: string,
    streaming: boolean,
  ): string {
    if (this.isJsonRpcEndpoint(endpoint)) {
      return JSON.stringify({
        jsonrpc: "2.0",
        id: requestId,
        method: streaming ? "SendStreamingMessage" : "SendMessage",
        params: sendRequest,
      });
    }
    return JSON.stringify(sendRequest);
  }

  private async parseJsonOrRpcResponse<T>(
    response: Response,
    isJsonRpc: boolean,
  ): Promise<T> {
    const body = await response.json();
    if (isJsonRpc) {
      if (body.error)
        throw new Error(body.error.message ?? `RPC error ${body.error.code}`);
      return body.result as T;
    }
    return body as T;
  }

  private isPart(obj: unknown): obj is Part {
    if (typeof obj !== "object" || obj === null) return false;
    const p = obj as Record<string, unknown>;
    return (
      typeof p.text === "string" ||
      typeof p.url === "string" ||
      typeof p.raw === "string" ||
      p.data !== undefined
    );
  }

  private buildParts(
    task: string,
    input: unknown,
    skill: AgentSkillContract,
  ): Part[] {
    const parts: Part[] = [];
    if (task) parts.push({ text: task });

    if (!input) return parts;

    if (Array.isArray(input)) {
      return [...parts, ...(input.filter((i) => this.isPart(i)) as Part[])];
    }

    if (typeof input === "string") {
      const trimmed = input.trim();
      if (trimmed.startsWith("http://") || trimmed.startsWith("https://")) {
        const mediaType = this.inferMediaType(trimmed, skill);
        parts.push(mediaType ? { url: trimmed, mediaType } : { url: trimmed });
      } else {
        parts.push({ text: trimmed });
      }
    } else if (typeof input === "object" && input !== null) {
      parts.push(
        this.isPart(input)
          ? (input as Part)
          : { data: input, mediaType: "application/json" },
      );
    }

    return parts;
  }

  private inferMediaType(
    url: string,
    skill: AgentSkillContract,
  ): string | undefined {
    const lower = url.toLowerCase();
    const img = [".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".bmp"];
    const aud = [".mp3", ".wav", ".ogg", ".m4a", ".flac", ".aac"];
    const vid = [".mp4", ".webm", ".mov", ".avi", ".mkv"];
    if (
      skill.inputModes.includes("image") &&
      img.some((e) => lower.includes(e))
    )
      return "image/*";
    if (
      skill.inputModes.includes("audio") &&
      aud.some((e) => lower.includes(e))
    )
      return "audio/*";
    if (
      skill.inputModes.includes("video") &&
      vid.some((e) => lower.includes(e))
    )
      return "video/*";
    return undefined;
  }

  // ─── SSE / streaming helpers ─────────────────────────────────────────────────

  /**
   * Parse a raw SSE data line into a `StreamResponse`.
   * Handles both plain HTTP+JSON (`data: {...}`) and JSON-RPC wrapped events
   * (`data: {"jsonrpc":"2.0","result":{...}}`).
   */
  private parseStreamEvent(
    data: string,
    isJsonRpc: boolean,
  ): StreamResponse | null {
    try {
      const parsed = JSON.parse(data) as Record<string, unknown>;
      if (isJsonRpc) {
        if (parsed.error) {
          throw new Error(
            String(
              (parsed.error as Record<string, unknown>).message ??
                "RPC stream error",
            ),
          );
        }
        return (parsed.result ?? parsed) as StreamResponse;
      }
      return parsed as StreamResponse;
    } catch {
      return null;
    }
  }

  /**
   * Read an SSE response body and yield each `StreamResponse` event.
   * Per spec §11.7 and §9.4.2.
   */
  private async *readSseStream(
    body: ReadableStream<Uint8Array>,
    isJsonRpc: boolean,
    signal?: AbortSignal,
  ): AsyncGenerator<StreamResponse> {
    const reader = body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    try {
      while (true) {
        if (signal?.aborted) break;
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() ?? "";

        for (const line of lines) {
          const trimmed = line.trim();
          if (!trimmed.startsWith("data:")) continue;
          const raw = trimmed.slice(5).trim();
          if (raw === "[DONE]" || raw === "") continue;

          const event = this.parseStreamEvent(raw, isJsonRpc);
          if (event) yield event;
        }
      }

      // flush remaining buffer
      if (buffer.trim().startsWith("data:")) {
        const raw = buffer.trim().slice(5).trim();
        if (raw && raw !== "[DONE]") {
          const event = this.parseStreamEvent(raw, isJsonRpc);
          if (event) yield event;
        }
      }
    } finally {
      reader.releaseLock();
    }
  }

  // ─── Public: build request ────────────────────────────────────────────────────

  buildSendMessageRequest(options: InvokeSkillOptions): SendMessageRequest {
    const { skill, task, input, context, taskId, contextId } = options;
    const parts = this.buildParts(task, input, skill);
    const messageId = options.messageId ?? crypto.randomUUID();

    return {
      message: {
        messageId,
        role: "user",
        parts,
        ...(taskId && { taskId }),
        ...(contextId && { contextId }),
        ...(context && { metadata: context as Struct }),
      },
      ...(this.config.tenant && { tenant: this.config.tenant }),
    };
  }

  // ─── Operation: Send Message (§3.1.1) ────────────────────────────────────────

  async invokeSkillWithRequest(
    sendRequest: SendMessageRequest,
    options: InvokeSkillOptions,
  ): Promise<SendMessageResponse> {
    const { skill, signal } = options;
    const requestId = crypto.randomUUID();

    const endpoint = this.selectEndpoint(skill, false);
    if (!endpoint) {
      throw new Error(
        `No send endpoint found for skill "${skill.name}". ` +
          `Check that the agent's supportedInterfaces has a recognised protocolBinding (JSONRPC, HTTP+JSON, GRPC).`,
      );
    }

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.config.timeout);

    try {
      const response = await fetch(endpoint.path, {
        method: "POST",
        headers: this.buildHeaders({ "X-Request-ID": requestId }),
        body: this.buildSendBody(sendRequest, endpoint, requestId, false),
        signal: signal ?? controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorData = await response
          .json()
          .catch(() => ({ message: response.statusText }));
        throw new Error(
          errorData.detail ??
            errorData.message ??
            `HTTP ${response.status}: ${response.statusText}`,
        );
      }

      return this.parseJsonOrRpcResponse<SendMessageResponse>(
        response,
        this.isJsonRpcEndpoint(endpoint),
      );
    } catch (error) {
      clearTimeout(timeoutId);
      if (error instanceof Error && error.name === "AbortError")
        throw new Error("Request timed out");
      throw error;
    }
  }

  async invokeSkill(options: InvokeSkillOptions): Promise<InvokeSkillResult> {
    const sendRequest = this.buildSendMessageRequest(options);
    const response = await this.invokeSkillWithRequest(sendRequest, options);
    return { request: sendRequest, response };
  }

  // ─── Operation: Send Streaming Message (§3.1.2) ───────────────────────────────

  /**
   * Send a message with real-time streaming via SSE.
   * Yields `StreamResponse` objects (§3.2.3): task, message, statusUpdate, or artifactUpdate.
   */
  async *invokeSkillStream(
    options: InvokeSkillOptions,
  ): AsyncGenerator<StreamResponse> {
    const { skill, signal } = options;

    const endpoint = this.selectEndpoint(skill, true);
    if (!endpoint) {
      throw new Error(
        `No streaming endpoint found for skill "${skill.name}". ` +
          `Ensure the agent declares streaming capability and the interface binding is supported.`,
      );
    }

    const sendRequest = this.buildSendMessageRequest({
      ...options,
      stream: true,
    });
    const requestId = crypto.randomUUID();
    const isJsonRpc = this.isJsonRpcEndpoint(endpoint);

    const response = await fetch(endpoint.path, {
      method: "POST",
      headers: this.buildHeaders({
        Accept: "text/event-stream",
        "X-Request-ID": requestId,
      }),
      body: this.buildSendBody(sendRequest, endpoint, requestId, true),
      signal,
    });

    if (!response.ok) {
      const errorData = await response
        .json()
        .catch(() => ({ message: response.statusText }));
      throw new Error(
        errorData.detail ??
          errorData.message ??
          `Streaming request failed: ${response.status} ${response.statusText}`,
      );
    }

    if (!response.body) throw new Error("Response body is not readable");

    yield* this.readSseStream(response.body, isJsonRpc, signal);
  }

  // ─── Operation: Get Task (§3.1.3) ─────────────────────────────────────────────

  /**
   * Retrieve the current state of a task.
   * HTTP+JSON: `GET /tasks/{id}` (§11.3.2)
   * JSON-RPC:  `POST <baseUrl>` method `GetTask` (§9.4.3)
   */
  async getTask(params: GetTaskRequest): Promise<Task> {
    const { baseUrl, isJsonRpc } = this.resolveInterface();

    if (isJsonRpc) {
      const response = await fetch(baseUrl, {
        method: "POST",
        headers: this.buildHeaders(),
        body: JSON.stringify({
          jsonrpc: "2.0",
          id: crypto.randomUUID(),
          method: "GetTask",
          params,
        }),
      });
      if (!response.ok)
        throw new Error(`GetTask failed: ${response.statusText}`);
      return this.parseJsonOrRpcResponse<Task>(response, true);
    }

    const qs =
      params.historyLength !== undefined
        ? `?historyLength=${params.historyLength}`
        : "";
    const response = await fetch(
      `${baseUrl}/tasks/${encodeURIComponent(params.id)}${qs}`,
      { method: "GET", headers: this.buildHeaders() },
    );
    if (!response.ok) throw new Error(`GetTask failed: ${response.statusText}`);
    return response.json() as Promise<Task>;
  }

  // ─── Operation: List Tasks (§3.1.4) ───────────────────────────────────────────

  /**
   * List tasks with optional filtering and pagination.
   * HTTP+JSON: `GET /tasks` (§11.3.2, §11.5)
   * JSON-RPC:  `POST <baseUrl>` method `ListTasks` (§9.4.4)
   */
  async listTasks(params: ListTasksRequest = {}): Promise<ListTasksResponse> {
    const { baseUrl, isJsonRpc } = this.resolveInterface();

    if (isJsonRpc) {
      const response = await fetch(baseUrl, {
        method: "POST",
        headers: this.buildHeaders(),
        body: JSON.stringify({
          jsonrpc: "2.0",
          id: crypto.randomUUID(),
          method: "ListTasks",
          params,
        }),
      });
      if (!response.ok)
        throw new Error(`ListTasks failed: ${response.statusText}`);
      return this.parseJsonOrRpcResponse<ListTasksResponse>(response, true);
    }

    // Build query string from params (§11.5 camelCase query params)
    const qs = new URLSearchParams();
    if (params.contextId) qs.set("contextId", params.contextId);
    if (params.status) qs.set("status", params.status);
    if (params.pageSize !== undefined)
      qs.set("pageSize", String(params.pageSize));
    if (params.pageToken) qs.set("pageToken", params.pageToken);
    if (params.historyLength !== undefined)
      qs.set("historyLength", String(params.historyLength));
    if (params.statusTimestampAfter)
      qs.set("statusTimestampAfter", params.statusTimestampAfter);
    if (params.includeArtifacts !== undefined)
      qs.set("includeArtifacts", String(params.includeArtifacts));

    const query = qs.toString();
    const response = await fetch(
      `${baseUrl}/tasks${query ? `?${query}` : ""}`,
      { method: "GET", headers: this.buildHeaders() },
    );
    if (!response.ok)
      throw new Error(`ListTasks failed: ${response.statusText}`);
    return response.json() as Promise<ListTasksResponse>;
  }

  // ─── Operation: Cancel Task (§3.1.5) ──────────────────────────────────────────

  /**
   * Request cancellation of an ongoing task.
   * HTTP+JSON: `POST /tasks/{id}:cancel` (§11.3.2)
   * JSON-RPC:  `POST <baseUrl>` method `CancelTask` (§9.4.5)
   */
  async cancelTask(params: CancelTaskRequest): Promise<Task> {
    const { baseUrl, isJsonRpc } = this.resolveInterface();

    if (isJsonRpc) {
      const response = await fetch(baseUrl, {
        method: "POST",
        headers: this.buildHeaders(),
        body: JSON.stringify({
          jsonrpc: "2.0",
          id: crypto.randomUUID(),
          method: "CancelTask",
          params,
        }),
      });
      if (!response.ok)
        throw new Error(`CancelTask failed: ${response.statusText}`);
      return this.parseJsonOrRpcResponse<Task>(response, true);
    }

    const response = await fetch(
      `${baseUrl}/tasks/${encodeURIComponent(params.id)}:cancel`,
      {
        method: "POST",
        headers: this.buildHeaders(),
        body: JSON.stringify({ metadata: params.metadata }),
      },
    );
    if (!response.ok)
      throw new Error(`CancelTask failed: ${response.statusText}`);
    return response.json() as Promise<Task>;
  }

  // ─── Operation: Subscribe to Task (§3.1.6) ────────────────────────────────────

  /**
   * Subscribe to real-time updates for an existing task via SSE.
   * HTTP+JSON: `POST /tasks/{id}:subscribe` (§11.3.2)
   * JSON-RPC:  `POST <baseUrl>` method `SubscribeToTask` (§9.4.6)
   *
   * Stream MUST begin with the current Task state, then yield
   * TaskStatusUpdateEvent / TaskArtifactUpdateEvent until terminal state.
   */
  async *subscribeToTask(
    params: SubscribeToTaskRequest,
  ): AsyncGenerator<StreamResponse> {
    const { baseUrl, isJsonRpc } = this.resolveInterface();

    let path: string;
    let body: string;

    if (isJsonRpc) {
      path = baseUrl;
      body = JSON.stringify({
        jsonrpc: "2.0",
        id: crypto.randomUUID(),
        method: "SubscribeToTask",
        params,
      });
    } else {
      path = `${baseUrl}/tasks/${encodeURIComponent(params.id)}:subscribe`;
      body = "{}";
    }

    const response = await fetch(path, {
      method: "POST",
      headers: this.buildHeaders({ Accept: "text/event-stream" }),
      body,
    });

    if (!response.ok) {
      const errorData = await response
        .json()
        .catch(() => ({ message: response.statusText }));
      throw new Error(
        errorData.detail ??
          errorData.message ??
          `SubscribeToTask failed: ${response.status} ${response.statusText}`,
      );
    }

    if (!response.body) throw new Error("Response body is not readable");

    yield* this.readSseStream(response.body, isJsonRpc);
  }

  // ─── Helpers ──────────────────────────────────────────────────────────────────

  getSkills(): AgentSkillContract[] {
    return this.contract.skills;
  }

  findSkill(skillId: string): AgentSkillContract | undefined {
    return this.contract.skills.find((s) => s.skillId === skillId);
  }

  findSkillsByTag(tag: string): AgentSkillContract[] {
    return this.contract.skills.filter((s) => s.tags.includes(tag));
  }
}

export function createAgentClient(
  contract: AgentContract,
  config: AgentClientConfig,
): AgentClient {
  return new AgentClient(contract, config);
}

// ─── ADK metadata helpers (Google Agent Developer Kit) ────────────────────────

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

export function isAdkMetadata(metadata: Struct): metadata is AdkMetadata {
  if (typeof metadata !== "object" || metadata === null) return false;
  return Object.keys(metadata).some((key) => key.startsWith("adk_"));
}
