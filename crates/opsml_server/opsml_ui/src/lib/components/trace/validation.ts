import type { FilterClause } from "./clause";
import type { TraceFilters, TraceMetricsRequest } from "./types";

/**
 * Runtime safety limits for user-submitted trace filters.
 *
 * The TypeScript `FilterClause` union keeps authored UI code honest, but these
 * SvelteKit endpoints also accept arbitrary JSON from authenticated users. The
 * caps below keep recursive clause evaluation and proxy payloads bounded before
 * a request reaches dev mocks or the Scouter backend.
 */
const MAX_CLAUSE_DEPTH = 8;
const MAX_CLAUSE_LEAVES = 64;
const MAX_FILTER_STRING_LENGTH = 512;
const MAX_ATTR_KEY_LENGTH = 256;
const MAX_TRACE_IDS = 100;
const MAX_TRACE_LIMIT = 500;
const MAX_RANGE_MS = 90 * 24 * 60 * 60 * 1000;

type ValidationResult<T> =
  | { ok: true; value: T }
  | { ok: false; error: string };

const TRACE_FILTER_KEYS = new Set([
  "clause",
  "start_time",
  "end_time",
  "limit",
  "cursor_start_time",
  "cursor_trace_id",
  "direction",
  "trace_ids",
  "entity_uid",
]);

const TRACE_METRICS_KEYS = new Set([
  "clause",
  "start_time",
  "end_time",
  "bucket_interval",
  "entity_uid",
]);

/** Returns true when a JSON value is an object that can carry request fields. */
function isPlainObject(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

/** Lists request keys that are not part of the accepted contract. */
function unknownKeys(
  value: Record<string, unknown>,
  allowed: Set<string>,
): string[] {
  return Object.keys(value).filter((key) => !allowed.has(key));
}

/** Validates bounded non-empty string fields used by trace filters. */
function validateString(
  value: unknown,
  field: string,
  maxLength = MAX_FILTER_STRING_LENGTH,
): string | undefined {
  if (typeof value !== "string") return `${field} must be a string`;
  if (value.length === 0) return `${field} must not be empty`;
  if (value.length > maxLength) return `${field} is too long`;
}

/** Validates a string field that must parse as a date. */
function validateDateString(value: unknown, field: string): string | undefined {
  const stringError = validateString(value, field);
  if (stringError) return stringError;
  if (Number.isNaN(Date.parse(value as string))) return `${field} must be a valid date`;
}

/** Validates optional start/end bounds and prevents overly broad trace queries. */
function validateTimeRange(value: Record<string, unknown>): string | undefined {
  if (value.start_time !== undefined) {
    const error = validateDateString(value.start_time, "start_time");
    if (error) return error;
  }
  if (value.end_time !== undefined) {
    const error = validateDateString(value.end_time, "end_time");
    if (error) return error;
  }
  if (value.start_time === undefined || value.end_time === undefined) return;

  const start = Date.parse(value.start_time as string);
  const end = Date.parse(value.end_time as string);
  if (start > end) return "start_time must be before end_time";
  if (end - start > MAX_RANGE_MS) return "time range is too large";
}

/** Validates the server-side page size cap for trace list requests. */
function validateLimit(value: unknown): string | undefined {
  if (typeof value !== "number" || !Number.isInteger(value)) {
    return "limit must be an integer";
  }
  if (value < 1 || value > MAX_TRACE_LIMIT) {
    return `limit must be between 1 and ${MAX_TRACE_LIMIT}`;
  }
}

/** Validates explicit trace-id filters without allowing unbounded arrays. */
function validateTraceIds(value: unknown): string | undefined {
  if (!Array.isArray(value)) return "trace_ids must be an array";
  if (value.length > MAX_TRACE_IDS) return "trace_ids has too many values";
  for (const [index, traceId] of value.entries()) {
    const error = validateString(traceId, `trace_ids[${index}]`);
    if (error) return error;
  }
}

/** Validates clause leaves whose payload is a single string value. */
function validateLeafString(
  clause: Record<string, unknown>,
  op: string,
): string | undefined {
  return validateString(clause.value, `${op}.value`);
}

/**
 * Validates the recursive `FilterClause` discriminated-union shape.
 *
 * The validator intentionally rejects unknown keys so a legacy scalar filter or
 * typo does not silently pass through the UI proxy with unclear backend
 * behavior.
 */
function validateClauseNode(
  clause: unknown,
  depth: number,
  leafCount: { value: number },
): string | undefined {
  if (!isPlainObject(clause)) return "clause must be an object";
  if (depth > MAX_CLAUSE_DEPTH) return "clause is too deeply nested";

  const keys = unknownKeys(clause, new Set(["op", "value"]));
  if (keys.length > 0) return `clause contains unknown field: ${keys[0]}`;

  if (typeof clause.op !== "string") return "clause.op must be a string";

  switch (clause.op) {
    case "and":
    case "or": {
      if (!Array.isArray(clause.value)) return `${clause.op}.value must be an array`;
      if (clause.value.length === 0) return `${clause.op}.value must not be empty`;
      for (const child of clause.value) {
        const error = validateClauseNode(child, depth + 1, leafCount);
        if (error) return error;
      }
      return;
    }
    case "not":
      return validateClauseNode(clause.value, depth + 1, leafCount);
    case "phrase":
    case "service":
    case "service_namespace":
    case "service_version":
    case "service_instance_id":
      leafCount.value += 1;
      if (leafCount.value > MAX_CLAUSE_LEAVES) return "clause has too many leaves";
      return validateLeafString(clause, clause.op);
    case "status_code":
      leafCount.value += 1;
      if (leafCount.value > MAX_CLAUSE_LEAVES) return "clause has too many leaves";
      if (typeof clause.value !== "number" || !Number.isInteger(clause.value)) {
        return "status_code.value must be an integer";
      }
      return;
    case "has_errors":
      leafCount.value += 1;
      if (leafCount.value > MAX_CLAUSE_LEAVES) return "clause has too many leaves";
      if (typeof clause.value !== "boolean") return "has_errors.value must be a boolean";
      return;
    case "duration_min_ms":
    case "duration_max_ms":
      leafCount.value += 1;
      if (leafCount.value > MAX_CLAUSE_LEAVES) return "clause has too many leaves";
      if (typeof clause.value !== "number" || !Number.isInteger(clause.value) || clause.value < 0) {
        return `${clause.op}.value must be a non-negative integer`;
      }
      return;
    case "attr": {
      leafCount.value += 1;
      if (leafCount.value > MAX_CLAUSE_LEAVES) return "clause has too many leaves";
      if (!isPlainObject(clause.value)) return "attr.value must be an object";
      const attrKeys = unknownKeys(clause.value, new Set(["key", "value"]));
      if (attrKeys.length > 0) return `attr.value contains unknown field: ${attrKeys[0]}`;
      return (
        validateString(clause.value.key, "attr.key", MAX_ATTR_KEY_LENGTH) ??
        validateString(clause.value.value, "attr.value")
      );
    }
    default:
      return `unsupported clause op: ${clause.op}`;
  }
}

/** Starts recursive clause validation with a fresh leaf counter. */
function validateClause(value: unknown): string | undefined {
  return validateClauseNode(value, 1, { value: 0 });
}

/** Validates fields shared by trace page, facet, and metrics requests. */
function validateTraceFilterFields(
  body: Record<string, unknown>,
  allowedKeys: Set<string>,
): string | undefined {
  const extraKeys = unknownKeys(body, allowedKeys);
  if (extraKeys.length > 0) return `unknown field: ${extraKeys[0]}`;

  if (body.clause !== undefined) {
    const error = validateClause(body.clause);
    if (error) return error;
  }
  if (body.limit !== undefined) {
    const error = validateLimit(body.limit);
    if (error) return error;
  }
  if (body.cursor_start_time !== undefined) {
    const error = validateDateString(body.cursor_start_time, "cursor_start_time");
    if (error) return error;
  }
  if (body.cursor_trace_id !== undefined) {
    const error = validateString(body.cursor_trace_id, "cursor_trace_id");
    if (error) return error;
  }
  if (body.direction !== undefined && body.direction !== "next" && body.direction !== "previous") {
    return "direction must be next or previous";
  }
  if (body.trace_ids !== undefined) {
    const error = validateTraceIds(body.trace_ids);
    if (error) return error;
  }
  if (body.entity_uid !== undefined) {
    const error = validateString(body.entity_uid, "entity_uid");
    if (error) return error;
  }

  return validateTimeRange(body);
}

/**
 * Validate a trace page/facet request body before mock evaluation or proxying.
 *
 * Returns the original body typed as `TraceFilters` only after checking the
 * runtime JSON shape, supported clause ops, pagination fields, and optional
 * time range.
 */
export function validateTraceFilters(body: unknown): ValidationResult<TraceFilters> {
  if (!isPlainObject(body)) return { ok: false, error: "request body must be an object" };
  const error = validateTraceFilterFields(body, TRACE_FILTER_KEYS);
  if (error) return { ok: false, error };
  return { ok: true, value: body as TraceFilters };
}

/**
 * Validate a trace metrics request body.
 *
 * Metrics always require `start_time` and `end_time`; otherwise this applies the
 * same clause and common field validation as `validateTraceFilters`.
 */
export function validateTraceMetricsRequest(
  body: unknown,
): ValidationResult<TraceMetricsRequest> {
  if (!isPlainObject(body)) return { ok: false, error: "request body must be an object" };
  const error = validateTraceFilterFields(body, TRACE_METRICS_KEYS);
  if (error) return { ok: false, error };
  if (!body.start_time || !body.end_time) {
    return { ok: false, error: "start_time and end_time are required" };
  }
  if (body.bucket_interval !== undefined) {
    const intervalError = validateString(body.bucket_interval, "bucket_interval", 64);
    if (intervalError) return { ok: false, error: intervalError };
  }
  return { ok: true, value: body as unknown as TraceMetricsRequest };
}

export type { FilterClause };
