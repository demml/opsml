import type { TraceSpan } from "./types";

function spanTimestamp(span: TraceSpan): number {
  const time = new Date(span.start_time).getTime();
  return Number.isFinite(time) ? time : 0;
}

function compareSpanOrder(a: TraceSpan, b: TraceSpan): number {
  const tA = spanTimestamp(a);
  const tB = spanTimestamp(b);
  return tA !== tB ? tA - tB : a.span_order - b.span_order;
}

function visualParentId(span: TraceSpan, spanIds: Set<string>): string | null {
  return span.parent_span_id && spanIds.has(span.parent_span_id) ? span.parent_span_id : null;
}

export function prepareWaterfallSpans(spans: TraceSpan[]): TraceSpan[] {
  const spanIds = new Set(spans.map((span) => span.span_id));
  const childrenMap = new Map<string | null, TraceSpan[]>();

  for (const span of spans) {
    const parentId = visualParentId(span, spanIds);
    if (!childrenMap.has(parentId)) childrenMap.set(parentId, []);
    childrenMap.get(parentId)!.push(span);
  }

  for (const siblings of childrenMap.values()) {
    siblings.sort(compareSpanOrder);
  }

  const result: TraceSpan[] = [];
  const visited = new Set<string>();

  function traverse(span: TraceSpan, depth: number, path: string[]) {
    if (visited.has(span.span_id)) return;

    visited.add(span.span_id);
    result.push({
      ...span,
      depth,
      path,
    });

    for (const child of childrenMap.get(span.span_id) ?? []) {
      traverse(child, depth + 1, [...path, span.span_id]);
    }
  }

  for (const root of childrenMap.get(null) ?? []) {
    traverse(root, 0, []);
  }

  const remaining = spans.filter((span) => !visited.has(span.span_id)).sort(compareSpanOrder);
  for (const span of remaining) {
    traverse(span, 0, []);
  }

  return result;
}
