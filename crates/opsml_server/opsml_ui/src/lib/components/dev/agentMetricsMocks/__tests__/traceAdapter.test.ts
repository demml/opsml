import { describe, it, expect } from 'vitest';
import { buildTraceListItem, buildTraceSpansResponse } from '../traceAdapter';
import { buildTraceMockResponse } from '../traceMockData';

describe('buildTraceSpansResponse', () => {
  it('returns a span for every entry in resp.spans', () => {
    const resp = buildTraceMockResponse();
    const result = buildTraceSpansResponse(resp);
    expect(result.spans).toHaveLength(resp.spans.length);
  });

  it('assigns sequential span_order starting at 0', () => {
    const resp = buildTraceMockResponse();
    const result = buildTraceSpansResponse(resp);
    result.spans.forEach((s, i) => expect(s.span_order).toBe(i));
  });

  it('assigns depth 0 to the root span', () => {
    const resp = buildTraceMockResponse();
    const result = buildTraceSpansResponse(resp);
    const root = result.spans.find((s) => !s.parent_span_id);
    expect(root?.depth).toBe(0);
  });

  it('assigns depth > 0 to child spans', () => {
    const resp = buildTraceMockResponse();
    const result = buildTraceSpansResponse(resp);
    const children = result.spans.filter((s) => s.parent_span_id);
    expect(children.length).toBeGreaterThan(0);
    children.forEach((s) => expect(s.depth).toBeGreaterThan(0));
  });

  it('sorts spans by start_time ascending', () => {
    const resp = buildTraceMockResponse();
    const result = buildTraceSpansResponse(resp);
    for (let i = 1; i < result.spans.length; i++) {
      const prev = new Date(result.spans[i - 1].start_time).getTime();
      const curr = new Date(result.spans[i].start_time).getTime();
      expect(curr).toBeGreaterThanOrEqual(prev);
    }
  });
});

describe('buildTraceListItem', () => {
  it('throws on empty spans', () => {
    const resp = buildTraceMockResponse();
    expect(() => buildTraceListItem({ ...resp, spans: [] })).toThrow();
  });

  it('returns trace_id from resp', () => {
    const resp = buildTraceMockResponse();
    const item = buildTraceListItem(resp);
    expect(item.trace_id).toBe(resp.trace_id);
  });

  it('sets has_errors when any span has error_type', () => {
    const resp = buildTraceMockResponse();
    const hasAnyError = resp.spans.some((s) => s.error_type);
    const item = buildTraceListItem(resp);
    expect(item.has_errors).toBe(hasAnyError);
  });

  it('computes duration_ms as end - start', () => {
    const resp = buildTraceMockResponse();
    const item = buildTraceListItem(resp);
    const startMs = Math.min(...resp.spans.map((s) => new Date(s.start_time).getTime()));
    const endMs = Math.max(
      ...resp.spans.map((s) =>
        s.end_time ? new Date(s.end_time).getTime() : new Date(s.start_time).getTime() + s.duration_ms
      )
    );
    expect(item.duration_ms).toBe(endMs - startMs);
  });
});
