import type {
  AssertionTask,
  GenAIEvalTaskResult,
  GenAIEvalWorkflowResult,
  LLMJudgeTask,
} from "./task";
import type {
  AlertDispatchConfig,
  AlertCondition,
  DriftType,
  RecordCursor,
  ServiceInfo,
  EntityType,
} from "../types";
import type { DateTime, JsonValue } from "$lib/types";
import type { Prompt, Provider } from "$lib/components/genai/types";
import type { MessageNum } from "$lib/components/genai/provider/types";

export enum Status {
  All = "All",
  Pending = "Pending",
  Processing = "Processing",
  Processed = "Processed",
  Failed = "Failed",
}

export interface GenAIAlertConfig {
  dispatch_config: AlertDispatchConfig;
  schedule: string;
  alert_condition: AlertCondition | null;
}

export interface GenAIEvalConfig {
  sample_ratio: number; // Rust f64 -> TS number
  space: string;
  name: string;
  version: string;
  uid: string;
  alert_config: GenAIAlertConfig;
  drift_type: DriftType;
}

/**
 * Agent interface mirroring the custom Rust Serialize implementation.
 * Fields 'client', 'tools', and 'max_iterations' are explicitly omitted
 * per the Rust 'serialize_struct("Agent", 3)' logic.
 */
export interface Agent {
  id: string;
  provider: Provider;
  system_instruction: MessageNum[];
}

export type TaskStatus = "Pending" | "Running" | "Completed" | "Failed";

export interface AgentResponse {
  id: string;
  response: any;
}

export interface TaskList {
  tasks: Record<string, Task>; // HashMap<String, Arc<RwLock<Task>>>
  execution_order: string[];
}

/**
 * Detailed Task interface mapping to the Rust 'Task' struct.
 * Note: 'output_validator' is omitted as it is marked #[serde(skip)].
 */
export interface Task {
  id: string;
  prompt: Prompt;
  dependencies: string[];
  status: TaskStatus;
  agent_id: string;
  result: AgentResponse | null;
  max_retries: number;
  retry_count: number;
}

/**
 * Workflow interface mirroring the custom Rust Serialize implementation.
 * Note: event_tracker and global_context are omitted as per the Rust logic.
 */
export interface Workflow {
  id: string;
  name: string;
  task_list: TaskList;
  /**
   * Agents mapped by their unique String identifiers.
   * Maps to Rust's HashMap<String, Arc<Agent>>.
   */
  agents: Record<string, Agent>;
}

export interface GenAIEvalProfile {
  config: GenAIEvalConfig;
  assertion_tasks: AssertionTask[];
  llm_judge_tasks: LLMJudgeTask[];
  task_ids: string[];
}

export interface GenAIEvalRecordPaginationRequest {
  service_info: ServiceInfo;
  status?: Status;
  limit?: number;
  cursor_created_at?: DateTime;
  cursor_id?: number;
  direction?: string; // "next" or "previous"
  start_datetime?: DateTime;
  end_datetime?: DateTime;
}

export interface GenAIEvalRecordPaginationResponse {
  items: GenAIEvalRecord[];
  has_next: boolean;
  next_cursor?: RecordCursor;
  has_previous: boolean;
  previous_cursor?: RecordCursor;
}

/**
 * Represents the GenAIEvalRecord struct.
 * Dates are handled as ISO-8601 strings, which is the default
 * serialization for chrono::DateTime.
 */
export interface GenAIEvalRecord {
  record_id: string;
  created_at: string; // ISO-8601 String
  uid: string;
  context: JsonValue;
  id: number; // i64 maps to number (up to 2^53 - 1)
  updated_at: string | null;
  processing_started_at: string | null;
  processing_ended_at: string | null;
  processing_duration: number | null; // i32
  entity_id: number;
  entity_uid: string;
  status: Status;
  entity_type: EntityType;
}

/**
 * Top-level pagination wrapper.
 */
export interface GenAIEvalWorkflowPaginationResponse {
  items: GenAIEvalWorkflowResult[];
  has_next: boolean;
  next_cursor: RecordCursor | null; // Option mapping
  has_previous: boolean;
  previous_cursor: RecordCursor | null;
}

/**
 * Container for multiple task results.
 */
export interface GenAIEvalTaskResponse {
  tasks: GenAIEvalTaskResult[];
}

/** Request interface for GenAIEvalTask */
export interface GenAIEvalTaskRequest {
  record_uid: string;
}
