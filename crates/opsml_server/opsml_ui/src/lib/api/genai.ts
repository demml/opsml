import { createInternalApiClient } from './internalClient';
import type {
  GenAISpanMetrics,
  GenAIAggregateMetrics,
  GenAITimeseriesResponse,
} from '$lib/types/genai';

/** Simple in-memory cache entry */
type CacheEntry<T> = { ts: number; value: T };

const ONE_MINUTE = 60_000;

const spanCache: Map<string, CacheEntry<GenAISpanMetrics[]>> = new Map();
const traceCache: Map<string, CacheEntry<GenAIAggregateMetrics>> = new Map();
const serviceTimeseriesCache: Map<string, CacheEntry<GenAITimeseriesResponse>> = new Map();

function isStale(ts: number, ttl = ONE_MINUTE) {
  return Date.now() - ts > ttl;
}

/**
 * Fetch GenAI metrics for a specific span.
 * GET /api/spans/{span_id}/genai/metrics
 */
export async function fetchSpanGenAIMetrics(spanId: string): Promise<GenAISpanMetrics[]> {
  if (!spanId) return [];
  const key = String(spanId);
  const cached = spanCache.get(key);
  if (cached && !isStale(cached.ts)) return cached.value;

  const client = createInternalApiClient(fetch);
  const path = `/api/spans/${encodeURIComponent(spanId)}/genai/metrics`;
  const res = await client.get(path);
  if (!res.ok) throw new Error(`Failed to fetch span GenAI metrics: ${res.status}`);
  const body = (await res.json()) as GenAISpanMetrics[];
  spanCache.set(key, { ts: Date.now(), value: body });
  return body;
}

/**
 * Fetch aggregate GenAI metrics for a trace.
 * GET /api/traces/{trace_id}/genai/aggregate
 */
export async function fetchTraceGenAIMetrics(traceId: string): Promise<GenAIAggregateMetrics> {
  if (!traceId) throw new Error('traceId is required');
  const key = String(traceId);
  const cached = traceCache.get(key);
  if (cached && !isStale(cached.ts)) return cached.value;

  const client = createInternalApiClient(fetch);
  const path = `/api/traces/${encodeURIComponent(traceId)}/genai/aggregate`;
  const res = await client.get(path);
  if (!res.ok) throw new Error(`Failed to fetch trace GenAI metrics: ${res.status}`);
  const body = (await res.json()) as GenAIAggregateMetrics;
  traceCache.set(key, { ts: Date.now(), value: body });
  return body;
}

/**
 * Fetch service-level GenAI timeseries.
 * GET /api/services/{service_id}/genai/timeseries?start_time=...&end_time=...
 */
export async function fetchServiceGenAITimeseries(
  serviceId: string,
  startDate: Date,
  endDate: Date,
): Promise<GenAITimeseriesResponse> {
  if (!serviceId) throw new Error('serviceId is required');
  const key = `${serviceId}:${startDate?.toISOString() ?? ''}:${endDate?.toISOString() ?? ''}`;
  const cached = serviceTimeseriesCache.get(key);
  if (cached && !isStale(cached.ts, ONE_MINUTE * 5)) return cached.value;

  const client = createInternalApiClient(fetch);
  const params = {
    start_time: startDate?.toISOString(),
    end_time: endDate?.toISOString(),
  } as Record<string, string>;
  const path = `/api/services/${encodeURIComponent(serviceId)}/genai/timeseries`;
  const res = await client.get(path, params);
  if (!res.ok) throw new Error(`Failed to fetch service GenAI timeseries: ${res.status}`);
  const body = (await res.json()) as GenAITimeseriesResponse;
  serviceTimeseriesCache.set(key, { ts: Date.now(), value: body });
  return body;
}

/** Utilities for tests or dev: clear caches */
export function _clearGenAICache() {
  spanCache.clear();
  traceCache.clear();
  serviceTimeseriesCache.clear();
}
