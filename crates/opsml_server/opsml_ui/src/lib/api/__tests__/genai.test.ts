import { describe, it, expect, vi, beforeEach } from 'vitest';
import { createInternalApiClient } from '$lib/api/internalClient';

vi.mock('$lib/api/internalClient', () => ({ createInternalApiClient: vi.fn() }));

import {
  fetchSpanGenAIMetrics,
  fetchTraceGenAIMetrics,
  fetchServiceGenAITimeseries,
  _clearGenAICache,
} from '../genai';

const mockGet = vi.fn();
const mockPost = vi.fn();

beforeEach(() => {
  vi.mocked(createInternalApiClient).mockReturnValue({ get: mockGet, post: mockPost } as unknown as ReturnType<typeof createInternalApiClient>);
  mockGet.mockReset();
  mockPost.mockReset();
  _clearGenAICache();
});

describe('genai API client', () => {
  it('fetchSpanGenAIMetrics returns parsed body and caches', async () => {
    const body = [{ token_count_input: 1, token_count_output: 2, model_name: 'm', latency_ms: 10, cost: 0.001 }];
    mockGet.mockResolvedValue({ ok: true, json: async () => body });
    const first = await fetchSpanGenAIMetrics('s1');
    expect(first).toEqual(body);
    const second = await fetchSpanGenAIMetrics('s1');
    expect(mockGet).toHaveBeenCalledTimes(1);
    expect(second).toEqual(body);
  });

  it('fetchTraceGenAIMetrics returns parsed body', async () => {
    const body = { total_tokens: 10, avg_latency: 100, model_distribution: { a: 1 }, time_period: { start_time: '2026-01-01', end_time: '2026-01-02' } };
    mockGet.mockResolvedValue({ ok: true, json: async () => body });
    const out = await fetchTraceGenAIMetrics('t1');
    expect(out).toEqual(body);
  });

  it('fetchServiceGenAITimeseries sends params and caches', async () => {
    const body = { points: [{ timestamp: '2026-01-01T00:00:00Z', metric_name: 'input_tokens', value: 10 }], labels: ['a'] };
    mockGet.mockResolvedValue({ ok: true, json: async () => body });
    const s = new Date('2026-01-01T00:00:00Z');
    const e = new Date('2026-01-01T01:00:00Z');
    const first = await fetchServiceGenAITimeseries('svc', s, e);
    expect(first).toEqual(body);
    const second = await fetchServiceGenAITimeseries('svc', s, e);
    expect(mockGet).toHaveBeenCalledTimes(1);
  });
});
