import type { DateTime } from "$lib/types";
import type { TraceListItem, TraceSpan, TraceSpansResponse } from "$lib/components/trace/types";
import type { GenAiSpanRecord, GenAiTraceMetricsResponse } from "./types";

function buildDepthMap(spans: GenAiSpanRecord[]): Map<string, number> {
  const byId = new Map(spans.map((s) => [s.span_id, s]));
  const cache = new Map<string, number>();
  function depth(s: GenAiSpanRecord): number {
    if (cache.has(s.span_id)) return cache.get(s.span_id)!;
    if (!s.parent_span_id) { cache.set(s.span_id, 0); return 0; }
    const parent = byId.get(s.parent_span_id);
    const d = parent ? depth(parent) + 1 : 0;
    cache.set(s.span_id, d);
    return d;
  }
  spans.forEach(depth);
  return cache;
}

function buildPathMap(spans: GenAiSpanRecord[]): Map<string, string[]> {
  const byId = new Map(spans.map((s) => [s.span_id, s]));
  const cache = new Map<string, string[]>();
  function path(s: GenAiSpanRecord): string[] {
    if (cache.has(s.span_id)) return cache.get(s.span_id)!;
    if (!s.parent_span_id) { const p = [s.span_id]; cache.set(s.span_id, p); return p; }
    const parent = byId.get(s.parent_span_id);
    const p = parent ? [...path(parent), s.span_id] : [s.span_id];
    cache.set(s.span_id, p);
    return p;
  }
  spans.forEach(path);
  return cache;
}

function genAiToAttributes(s: GenAiSpanRecord): { key: string; value: unknown }[] {
  const attrs: { key: string; value: unknown }[] = [];
  const push = (k: string, v: unknown) => { if (v != null && v !== '') attrs.push({ key: k, value: v }); };
  push("gen_ai.operation.name", s.operation_name);
  push("gen_ai.system", s.provider_name);
  push("gen_ai.request.model", s.request_model);
  push("gen_ai.response.model", s.response_model);
  push("gen_ai.response.id", s.response_id);
  push("gen_ai.usage.input_tokens", s.input_tokens);
  push("gen_ai.usage.output_tokens", s.output_tokens);
  push("gen_ai.usage.cache_creation_input_tokens", s.cache_creation_input_tokens);
  push("gen_ai.usage.cache_read_input_tokens", s.cache_read_input_tokens);
  push("gen_ai.request.temperature", s.request_temperature);
  push("gen_ai.request.max_tokens", s.request_max_tokens);
  push("gen_ai.request.top_p", s.request_top_p);
  push("gen_ai.agent.name", s.agent_name);
  push("gen_ai.agent.id", s.agent_id);
  push("gen_ai.agent.version", s.agent_version);
  push("gen_ai.agent.description", s.agent_description);
  push("gen_ai.tool.name", s.tool_name);
  push("gen_ai.tool.type", s.tool_type);
  push("gen_ai.tool.call.id", s.tool_call_id);
  push("gen_ai.conversation.id", s.conversation_id);
  push("server.address", s.server_address);
  push("server.port", s.server_port);
  if (s.error_type) push("span.error", s.error_type);
  if (s.finish_reasons.length) push("gen_ai.response.finish_reasons", s.finish_reasons);
  return attrs;
}

export function genAiToTraceSpan(
  s: GenAiSpanRecord,
  depth: number,
  path: string[],
  order: number,
  rootSpanId: string,
): TraceSpan {
  return {
    trace_id: s.trace_id,
    span_id: s.span_id,
    parent_span_id: s.parent_span_id,
    span_name: s.label ?? s.operation_name ?? s.span_id.slice(0, 8),
    span_kind: s.tool_name ? "CLIENT" : s.operation_name === "invoke_agent" ? "SERVER" : "INTERNAL",
    start_time: s.start_time,
    end_time: s.end_time,
    duration_ms: s.duration_ms,
    status_code: s.error_type ? 2 : s.duration_ms > 0 ? 1 : 0,
    status_message: s.error_type ?? null,
    attributes: genAiToAttributes(s),
    events: [],
    links: [],
    depth,
    path,
    root_span_id: rootSpanId,
    span_order: order,
    input: s.input_messages,
    output: s.output_messages,
    service_name: s.service_name,
  };
}

export function buildTraceListItem(
  resp: GenAiTraceMetricsResponse,
  summary = resp.agent_dashboard.summary,
): TraceListItem {
  const spans = resp.spans;
  const rootSpan = spans[0];
  const startMs = Math.min(...spans.map((s) => new Date(s.start_time).getTime()));
  const endMs = Math.max(
    ...spans.map((s) =>
      s.end_time ? new Date(s.end_time).getTime() : new Date(s.start_time).getTime() + s.duration_ms
    )
  );
  const errorCount = spans.filter((s) => s.error_type).length;
  return {
    trace_id: resp.trace_id,
    service_name: rootSpan.service_name,
    scope: "gen_ai",
    root_operation: rootSpan.operation_name ?? rootSpan.label ?? resp.trace_id,
    start_time: new Date(startMs).toISOString() as DateTime,
    end_time: new Date(endMs).toISOString() as DateTime,
    duration_ms: endMs - startMs,
    status_code: errorCount > 0 ? 2 : 1,
    status_message: null,
    span_count: spans.length,
    has_errors: errorCount > 0,
    error_count: errorCount,
    created_at: new Date(startMs).toISOString() as DateTime,
    resource_attributes: [
      { key: "service.name", value: rootSpan.service_name },
      { key: "gen_ai.agent.name", value: rootSpan.agent_name },
      { key: "gen_ai.agent.version", value: rootSpan.agent_version },
    ].filter((a) => a.value != null),
  };
}

export function buildTraceSpansResponse(resp: GenAiTraceMetricsResponse): TraceSpansResponse {
  const spans = resp.spans;
  const rootSpanId = spans[0]?.span_id ?? "";
  const depthMap = buildDepthMap(spans);
  const pathMap = buildPathMap(spans);

  // Sort: depth-first by start_time to assign span_order
  const ordered = [...spans].sort(
    (a, b) => new Date(a.start_time).getTime() - new Date(b.start_time).getTime()
  );

  return {
    spans: ordered.map((s, i) =>
      genAiToTraceSpan(
        s,
        depthMap.get(s.span_id) ?? 0,
        pathMap.get(s.span_id) ?? [s.span_id],
        i,
        rootSpanId,
      )
    ),
  };
}
