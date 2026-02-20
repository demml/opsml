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
  | "HumanValidation"
  | "TraceAssertion";

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
 * Assertion target that can be either a field path or trace assertion.
 */
export type Assertion =
  | { FieldPath: string | null }
  | { TraceAssertion: TraceAssertion };

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
  assertion: Assertion;
  operator: ComparisonOperator;
  expected: JsonValue;
  actual: JsonValue;
  message: string;
  entity_uid: string;
  condition: boolean;
  stage: number; // i32
}

/**
 * Extract assertion from GenAIEvalTaskResult.
 * Returns field_path for standard assertions, TraceAssertion for trace tasks.
 */
export function getAssertion(
  result: GenAIEvalTaskResult,
): string | null | TraceAssertion {
  if ("FieldPath" in result.assertion) {
    return result.assertion.FieldPath;
  }
  if ("TraceAssertion" in result.assertion) {
    return result.assertion.TraceAssertion;
  }
  throw new Error("Invalid Assertion variant");
}

/**
 * Aggregation operations for span attribute values.
 */
export type AggregationType =
  | "Count"
  | "Sum"
  | "Average"
  | "Min"
  | "Max"
  | "First"
  | "Last";

/**
 * Filter configuration for selecting spans within a trace.
 */
export type SpanFilter =
  | { ByName: { name: string } }
  | { ByNamePattern: { pattern: string } }
  | { WithAttribute: { key: string } }
  | { WithAttributeValue: { key: string; value: JsonValue } }
  | { WithStatus: { status: string } }
  | { WithDuration: { min_ms?: number; max_ms?: number } }
  | { Sequence: { names: string[] } }
  | { And: { filters: SpanFilter[] } }
  | { Or: { filters: SpanFilter[] } };

/**
 * Unified assertion target for trace-level and span-level checks.
 */
export type TraceAssertion =
  | { SpanSequence: { span_names: string[] } }
  | { SpanSet: { span_names: string[] } }
  | { SpanCount: { filter: SpanFilter } }
  | { SpanExists: { filter: SpanFilter } }
  | { SpanAttribute: { filter: SpanFilter; attribute_key: string } }
  | { SpanDuration: { filter: SpanFilter } }
  | {
      SpanAggregation: {
        filter: SpanFilter;
        attribute_key: string;
        aggregation: AggregationType;
      };
    }
  | { TraceDuration: {} }
  | { TraceSpanCount: {} }
  | { TraceErrorCount: {} }
  | { TraceServiceCount: {} }
  | { TraceMaxDepth: {} }
  | { TraceAttribute: { attribute_key: string } };

/**
 * Assertion task for distributed trace validation.
 */
export interface TraceAssertionTask {
  id: string;
  assertion: TraceAssertion;
  operator: ComparisonOperator;
  expected_value: JsonValue;
  description: string | null;
  depends_on: string[];
  task_type: EvaluationTaskType;
  result?: AssertionResult;
  condition: boolean;
}
