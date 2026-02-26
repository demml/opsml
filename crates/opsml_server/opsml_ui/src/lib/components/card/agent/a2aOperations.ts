/**
 * A2A Protocol Operation Names
 *
 * Handles version-specific operation naming across protocol versions.
 *
 * v0.3.0: Slash-based operation names (message/send, tasks/get)
 * v1.0:   PascalCase operation names (SendMessage, GetTask)
 *
 * See: https://a2a-protocol.org/latest/whats-new-v1/
 */

/**
 * Supported A2A protocol versions
 */
export type A2AProtocolVersion = "0.3" | "0.3.0" | "1.0" | "1.0.0";

/**
 * Normalized protocol version (internal representation)
 */
type NormalizedVersion = "0.3" | "1.0";

/**
 * Core A2A operations
 */
export enum A2AOperation {
  SendMessage = "SendMessage",
  SendStreamingMessage = "SendStreamingMessage",
  GetTask = "GetTask",
  ListTasks = "ListTasks",
  CancelTask = "CancelTask",
  SubscribeToTask = "SubscribeToTask",
  GetExtendedAgentCard = "GetExtendedAgentCard",
  CreatePushNotificationConfig = "CreatePushNotificationConfig",
  GetPushNotificationConfig = "GetPushNotificationConfig",
  ListPushNotificationConfigs = "ListPushNotificationConfigs",
  DeletePushNotificationConfig = "DeletePushNotificationConfig",
}

/**
 * Protocol binding type
 */
export type ProtocolBinding = "jsonrpc" | "http+json" | "grpc" | "websocket";

/**
 * Operation name mapping for each protocol version
 */
const OPERATION_NAMES: Record<
  NormalizedVersion,
  Record<A2AOperation, string>
> = {
  "0.3": {
    [A2AOperation.SendMessage]: "message/send",
    [A2AOperation.SendStreamingMessage]: "message/stream",
    [A2AOperation.GetTask]: "tasks/get",
    [A2AOperation.ListTasks]: "tasks/list",
    [A2AOperation.CancelTask]: "tasks/cancel",
    [A2AOperation.SubscribeToTask]: "tasks/resubscribe",
    [A2AOperation.GetExtendedAgentCard]: "agent/getAuthenticatedExtendedCard",
    [A2AOperation.CreatePushNotificationConfig]:
      "tasks/pushNotificationConfig/set",
    [A2AOperation.GetPushNotificationConfig]:
      "tasks/pushNotificationConfig/get",
    [A2AOperation.ListPushNotificationConfigs]:
      "tasks/pushNotificationConfig/list",
    [A2AOperation.DeletePushNotificationConfig]:
      "tasks/pushNotificationConfig/delete",
  },
  "1.0": {
    [A2AOperation.SendMessage]: "SendMessage",
    [A2AOperation.SendStreamingMessage]: "SendStreamingMessage",
    [A2AOperation.GetTask]: "GetTask",
    [A2AOperation.ListTasks]: "ListTasks",
    [A2AOperation.CancelTask]: "CancelTask",
    [A2AOperation.SubscribeToTask]: "SubscribeToTask",
    [A2AOperation.GetExtendedAgentCard]: "GetExtendedAgentCard",
    [A2AOperation.CreatePushNotificationConfig]: "CreatePushNotificationConfig",
    [A2AOperation.GetPushNotificationConfig]: "GetPushNotificationConfig",
    [A2AOperation.ListPushNotificationConfigs]: "ListPushNotificationConfigs",
    [A2AOperation.DeletePushNotificationConfig]: "DeletePushNotificationConfig",
  },
};

/**
 * HTTP+JSON URL paths for v0.3.0 (includes /v1/ prefix)
 */
const HTTP_JSON_PATHS_V0_3: Record<A2AOperation, string> = {
  [A2AOperation.SendMessage]: "/v1/message:send",
  [A2AOperation.SendStreamingMessage]: "/v1/message:stream",
  [A2AOperation.GetTask]: "/v1/tasks",
  [A2AOperation.ListTasks]: "/v1/tasks",
  [A2AOperation.CancelTask]: "/v1/tasks",
  [A2AOperation.SubscribeToTask]: "/v1/tasks",
  [A2AOperation.GetExtendedAgentCard]: "/v1/agent/extended",
  [A2AOperation.CreatePushNotificationConfig]:
    "/v1/tasks/pushNotificationConfigs",
  [A2AOperation.GetPushNotificationConfig]: "/v1/tasks/pushNotificationConfigs",
  [A2AOperation.ListPushNotificationConfigs]:
    "/v1/tasks/pushNotificationConfigs",
  [A2AOperation.DeletePushNotificationConfig]:
    "/v1/tasks/pushNotificationConfigs",
};

/**
 * HTTP+JSON URL paths for v1.0 (no /v1/ prefix per spec §11.3)
 */
const HTTP_JSON_PATHS_V1_0: Record<A2AOperation, string> = {
  [A2AOperation.SendMessage]: "/message:send",
  [A2AOperation.SendStreamingMessage]: "/message:stream",
  [A2AOperation.GetTask]: "/tasks",
  [A2AOperation.ListTasks]: "/tasks",
  [A2AOperation.CancelTask]: "/tasks",
  [A2AOperation.SubscribeToTask]: "/tasks",
  [A2AOperation.GetExtendedAgentCard]: "/agent/extended",
  [A2AOperation.CreatePushNotificationConfig]: "/tasks/pushNotificationConfigs",
  [A2AOperation.GetPushNotificationConfig]: "/tasks/pushNotificationConfigs",
  [A2AOperation.ListPushNotificationConfigs]: "/tasks/pushNotificationConfigs",
  [A2AOperation.DeletePushNotificationConfig]: "/tasks/pushNotificationConfigs",
};

/**
 * Normalize protocol version string to canonical form
 */
function normalizeVersion(version: string | undefined): NormalizedVersion {
  if (!version) return "1.0"; // Default to latest
  const v = version.toLowerCase().trim();

  // v0.3 variants
  if (v === "0.3" || v === "0.3.0" || v.startsWith("0.3.")) return "0.3";

  // v1.0 variants (default)
  return "1.0";
}

/**
 * Normalize protocol binding string
 */
function normalizeBinding(binding: string): ProtocolBinding {
  const b = binding.toLowerCase().trim();
  if (b === "jsonrpc" || b === "json-rpc" || b === "json_rpc") return "jsonrpc";
  if (
    b === "http+json" ||
    b === "httpjson" ||
    b === "http" ||
    b === "https" ||
    b === "rest"
  )
    return "http+json";
  if (b === "grpc" || b === "grpc+proto") return "grpc";
  if (b === "websocket" || b === "ws" || b === "wss") return "websocket";
  return "http+json"; // Default fallback
}

/**
 * Get the operation name for a specific protocol version and binding.
 *
 * For JSON-RPC: Returns method name to use in "method" field
 * For HTTP+JSON: Returns the method name (path determination is separate)
 *
 * @example
 * ```ts
 * // v0.3.0 JSON-RPC
 * getOperationName(A2AOperation.SendMessage, "0.3.0", "jsonrpc")
 * // => "message/send"
 *
 * // v1.0 JSON-RPC
 * getOperationName(A2AOperation.SendMessage, "1.0", "jsonrpc")
 * // => "SendMessage"
 * ```
 */
export function getOperationName(
  operation: A2AOperation,
  protocolVersion: string | undefined,
  protocolBinding: string,
): string {
  const version = normalizeVersion(protocolVersion);
  const binding = normalizeBinding(protocolBinding);

  // For JSON-RPC and gRPC, return the method name directly
  if (binding === "jsonrpc" || binding === "grpc") {
    return OPERATION_NAMES[version][operation];
  }

  // For HTTP+JSON, return the method name (caller handles path construction)
  return OPERATION_NAMES[version][operation];
}

/**
 * Get the full HTTP+JSON URL path for an operation.
 * Only applicable for HTTP+JSON binding.
 *
 * @example
 * ```ts
 * // v0.3.0
 * getHttpJsonPath(A2AOperation.SendMessage, "0.3.0")
 * // => "/v1/message:send"
 *
 * // v1.0
 * getHttpJsonPath(A2AOperation.SendMessage, "1.0")
 * // => "/message:send"
 * ```
 */
export function getHttpJsonPath(
  operation: A2AOperation,
  protocolVersion: string | undefined,
): string {
  const version = normalizeVersion(protocolVersion);
  return version === "0.3"
    ? HTTP_JSON_PATHS_V0_3[operation]
    : HTTP_JSON_PATHS_V1_0[operation];
}

/**
 * A2A Operation resolver that encapsulates version and binding logic
 */
export class A2AOperationResolver {
  private version: NormalizedVersion;
  private binding: ProtocolBinding;

  constructor(protocolVersion: string | undefined, protocolBinding: string) {
    this.version = normalizeVersion(protocolVersion);
    this.binding = normalizeBinding(protocolBinding);
  }

  /**
   * Get the operation name (method name for JSON-RPC/gRPC)
   */
  getMethodName(operation: A2AOperation): string {
    return OPERATION_NAMES[this.version][operation];
  }

  /**
   * Get the full URL path for HTTP+JSON operations
   */
  getHttpJsonPath(operation: A2AOperation): string {
    if (this.binding !== "http+json") {
      throw new Error(
        `getHttpJsonPath() only valid for http+json binding, got: ${this.binding}`,
      );
    }
    return this.version === "0.3"
      ? HTTP_JSON_PATHS_V0_3[operation]
      : HTTP_JSON_PATHS_V1_0[operation];
  }

  /**
   * Check if this is a v0.3.x protocol
   */
  isV0_3(): boolean {
    return this.version === "0.3";
  }

  /**
   * Check if this is a v1.0+ protocol
   */
  isV1_0(): boolean {
    return this.version === "1.0";
  }

  /**
   * Get the protocol binding
   */
  getBinding(): ProtocolBinding {
    return this.binding;
  }

  /**
   * Get the normalized version
   */
  getVersion(): NormalizedVersion {
    return this.version;
  }
}

/**
 * Create an operation resolver from an AgentInterface
 */
export function createOperationResolver(agentInterface: {
  protocolVersion?: string;
  protocolBinding: string;
}): A2AOperationResolver {
  return new A2AOperationResolver(
    agentInterface.protocolVersion,
    agentInterface.protocolBinding,
  );
}
