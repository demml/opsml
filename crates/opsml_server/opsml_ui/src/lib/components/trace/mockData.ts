/**
 * Mock trace, span, and metric data for UI development.
 * Spans are built first; trace list items are derived from them so counts always match.
 */

import type {
  TraceListItem,
  TraceSpan,
  TraceMetricBucket,
  TracePaginationResponse,
  TraceSpansResponse,
  TraceMetricsResponse,
  TraceFilters,
  TraceMetricsRequest,
  TraceRequest,
  Attribute,
} from "$lib/components/trace/types";

// ── Helpers ──────────────────────────────────────────────────────────────

let _counter = 0;
function sid(): string {
  _counter++;
  return _counter.toString(16).padStart(16, "0");
}
function tid(): string {
  _counter++;
  return _counter.toString(16).padStart(32, "0");
}
function ts(baseMs: number, offsetMs: number = 0): string {
  return new Date(baseMs + offsetMs).toISOString();
}

function span(
  overrides: Partial<TraceSpan> & Pick<TraceSpan, "trace_id" | "span_id" | "span_name" | "start_time" | "service_name" | "root_span_id">,
): TraceSpan {
  const dur = overrides.duration_ms ?? 100;
  const startMs = new Date(overrides.start_time).getTime();
  return {
    parent_span_id: null,
    span_kind: "INTERNAL",
    end_time: ts(startMs, dur),
    duration_ms: dur,
    status_code: 1,
    status_message: null,
    attributes: [],
    events: [],
    links: [],
    depth: 0,
    path: [],
    span_order: 0,
    input: null,
    output: null,
    ...overrides,
  };
}

// ── Stable base time (10 minutes ago) ────────────────────────────────────
const NOW = Date.now();

// ── Trace 0: inference-api POST /predict (success, 5 spans, depth 3) ─────
function buildTrace0() {
  const traceId = tid();
  const base = NOW - 1 * 60_000;
  const root = sid();
  const preId = sid();
  const infId = sid();
  const loadId = sid(); // depth 2 under model.predict
  const postId = sid();

  return [
    span({ trace_id: traceId, span_id: root, span_name: "POST /predict", span_kind: "SERVER", start_time: ts(base), duration_ms: 342, root_span_id: root, service_name: "inference-api",
      attributes: [{ key: "http.method", value: "POST" }, { key: "http.route", value: "/predict" }, { key: "http.status_code", value: 200 }, { key: "model.name", value: "fraud-detector-v3" }, { key: "card.model.uid", value: "mdl_8f2a3c91" }],
    }),
    span({ trace_id: traceId, span_id: preId, parent_span_id: root, span_name: "preprocess_input", start_time: ts(base, 5), duration_ms: 38, depth: 1, path: [root], root_span_id: root, span_order: 1, service_name: "inference-api",
      attributes: [{ key: "input.shape", value: "[1, 24]" }, { key: "preprocessing.steps", value: ["normalize", "encode", "impute"] }],
    }),
    span({ trace_id: traceId, span_id: infId, parent_span_id: root, span_name: "model.predict", start_time: ts(base, 50), duration_ms: 230, depth: 1, path: [root], root_span_id: root, span_order: 2, service_name: "inference-api",
      attributes: [{ key: "model.framework", value: "pytorch" }, { key: "model.version", value: "3.2.1" }, { key: "model.device", value: "cuda:0" }],
    }),
    span({ trace_id: traceId, span_id: loadId, parent_span_id: infId, span_name: "load_weights", span_kind: "INTERNAL", start_time: ts(base, 55), duration_ms: 45, depth: 2, path: [root, infId], root_span_id: root, span_order: 3, service_name: "inference-api",
      attributes: [{ key: "model.checkpoint", value: "s3://models/fraud-v3/weights.pt" }, { key: "cache.hit", value: true }],
    }),
    span({ trace_id: traceId, span_id: postId, parent_span_id: root, span_name: "postprocess_output", start_time: ts(base, 290), duration_ms: 42, depth: 1, path: [root], root_span_id: root, span_order: 4, service_name: "inference-api",
      attributes: [{ key: "output.classes", value: ["fraud", "legitimate"] }, { key: "output.confidence", value: 0.934 }],
    }),
  ];
}

// ── Trace 1: inference-api POST /predict (error, 4 spans, depth 3) ───────
function buildTrace1() {
  const traceId = tid();
  const base = NOW - 2 * 60_000;
  const root = sid();
  const preId = sid();
  const infId = sid();
  const allocId = sid(); // depth 2: CUDA alloc fails

  return [
    span({ trace_id: traceId, span_id: root, span_name: "POST /predict", span_kind: "SERVER", start_time: ts(base), duration_ms: 1287, status_code: 2, status_message: "Internal Server Error", root_span_id: root, service_name: "inference-api",
      attributes: [{ key: "http.method", value: "POST" }, { key: "http.route", value: "/predict" }, { key: "http.status_code", value: 500 }, { key: "model.name", value: "fraud-detector-v3" }],
    }),
    span({ trace_id: traceId, span_id: preId, parent_span_id: root, span_name: "preprocess_input", start_time: ts(base, 5), duration_ms: 42, depth: 1, path: [root], root_span_id: root, span_order: 1, service_name: "inference-api",
      attributes: [{ key: "input.shape", value: "[1, 24]" }],
    }),
    span({ trace_id: traceId, span_id: infId, parent_span_id: root, span_name: "model.predict", start_time: ts(base, 55), duration_ms: 1220, status_code: 2, status_message: "CUDA OOM", depth: 1, path: [root], root_span_id: root, span_order: 2, service_name: "inference-api",
      attributes: [{ key: "model.framework", value: "pytorch" }, { key: "model.device", value: "cuda:0" }],
    }),
    span({ trace_id: traceId, span_id: allocId, parent_span_id: infId, span_name: "cuda.alloc_tensor", start_time: ts(base, 60), duration_ms: 1200, status_code: 2, status_message: "CUDA out of memory", depth: 2, path: [root, infId], root_span_id: root, span_order: 3, service_name: "inference-api",
      attributes: [{ key: "cuda.requested_bytes", value: 2147483648 }, { key: "cuda.free_bytes", value: 536870912 }],
      events: [{
        timestamp: ts(base, 1260), name: "exception", dropped_attributes_count: 0,
        attributes: [
          { key: "exception.type", value: "RuntimeError" },
          { key: "exception.message", value: "CUDA out of memory. Tried to allocate 2.00 GiB" },
          { key: "exception.traceback", value: 'Traceback (most recent call last):\n  File "model.py", line 142, in predict\n    output = self.model(input_tensor)\n  File "torch/nn/modules/module.py", line 1501, in _call_impl\n    return forward_call(*input, **kwargs)\nRuntimeError: CUDA out of memory. Tried to allocate 2.00 GiB' },
        ],
      }],
    }),
  ];
}

// ── Trace 2: llm-gateway chat.completions (success, 7 spans, depth 4) ────
function buildTrace2() {
  const traceId = tid();
  const base = NOW - 3 * 60_000;
  const root = sid();
  const promptId = sid();
  const llmId = sid();
  const streamId = sid();  // depth 2 under llm.call
  const parseId = sid();   // depth 2 under llm.call
  const toolId = sid();
  const dbId = sid();      // depth 2 under tool

  return [
    span({ trace_id: traceId, span_id: root, span_name: "chat.completions", span_kind: "SERVER", start_time: ts(base), duration_ms: 2891, root_span_id: root, service_name: "llm-gateway",
      attributes: [{ key: "gen_ai.system", value: "anthropic" }, { key: "gen_ai.request.model", value: "claude-sonnet-4-20250514" }, { key: "gen_ai.usage.input_tokens", value: 1247 }, { key: "gen_ai.usage.output_tokens", value: 583 }, { key: "card.agent.uid", value: "agt_d4e7f012" }],
    }),
    span({ trace_id: traceId, span_id: promptId, parent_span_id: root, span_name: "build_prompt", start_time: ts(base, 5), duration_ms: 45, depth: 1, path: [root], root_span_id: root, span_order: 1, service_name: "llm-gateway",
      attributes: [{ key: "prompt.template", value: "fraud_analysis_v2" }, { key: "prompt.variables", value: 4 }],
      input: JSON.stringify({ template: "fraud_analysis_v2", variables: { account_id: "7842", window: "4m" } }),
    }),
    span({ trace_id: traceId, span_id: llmId, parent_span_id: root, span_name: "llm.call", span_kind: "CLIENT", start_time: ts(base, 55), duration_ms: 2100, depth: 1, path: [root], root_span_id: root, span_order: 2, service_name: "llm-gateway",
      attributes: [{ key: "gen_ai.request.model", value: "claude-sonnet-4-20250514" }, { key: "gen_ai.request.temperature", value: 0.7 }, { key: "gen_ai.request.max_tokens", value: 2048 }],
      input: JSON.stringify({ role: "user", content: "Analyze the following customer transaction data and identify anomalous patterns indicating fraud." }),
      output: JSON.stringify({ role: "assistant", content: "Based on the transaction data, I've identified 3 anomalous patterns:\n\n1. **Velocity spike**: 12 transactions in 4 minutes from account 7842\n2. **Geographic anomaly**: Card-present in Tokyo → online from São Paulo in 23 min\n3. **Amount deviation**: $4,892 at MCC 5944 — 8.3x 90-day average" }),
    }),
    span({ trace_id: traceId, span_id: streamId, parent_span_id: llmId, span_name: "http.stream_response", span_kind: "CLIENT", start_time: ts(base, 60), duration_ms: 2050, depth: 2, path: [root, llmId], root_span_id: root, span_order: 3, service_name: "llm-gateway",
      attributes: [{ key: "http.method", value: "POST" }, { key: "http.url", value: "https://api.anthropic.com/v1/messages" }, { key: "http.status_code", value: 200 }, { key: "stream.chunks", value: 47 }],
    }),
    span({ trace_id: traceId, span_id: parseId, parent_span_id: llmId, span_name: "parse_tool_calls", start_time: ts(base, 2120), duration_ms: 12, depth: 2, path: [root, llmId], root_span_id: root, span_order: 4, service_name: "llm-gateway",
      attributes: [{ key: "tool_calls.count", value: 1 }, { key: "tool_calls.names", value: ["search_knowledge_base"] }],
    }),
    span({ trace_id: traceId, span_id: toolId, parent_span_id: root, span_name: "tool.search_knowledge_base", start_time: ts(base, 2200), duration_ms: 620, depth: 1, path: [root], root_span_id: root, span_order: 5, service_name: "llm-gateway",
      attributes: [{ key: "tool.name", value: "search_knowledge_base" }, { key: "tool.result_count", value: 7 }],
      input: JSON.stringify({ query: "fraud detection patterns for velocity anomalies", top_k: 10 }),
      output: JSON.stringify({ results: 7, relevance_scores: [0.94, 0.91, 0.87, 0.82, 0.79, 0.71, 0.68] }),
    }),
    span({ trace_id: traceId, span_id: dbId, parent_span_id: toolId, span_name: "pg.query", span_kind: "CLIENT", start_time: ts(base, 2210), duration_ms: 580, depth: 2, path: [root, toolId], root_span_id: root, span_order: 6, service_name: "llm-gateway",
      attributes: [{ key: "db.system", value: "postgresql" }, { key: "db.statement", value: "SELECT id, content, embedding <=> $1 AS score FROM knowledge_base ORDER BY score LIMIT $2" }, { key: "db.rows_returned", value: 7 }],
    }),
  ];
}

// ── Trace 3: data-pipeline ingest (success, 8 spans, depth 3) ────────────
function buildTrace3() {
  const traceId = tid();
  const base = NOW - 4 * 60_000;
  const root = sid();
  const readId = sid();
  const s3Id = sid();      // depth 2: s3 download
  const valId = sid();
  const featId = sid();
  const normId = sid();    // depth 2: normalize step
  const encId = sid();     // depth 2: encode step
  const writeId = sid();

  return [
    span({ trace_id: traceId, span_id: root, span_name: "ingest_daily_features", span_kind: "SERVER", start_time: ts(base), duration_ms: 14520, root_span_id: root, service_name: "data-pipeline",
      attributes: [{ key: "pipeline.name", value: "daily-feature-ingest" }, { key: "pipeline.records", value: 284319 }, { key: "card.data.uid", value: "dat_a1b2c3d4" }],
    }),
    span({ trace_id: traceId, span_id: readId, parent_span_id: root, span_name: "read_source", start_time: ts(base, 10), duration_ms: 3200, depth: 1, path: [root], root_span_id: root, span_order: 1, service_name: "data-pipeline",
      attributes: [{ key: "source.type", value: "s3" }, { key: "source.format", value: "parquet" }, { key: "source.files", value: 12 }],
    }),
    span({ trace_id: traceId, span_id: s3Id, parent_span_id: readId, span_name: "s3.get_objects", span_kind: "CLIENT", start_time: ts(base, 20), duration_ms: 3100, depth: 2, path: [root, readId], root_span_id: root, span_order: 2, service_name: "data-pipeline",
      attributes: [{ key: "aws.s3.bucket", value: "opsml-features" }, { key: "aws.s3.prefix", value: "daily/2026-03-20/" }, { key: "http.method", value: "GET" }, { key: "bytes.downloaded", value: 847_291_456 }],
    }),
    span({ trace_id: traceId, span_id: valId, parent_span_id: root, span_name: "validate_schema", start_time: ts(base, 3300), duration_ms: 1200, depth: 1, path: [root], root_span_id: root, span_order: 3, service_name: "data-pipeline",
      attributes: [{ key: "schema.columns", value: 42 }, { key: "schema.violations", value: 0 }],
    }),
    span({ trace_id: traceId, span_id: featId, parent_span_id: root, span_name: "compute_features", start_time: ts(base, 4600), duration_ms: 7200, depth: 1, path: [root], root_span_id: root, span_order: 4, service_name: "data-pipeline",
      attributes: [{ key: "features.input_cols", value: 42 }, { key: "features.output_cols", value: 128 }, { key: "features.engine", value: "polars" }],
    }),
    span({ trace_id: traceId, span_id: normId, parent_span_id: featId, span_name: "normalize_numerics", start_time: ts(base, 4700), duration_ms: 3100, depth: 2, path: [root, featId], root_span_id: root, span_order: 5, service_name: "data-pipeline",
      attributes: [{ key: "normalize.method", value: "z-score" }, { key: "normalize.columns", value: 18 }],
    }),
    span({ trace_id: traceId, span_id: encId, parent_span_id: featId, span_name: "encode_categoricals", start_time: ts(base, 7900), duration_ms: 3800, depth: 2, path: [root, featId], root_span_id: root, span_order: 6, service_name: "data-pipeline",
      attributes: [{ key: "encode.method", value: "target_encoding" }, { key: "encode.columns", value: 24 }, { key: "encode.cardinality_max", value: 1847 }],
    }),
    span({ trace_id: traceId, span_id: writeId, parent_span_id: root, span_name: "write_feature_store", span_kind: "CLIENT", start_time: ts(base, 12000), duration_ms: 2400, depth: 1, path: [root], root_span_id: root, span_order: 7, service_name: "data-pipeline",
      attributes: [{ key: "store.type", value: "delta_lake" }, { key: "store.table", value: "features.fraud_detection" }, { key: "store.rows_written", value: 284319 }, { key: "store.partitions", value: 4 }],
    }),
  ];
}

// ── Trace 4: llm-gateway chat.completions (error, 5 spans, depth 2) ──────
function buildTrace4() {
  const traceId = tid();
  const base = NOW - 5 * 60_000;
  const root = sid();
  const promptId = sid();
  const call1 = sid();
  const retry1 = sid();
  const retry2 = sid();

  return [
    span({ trace_id: traceId, span_id: root, span_name: "chat.completions", span_kind: "SERVER", start_time: ts(base), duration_ms: 8432, status_code: 2, status_message: "Rate limit exceeded after retries", root_span_id: root, service_name: "llm-gateway",
      attributes: [{ key: "gen_ai.system", value: "openai" }, { key: "gen_ai.request.model", value: "gpt-4o" }, { key: "gen_ai.usage.input_tokens", value: 3891 }, { key: "gen_ai.usage.output_tokens", value: 0 }, { key: "error.type", value: "RateLimitError" }],
    }),
    span({ trace_id: traceId, span_id: promptId, parent_span_id: root, span_name: "build_prompt", start_time: ts(base, 5), duration_ms: 30, depth: 1, path: [root], root_span_id: root, span_order: 1, service_name: "llm-gateway",
      attributes: [{ key: "prompt.template", value: "analysis_v1" }, { key: "prompt.token_count", value: 3891 }],
    }),
    span({ trace_id: traceId, span_id: call1, parent_span_id: root, span_name: "llm.call", span_kind: "CLIENT", start_time: ts(base, 40), duration_ms: 2800, status_code: 2, status_message: "429 Too Many Requests", depth: 1, path: [root], root_span_id: root, span_order: 2, service_name: "llm-gateway",
      attributes: [{ key: "http.status_code", value: 429 }, { key: "retry.after_seconds", value: 32 }],
      events: [{ timestamp: ts(base, 2840), name: "exception", dropped_attributes_count: 0, attributes: [
        { key: "exception.type", value: "RateLimitError" },
        { key: "exception.message", value: "Rate limit exceeded: 429 Too Many Requests. Retry after 32s." },
      ]}],
    }),
    span({ trace_id: traceId, span_id: retry1, parent_span_id: root, span_name: "llm.call (retry 1)", span_kind: "CLIENT", start_time: ts(base, 3000), duration_ms: 2600, status_code: 2, status_message: "429 Too Many Requests", depth: 1, path: [root], root_span_id: root, span_order: 3, service_name: "llm-gateway",
      attributes: [{ key: "retry.attempt", value: 1 }, { key: "http.status_code", value: 429 }],
    }),
    span({ trace_id: traceId, span_id: retry2, parent_span_id: root, span_name: "llm.call (retry 2)", span_kind: "CLIENT", start_time: ts(base, 5800), duration_ms: 2500, status_code: 2, status_message: "429 Too Many Requests", depth: 1, path: [root], root_span_id: root, span_order: 4, service_name: "llm-gateway",
      attributes: [{ key: "retry.attempt", value: 2 }, { key: "http.status_code", value: 429 }],
    }),
  ];
}

// ── Trace 5: inference-api POST /predict/batch (success, 7 spans, depth 3) ─
function buildTrace5() {
  const traceId = tid();
  const base = NOW - 6 * 60_000;
  const root = sid();
  const decodeId = sid();
  const batchId = sid();
  const chunk1 = sid();    // depth 2 under batch
  const chunk2 = sid();    // depth 2 under batch
  const mergeId = sid();
  const cacheId = sid();

  return [
    span({ trace_id: traceId, span_id: root, span_name: "POST /predict/batch", span_kind: "SERVER", start_time: ts(base), duration_ms: 4215, root_span_id: root, service_name: "inference-api",
      attributes: [{ key: "http.method", value: "POST" }, { key: "http.route", value: "/predict/batch" }, { key: "batch.size", value: 128 }, { key: "model.name", value: "churn-predictor-v2" }, { key: "card.model.uid", value: "mdl_7e1b5a44" }],
    }),
    span({ trace_id: traceId, span_id: decodeId, parent_span_id: root, span_name: "decode_batch_request", start_time: ts(base, 5), duration_ms: 85, depth: 1, path: [root], root_span_id: root, span_order: 1, service_name: "inference-api",
      attributes: [{ key: "batch.format", value: "json_array" }, { key: "batch.items", value: 128 }],
    }),
    span({ trace_id: traceId, span_id: batchId, parent_span_id: root, span_name: "model.predict_batch", start_time: ts(base, 100), duration_ms: 3600, depth: 1, path: [root], root_span_id: root, span_order: 2, service_name: "inference-api",
      attributes: [{ key: "model.framework", value: "xgboost" }, { key: "model.version", value: "2.1.0" }, { key: "batch.chunk_size", value: 64 }],
    }),
    span({ trace_id: traceId, span_id: chunk1, parent_span_id: batchId, span_name: "predict_chunk[0:64]", start_time: ts(base, 110), duration_ms: 1700, depth: 2, path: [root, batchId], root_span_id: root, span_order: 3, service_name: "inference-api",
      attributes: [{ key: "chunk.offset", value: 0 }, { key: "chunk.size", value: 64 }],
    }),
    span({ trace_id: traceId, span_id: chunk2, parent_span_id: batchId, span_name: "predict_chunk[64:128]", start_time: ts(base, 1820), duration_ms: 1850, depth: 2, path: [root, batchId], root_span_id: root, span_order: 4, service_name: "inference-api",
      attributes: [{ key: "chunk.offset", value: 64 }, { key: "chunk.size", value: 64 }],
    }),
    span({ trace_id: traceId, span_id: mergeId, parent_span_id: root, span_name: "merge_results", start_time: ts(base, 3710), duration_ms: 120, depth: 1, path: [root], root_span_id: root, span_order: 5, service_name: "inference-api",
      attributes: [{ key: "results.count", value: 128 }, { key: "results.format", value: "json_array" }],
    }),
    span({ trace_id: traceId, span_id: cacheId, parent_span_id: root, span_name: "cache.set_batch", span_kind: "CLIENT", start_time: ts(base, 3840), duration_ms: 350, depth: 1, path: [root], root_span_id: root, span_order: 6, service_name: "inference-api",
      attributes: [{ key: "cache.backend", value: "redis" }, { key: "cache.keys", value: 128 }, { key: "cache.ttl_seconds", value: 300 }],
    }),
  ];
}

// ── Trace 6: monitoring-agent run_drift_check (success, 4 spans, depth 2) ─
function buildTrace6() {
  const traceId = tid();
  const base = NOW - 7 * 60_000;
  const root = sid();
  const fetchId = sid();
  const dbId = sid();      // depth 2: actual DB query
  const calcId = sid();

  return [
    span({ trace_id: traceId, span_id: root, span_name: "run_drift_check", span_kind: "SERVER", start_time: ts(base), duration_ms: 987, root_span_id: root, service_name: "monitoring-agent",
      attributes: [{ key: "scouter.entity", value: "fraud-detector-v3" }, { key: "drift.method", value: "psi" }, { key: "drift.score", value: 0.042 }, { key: "drift.threshold", value: 0.1 }],
    }),
    span({ trace_id: traceId, span_id: fetchId, parent_span_id: root, span_name: "fetch_reference_data", span_kind: "CLIENT", start_time: ts(base, 5), duration_ms: 420, depth: 1, path: [root], root_span_id: root, span_order: 1, service_name: "monitoring-agent",
      attributes: [{ key: "reference.source", value: "feature_store" }, { key: "reference.rows", value: 5000 }],
    }),
    span({ trace_id: traceId, span_id: dbId, parent_span_id: fetchId, span_name: "pg.query", span_kind: "CLIENT", start_time: ts(base, 10), duration_ms: 390, depth: 2, path: [root, fetchId], root_span_id: root, span_order: 2, service_name: "monitoring-agent",
      attributes: [{ key: "db.system", value: "postgresql" }, { key: "db.operation", value: "SELECT" }, { key: "db.statement", value: "SELECT * FROM reference_distributions WHERE entity = $1 LIMIT 5000" }, { key: "db.rows_returned", value: 5000 }],
    }),
    span({ trace_id: traceId, span_id: calcId, parent_span_id: root, span_name: "compute_drift_score", start_time: ts(base, 440), duration_ms: 520, depth: 1, path: [root], root_span_id: root, span_order: 3, service_name: "monitoring-agent",
      attributes: [{ key: "drift.method", value: "psi" }, { key: "drift.score", value: 0.042 }, { key: "drift.features_analyzed", value: 24 }, { key: "drift.passed", value: true }],
    }),
  ];
}

// ── Trace 7: inference-api GET /health (2 spans) ─────────────────────────
function buildTrace7() {
  const traceId = tid();
  const base = NOW - 8 * 60_000;
  const root = sid();
  const dbCheck = sid();

  return [
    span({ trace_id: traceId, span_id: root, span_name: "GET /health", span_kind: "SERVER", start_time: ts(base), duration_ms: 12, root_span_id: root, service_name: "inference-api",
      attributes: [{ key: "http.method", value: "GET" }, { key: "http.route", value: "/health" }, { key: "http.status_code", value: 200 }],
    }),
    span({ trace_id: traceId, span_id: dbCheck, parent_span_id: root, span_name: "db.ping", span_kind: "CLIENT", start_time: ts(base, 2), duration_ms: 8, depth: 1, path: [root], root_span_id: root, span_order: 1, service_name: "inference-api",
      attributes: [{ key: "db.system", value: "postgresql" }, { key: "db.operation", value: "SELECT 1" }],
    }),
  ];
}

// ── Trace 8: llm-gateway tool.execute (success, 6 spans, depth 3) ────────
function buildTrace8() {
  const traceId = tid();
  const base = NOW - 9 * 60_000;
  const root = sid();
  const resolveId = sid();
  const execId = sid();
  const dbId = sid();      // depth 2 under exec
  const rankId = sid();    // depth 2 under exec
  const formatId = sid();

  return [
    span({ trace_id: traceId, span_id: root, span_name: "tool.execute", span_kind: "SERVER", start_time: ts(base), duration_ms: 1543, root_span_id: root, service_name: "llm-gateway",
      attributes: [{ key: "gen_ai.system", value: "anthropic" }, { key: "tool.name", value: "search_knowledge_base" }, { key: "tool.result_count", value: 7 }, { key: "card.agent.uid", value: "agt_d4e7f012" }],
    }),
    span({ trace_id: traceId, span_id: resolveId, parent_span_id: root, span_name: "resolve_tool", start_time: ts(base, 3), duration_ms: 15, depth: 1, path: [root], root_span_id: root, span_order: 1, service_name: "llm-gateway",
      attributes: [{ key: "tool.registry", value: "agent_tools" }, { key: "tool.name", value: "search_knowledge_base" }],
    }),
    span({ trace_id: traceId, span_id: execId, parent_span_id: root, span_name: "tool.search_knowledge_base", start_time: ts(base, 25), duration_ms: 1400, depth: 1, path: [root], root_span_id: root, span_order: 2, service_name: "llm-gateway",
      input: JSON.stringify({ query: "fraud detection velocity patterns", top_k: 10 }),
      output: JSON.stringify({ results: 7, relevance_scores: [0.94, 0.91, 0.87, 0.82, 0.79, 0.71, 0.68] }),
      attributes: [{ key: "tool.name", value: "search_knowledge_base" }],
    }),
    span({ trace_id: traceId, span_id: dbId, parent_span_id: execId, span_name: "pg.vector_search", span_kind: "CLIENT", start_time: ts(base, 30), duration_ms: 980, depth: 2, path: [root, execId], root_span_id: root, span_order: 3, service_name: "llm-gateway",
      attributes: [{ key: "db.system", value: "postgresql" }, { key: "db.statement", value: "SELECT id, content, embedding <=> $1 AS dist FROM kb ORDER BY dist LIMIT $2" }, { key: "db.rows_returned", value: 10 }],
    }),
    span({ trace_id: traceId, span_id: rankId, parent_span_id: execId, span_name: "rerank_results", start_time: ts(base, 1020), duration_ms: 380, depth: 2, path: [root, execId], root_span_id: root, span_order: 4, service_name: "llm-gateway",
      attributes: [{ key: "rerank.model", value: "cross-encoder-v2" }, { key: "rerank.input_count", value: 10 }, { key: "rerank.output_count", value: 7 }, { key: "rerank.threshold", value: 0.65 }],
    }),
    span({ trace_id: traceId, span_id: formatId, parent_span_id: root, span_name: "format_tool_response", start_time: ts(base, 1440), duration_ms: 80, depth: 1, path: [root], root_span_id: root, span_order: 5, service_name: "llm-gateway",
      attributes: [{ key: "format.type", value: "json" }, { key: "format.truncated", value: false }],
    }),
  ];
}

// ── Trace 9: data-pipeline validate_schema (error, 5 spans, depth 3) ─────
function buildTrace9() {
  const traceId = tid();
  const base = NOW - 10 * 60_000;
  const root = sid();
  const fetchId = sid();
  const colCheck = sid();
  const typeCheck = sid();  // depth 2 under colCheck
  const nullCheck = sid();  // depth 2 under colCheck

  return [
    span({ trace_id: traceId, span_id: root, span_name: "validate_schema", span_kind: "SERVER", start_time: ts(base), duration_ms: 356, status_code: 2, status_message: "3 validation errors", root_span_id: root, service_name: "data-pipeline",
      attributes: [{ key: "pipeline.name", value: "schema-validator" }, { key: "validation.errors", value: 3 }, { key: "card.data.uid", value: "dat_a1b2c3d4" }],
    }),
    span({ trace_id: traceId, span_id: fetchId, parent_span_id: root, span_name: "fetch_schema_definition", start_time: ts(base, 5), duration_ms: 45, depth: 1, path: [root], root_span_id: root, span_order: 1, service_name: "data-pipeline",
      attributes: [{ key: "schema.source", value: "registry" }, { key: "schema.version", value: "2.4.0" }],
    }),
    span({ trace_id: traceId, span_id: colCheck, parent_span_id: root, span_name: "check_columns", start_time: ts(base, 60), duration_ms: 280, status_code: 2, status_message: "Type mismatches found", depth: 1, path: [root], root_span_id: root, span_order: 2, service_name: "data-pipeline",
      attributes: [{ key: "columns.expected", value: 42 }, { key: "columns.found", value: 42 }, { key: "columns.type_errors", value: 2 }],
    }),
    span({ trace_id: traceId, span_id: typeCheck, parent_span_id: colCheck, span_name: "validate_column_types", start_time: ts(base, 65), duration_ms: 180, status_code: 2, status_message: "amount: expected float64 got string; timestamp: expected datetime got int64", depth: 2, path: [root, colCheck], root_span_id: root, span_order: 3, service_name: "data-pipeline",
      attributes: [{ key: "errors", value: [{ column: "amount", expected: "float64", actual: "string" }, { column: "timestamp", expected: "datetime", actual: "int64" }] }],
      events: [
        { timestamp: ts(base, 200), name: "validation_error", dropped_attributes_count: 0, attributes: [{ key: "column", value: "amount" }, { key: "expected_type", value: "float64" }, { key: "actual_type", value: "string" }, { key: "sample_value", value: "N/A" }] },
        { timestamp: ts(base, 210), name: "validation_error", dropped_attributes_count: 0, attributes: [{ key: "column", value: "timestamp" }, { key: "expected_type", value: "datetime" }, { key: "actual_type", value: "int64" }, { key: "sample_value", value: "1710979200" }] },
      ],
    }),
    span({ trace_id: traceId, span_id: nullCheck, parent_span_id: colCheck, span_name: "validate_null_constraints", start_time: ts(base, 250), duration_ms: 85, status_code: 2, depth: 2, path: [root, colCheck], root_span_id: root, span_order: 4, service_name: "data-pipeline",
      attributes: [{ key: "nullable_violations", value: 1 }, { key: "column", value: "customer_id" }, { key: "null_count", value: 47 }],
      events: [{ timestamp: ts(base, 330), name: "validation_error", dropped_attributes_count: 0, attributes: [{ key: "column", value: "customer_id" }, { key: "constraint", value: "NOT NULL" }, { key: "null_rows", value: 47 }] }],
    }),
  ];
}

// ── Trace 10: inference-api POST /predict (success, 5 spans, depth 3) ────
function buildTrace10() {
  const traceId = tid();
  const base = NOW - 11 * 60_000;
  const root = sid();
  const preId = sid();
  const infId = sid();
  const tokId = sid();     // depth 2: tokenize under model.predict
  const postId = sid();

  return [
    span({ trace_id: traceId, span_id: root, span_name: "POST /predict", span_kind: "SERVER", start_time: ts(base), duration_ms: 289, root_span_id: root, service_name: "inference-api",
      attributes: [{ key: "http.method", value: "POST" }, { key: "http.route", value: "/predict" }, { key: "http.status_code", value: 200 }, { key: "model.name", value: "sentiment-classifier" }, { key: "card.model.uid", value: "mdl_cc3d9102" }],
    }),
    span({ trace_id: traceId, span_id: preId, parent_span_id: root, span_name: "preprocess_input", start_time: ts(base, 3), duration_ms: 25, depth: 1, path: [root], root_span_id: root, span_order: 1, service_name: "inference-api",
      attributes: [{ key: "input.type", value: "text" }, { key: "input.length_chars", value: 342 }],
    }),
    span({ trace_id: traceId, span_id: infId, parent_span_id: root, span_name: "model.predict", start_time: ts(base, 32), duration_ms: 210, depth: 1, path: [root], root_span_id: root, span_order: 2, service_name: "inference-api",
      attributes: [{ key: "model.framework", value: "huggingface" }, { key: "model.name", value: "distilbert-sentiment" }],
    }),
    span({ trace_id: traceId, span_id: tokId, parent_span_id: infId, span_name: "tokenize", start_time: ts(base, 35), duration_ms: 18, depth: 2, path: [root, infId], root_span_id: root, span_order: 3, service_name: "inference-api",
      attributes: [{ key: "tokenizer", value: "distilbert-base-uncased" }, { key: "tokens", value: 64 }, { key: "truncated", value: false }],
    }),
    span({ trace_id: traceId, span_id: postId, parent_span_id: root, span_name: "postprocess_output", start_time: ts(base, 248), duration_ms: 35, depth: 1, path: [root], root_span_id: root, span_order: 4, service_name: "inference-api",
      attributes: [{ key: "output.label", value: "positive" }, { key: "output.confidence", value: 0.891 }],
    }),
  ];
}

// ── Trace 11: monitoring-agent drift check (error, 5 spans, depth 2) ─────
function buildTrace11() {
  const traceId = tid();
  const base = NOW - 12 * 60_000;
  const root = sid();
  const fetchId = sid();
  const dbId = sid();
  const calcId = sid();
  const alertId = sid();

  return [
    span({ trace_id: traceId, span_id: root, span_name: "run_drift_check", span_kind: "SERVER", start_time: ts(base), duration_ms: 2341, status_code: 2, status_message: "Drift threshold exceeded", root_span_id: root, service_name: "monitoring-agent",
      attributes: [{ key: "scouter.entity", value: "churn-predictor-v2" }, { key: "drift.method", value: "spc" }, { key: "drift.score", value: 0.187 }, { key: "drift.threshold", value: 0.1 }, { key: "drift.alert", value: true }],
    }),
    span({ trace_id: traceId, span_id: fetchId, parent_span_id: root, span_name: "fetch_reference_data", span_kind: "CLIENT", start_time: ts(base, 5), duration_ms: 480, depth: 1, path: [root], root_span_id: root, span_order: 1, service_name: "monitoring-agent",
      attributes: [{ key: "reference.source", value: "feature_store" }, { key: "reference.rows", value: 10000 }],
    }),
    span({ trace_id: traceId, span_id: dbId, parent_span_id: fetchId, span_name: "pg.query", span_kind: "CLIENT", start_time: ts(base, 10), duration_ms: 450, depth: 2, path: [root, fetchId], root_span_id: root, span_order: 2, service_name: "monitoring-agent",
      attributes: [{ key: "db.system", value: "postgresql" }, { key: "db.operation", value: "SELECT" }, { key: "db.rows_returned", value: 10000 }],
    }),
    span({ trace_id: traceId, span_id: calcId, parent_span_id: root, span_name: "compute_drift_score", start_time: ts(base, 500), duration_ms: 1600, status_code: 2, status_message: "Drift threshold exceeded", depth: 1, path: [root], root_span_id: root, span_order: 3, service_name: "monitoring-agent",
      attributes: [{ key: "drift.method", value: "spc" }, { key: "drift.score", value: 0.187 }, { key: "drift.features_analyzed", value: 24 }, { key: "drift.passed", value: false }],
      events: [{ timestamp: ts(base, 2100), name: "drift_alert", dropped_attributes_count: 0, attributes: [
        { key: "alert.severity", value: "high" },
        { key: "alert.message", value: "Feature drift detected above threshold (0.187 > 0.1)" },
        { key: "alert.features", value: ["transaction_amount", "merchant_category", "time_of_day"] },
      ]}],
    }),
    span({ trace_id: traceId, span_id: alertId, parent_span_id: root, span_name: "send_alert", span_kind: "CLIENT", start_time: ts(base, 2150), duration_ms: 160, depth: 1, path: [root], root_span_id: root, span_order: 4, service_name: "monitoring-agent",
      attributes: [{ key: "alert.channel", value: "slack" }, { key: "alert.destination", value: "#ml-alerts" }, { key: "http.method", value: "POST" }, { key: "http.status_code", value: 200 }],
    }),
  ];
}

// ── Assemble all traces ──────────────────────────────────────────────────

const ALL_BUILDERS = [
  buildTrace0, buildTrace1, buildTrace2, buildTrace3,
  buildTrace4, buildTrace5, buildTrace6, buildTrace7,
  buildTrace8, buildTrace9, buildTrace10, buildTrace11,
];

// Service/scope metadata for each trace (used for TraceListItem)
const TRACE_META: { service: string; scope: string }[] = [
  { service: "inference-api", scope: "http" },
  { service: "inference-api", scope: "http" },
  { service: "llm-gateway", scope: "genai" },
  { service: "data-pipeline", scope: "batch" },
  { service: "llm-gateway", scope: "genai" },
  { service: "inference-api", scope: "http" },
  { service: "monitoring-agent", scope: "drift" },
  { service: "inference-api", scope: "http" },
  { service: "llm-gateway", scope: "genai" },
  { service: "data-pipeline", scope: "batch" },
  { service: "inference-api", scope: "http" },
  { service: "monitoring-agent", scope: "drift" },
];

// Build all spans once at module load
const ALL_SPANS: TraceSpan[][] = ALL_BUILDERS.map((fn) => fn());

// Derive trace list items from actual spans (so counts always match)
function buildTraceListItems(): TraceListItem[] {
  // Shift all timestamps forward so traces always appear "just happened"
  // relative to the current wall-clock time, not the frozen module-load time.
  const offsetMs = Date.now() - NOW;
  return ALL_SPANS.map((spans, i) => {
    const root = spans[0];
    const errorSpans = spans.filter((s) => s.status_code === 2);
    const startMs = new Date(root.start_time).getTime() + offsetMs;
    const endMs = root.end_time ? new Date(root.end_time).getTime() + offsetMs : undefined;
    return {
      trace_id: root.trace_id,
      service_name: TRACE_META[i].service,
      scope: TRACE_META[i].scope,
      root_operation: root.span_name,
      start_time: new Date(startMs).toISOString(),
      end_time: endMs !== undefined ? new Date(endMs).toISOString() : root.end_time,
      duration_ms: root.duration_ms,
      status_code: root.status_code,
      status_message: root.status_message,
      span_count: spans.length,
      has_errors: errorSpans.length > 0,
      error_count: errorSpans.length,
      created_at: new Date(startMs).toISOString(),
      resource_attributes: root.attributes,
    };
  });
}

// Index spans by trace_id
const SPANS_BY_TRACE = new Map<string, TraceSpan[]>();
ALL_SPANS.forEach((spans) => {
  SPANS_BY_TRACE.set(spans[0].trace_id, spans);
});

// ── Build metric buckets ─────────────────────────────────────────────────

function buildMetricBuckets(
  startTime: string,
  endTime: string,
  bucketInterval: string,
): TraceMetricBucket[] {
  const start = new Date(startTime).getTime();
  const end = new Date(endTime).getTime();

  let intervalMs = 60_000;
  const match = bucketInterval.match(/(\d+)\s*(minute|hour|day|second)s?/i);
  if (match) {
    const n = parseInt(match[1]);
    const unit = match[2].toLowerCase();
    if (unit === "second") intervalMs = n * 1_000;
    else if (unit === "minute") intervalMs = n * 60_000;
    else if (unit === "hour") intervalMs = n * 3_600_000;
    else if (unit === "day") intervalMs = n * 86_400_000;
  }

  const buckets: TraceMetricBucket[] = [];
  let t = start;

  while (t < end) {
    const progress = (t - start) / (end - start);
    const noise = Math.sin(progress * 12) * 0.3 + Math.random() * 0.4;
    const baseCount = 8 + Math.floor(noise * 15);
    const baseAvg = 200 + noise * 400;
    const errorNoise = Math.max(0, Math.sin(progress * 8 + 1) * 0.08 + Math.random() * 0.05);

    buckets.push({
      bucket_start: new Date(t).toISOString(),
      trace_count: Math.max(1, baseCount),
      avg_duration_ms: Math.round(baseAvg),
      p50_duration_ms: Math.round(baseAvg * 0.7),
      p95_duration_ms: Math.round(baseAvg * 2.2),
      p99_duration_ms: Math.round(baseAvg * 3.8),
      error_rate: Math.round(errorNoise * 100) / 100,
    });

    t += intervalMs;
  }

  return buckets;
}

// ── Public API ───────────────────────────────────────────────────────────

export function getMockTracePage(filters: TraceFilters): TracePaginationResponse {
  let items = buildTraceListItems();

  if (filters.service_name) {
    items = items.filter((t) => t.service_name === filters.service_name);
  }
  if (filters.has_errors !== undefined) {
    items = items.filter((t) => t.has_errors === filters.has_errors);
  }

  const limit = filters.limit || 50;

  return {
    items: items.slice(0, limit),
    has_next: items.length > limit,
    next_cursor:
      items.length > limit
        ? { start_time: items[limit - 1].start_time, trace_id: items[limit - 1].trace_id }
        : undefined,
    has_previous: false,
    previous_cursor: undefined,
  };
}

export function getMockTraceSpans(request: TraceRequest): TraceSpansResponse {
  const spans = SPANS_BY_TRACE.get(request.trace_id);
  if (spans) {
    return { spans };
  }
  // Fallback: first trace
  const first = ALL_SPANS[0];
  return { spans: first || [] };
}

export function getMockTraceMetrics(
  request: TraceMetricsRequest,
): TraceMetricsResponse {
  const startTime = request.start_time || new Date(Date.now() - 15 * 60_000).toISOString();
  const endTime = request.end_time || new Date().toISOString();
  const bucketInterval = request.bucket_interval || "1 minutes";

  return {
    metrics: buildMetricBuckets(startTime, endTime, bucketInterval),
  };
}
