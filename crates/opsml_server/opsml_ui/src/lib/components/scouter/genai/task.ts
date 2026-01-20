import type { Prompt } from "$lib/components/genai/types";
import type { JsonValue } from "$lib/types";

/**
 * Represents the fundamental Comparison Operators available in the Rust backend.
 * These are represented as string literals for seamless JSON deserialization.
 */
export type ComparisonOperator =
  | "Equals"
  | "NotEqual"
  | "GreaterThan"
  | "GreaterThanOrEqual"
  | "LessThan"
  | "LessThanOrEqual"
  | "Contains"
  | "NotContains"
  | "StartsWith"
  | "EndsWith"
  | "Matches"
  | "HasLengthGreaterThan"
  | "HasLengthLessThan"
  | "HasLengthEqual"
  | "HasLengthGreaterThanOrEqual"
  | "HasLengthLessThanOrEqual"
  | "IsNumeric"
  | "IsString"
  | "IsBoolean"
  | "IsNull"
  | "IsArray"
  | "IsObject"
  | "IsEmail"
  | "IsUrl"
  | "IsUuid"
  | "IsIso8601"
  | "IsJson"
  | "MatchesRegex"
  | "InRange"
  | "NotInRange"
  | "IsPositive"
  | "IsNegative"
  | "IsZero"
  | "ContainsAll"
  | "ContainsAny"
  | "ContainsNone"
  | "IsEmpty"
  | "IsNotEmpty"
  | "HasUniqueItems"
  | "IsAlphabetic"
  | "IsAlphanumeric"
  | "IsLowerCase"
  | "IsUpperCase"
  | "ContainsWord"
  | "ApproximatelyEquals";

/**
 * Maps to EvaluationTaskType enum.
 */
export type EvaluationTaskType =
  | "Assertion"
  | "LLMJudge"
  | "Conditional"
  | "HumanValidation";

/**
 * Result of an assertion execution.
 */
export interface AssertionResult {
  passed: boolean;
  actual: JsonValue;
  message: string;
  expected: JsonValue;
}

/**
 * The primary AssertionTask interface.
 * Matches the Rust 'AssertionTask' struct.
 */
export interface AssertionTask {
  id: string;
  field_path: string | null; // Option<String>
  operator: ComparisonOperator;
  expected_value: JsonValue; // Value
  description: string | null; // Option<String>
  depends_on: string[]; // Vec<String>
  task_type: EvaluationTaskType;
  result?: AssertionResult; // Option<AssertionResult> + skip_serializing_if
  condition: boolean;
}

export interface LLMJudgeTask {
  id: string;
  prompt: Prompt;
  field_path: string | null;
  expected_value: JsonValue;
  operator: ComparisonOperator;
  task_type: EvaluationTaskType;
  depends_on: string[];
  max_retries: number | null; // u32 maps to number
  condition: boolean;
  description: string | null;
  result?: AssertionResult;
}

/**
 * Represents a node in the execution graph.
 */
export interface ExecutionNode {
  id: string;
  stage: number; // Rust usize -> TS number
  parents: string[];
  children: string[];
}

/**
 * The DAG (Directed Acyclic Graph) structure of the evaluation.
 */
export interface ExecutionPlan {
  stages: string[][]; // Vec<Vec<String>>
  nodes: Record<string, ExecutionNode>; // HashMap<String, ExecutionNode>
}

/**
 * Individual workflow result mapping to the GenAIEvalWorkflowResult struct.
 */
export interface GenAIEvalWorkflowResult {
  id: number; // i64
  record_uid: string;
  entity_id: number;
  entity_uid: string;
  created_at: string; // ISO-8601 String from DateTime<Utc>
  total_tasks: number;
  passed_tasks: number;
  failed_tasks: number;
  pass_rate: number; // f64
  duration_ms: number; // i64
  execution_plan: ExecutionPlan;
}

/**
 * Maps to GenAIEvalTaskResult struct.
 * Note: entity_id is included here for TS safety even if not exposed to Python.
 */
export interface GenAIEvalTaskResult {
  created_at: string; // ISO-8601
  start_time: string; // ISO-8601
  end_time: string; // ISO-8601
  record_uid: string;
  entity_id: number; // i32
  task_id: string;
  task_type: EvaluationTaskType;
  passed: boolean;
  value: number; // f64
  field_path: string | null;
  operator: ComparisonOperator;
  expected: JsonValue;
  actual: JsonValue;
  message: string;
  entity_uid: string;
  condition: boolean;
  stage: number; // i32
}
