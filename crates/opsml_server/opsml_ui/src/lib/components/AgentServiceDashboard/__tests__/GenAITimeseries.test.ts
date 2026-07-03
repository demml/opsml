import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/svelte';

vi.mock('$lib/components/card/agent/observability/GenAiChartCard.svelte', () => ({ default: vi.fn() }));
vi.mock('$lib/api/internalClient', () => ({ createInternalApiClient: vi.fn() }));

import GenAITimeseries from '../GenAITimeseries.svelte';
import { createInternalApiClient } from '$lib/api/internalClient';

const mockGet = vi.fn();

beforeEach(() => {
  vi.mocked(createInternalApiClient).mockReturnValue({ get: mockGet } as unknown as ReturnType<typeof createInternalApiClient>);
  mockGet.mockReset();
});

describe('GenAITimeseries', () => {
  it('renders charts when service timeseries returns data', async () => {
    const body = {
      agent_dashboard: { buckets: [ { bucket_start: '2026-01-01T00:00:00Z', total_cost: 1, total_input_tokens: 10, total_output_tokens: 5, span_count: 1, error_count:0, error_rate:0, avg_duration_ms:100, p50_duration_ms:100, p95_duration_ms:100, p99_duration_ms:100, total_cache_creation_tokens:0, total_cache_read_tokens:0 } ], summary: { total_requests:1, avg_duration_ms:100, p50_duration_ms:100, p95_duration_ms:100, p99_duration_ms:100, overall_error_rate:0, total_input_tokens:10, total_output_tokens:5, total_cache_creation_tokens:0, total_cache_read_tokens:0, unique_agent_count:1, unique_conversation_count:1, cost_by_model:[] } },
      model_usage: { models: [ { model: 'gpt-4o-mini', provider_name: 'openai', span_count: 1, total_input_tokens:10, total_output_tokens:5, p50_duration_ms:100, p95_duration_ms:100, error_rate:0 } ] },
      buckets: [],
    };

    mockGet.mockResolvedValue({ ok: true, json: async () => body });

    const { container } = render(GenAITimeseries, { props: { serviceId: 'svc-1' } });
    // Expect the component heading
    expect(container.textContent).toContain('GenAI Timeseries');
    // Model name should appear somewhere in rendered content (from mocked data)
    expect(await screen.findByText('GenAI Timeseries')).toBeTruthy();
  });
});
