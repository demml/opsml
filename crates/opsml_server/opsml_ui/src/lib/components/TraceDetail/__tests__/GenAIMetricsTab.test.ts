import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/svelte';

vi.mock('$lib/api/internalClient', () => ({ createInternalApiClient: vi.fn() }));

import GenAIMetricsTab from '../GenAIMetricsTab.svelte';
import { createInternalApiClient } from '$lib/api/internalClient';
import type { GenAiTraceMetricsResponse } from '$lib/components/scouter/genai/types';

function makeGenAi(): GenAiTraceMetricsResponse {
  return {
    trace_id: 't1',
    has_genai_spans: true,
    spans: [
      {
        trace_id: 't1',
        span_id: 's1',
        parent_span_id: null,
        service_name: 'svc',
        start_time: '2026-01-01T00:00:00Z',
        end_time: '2026-01-01T00:00:01Z',
        duration_ms: 100,
        status_code: 1,
        operation_name: 'op',
        provider_name: 'openai',
        request_model: 'gpt-4o-mini',
        response_model: null,
        response_id: null,
        input_tokens: 10,
        output_tokens: 5,
        cache_creation_input_tokens: 0,
        cache_read_input_tokens: 0,
        finish_reasons: [],
        output_type: null,
        conversation_id: null,
        agent_name: null,
        agent_id: null,
        agent_description: null,
        agent_version: null,
        data_source_id: null,
        tool_name: null,
        tool_type: null,
        tool_call_id: null,
        request_temperature: null,
        request_max_tokens: null,
        request_choice_count: null,
        request_seed: null,
        request_frequency_penalty: null,
        request_presence_penalty: null,
        request_stop_sequences: [],
        server_address: null,
        server_port: null,
        error_type: null,
        openai_api_type: null,
        openai_service_tier: null,
        label: null,
        input_messages: null,
        output_messages: null,
        system_instructions: null,
        tool_definitions: null,
        eval_results: [],
      },
    ],
    span_limit: 100,
    spans_truncated: false,
    sensitive_content_redacted: false,
    token_metrics: { buckets: [] },
    operation_breakdown: { operations: [] },
    model_usage: { models: [] },
    agent_activity: { agents: [] },
    agent_dashboard: { summary: { total_requests: 0, avg_duration_ms: 0, p50_duration_ms: null, p95_duration_ms: null, p99_duration_ms: null, overall_error_rate: 0, total_input_tokens: 0, total_output_tokens: 0, total_cache_creation_tokens: 0, total_cache_read_tokens: 0, unique_agent_count: 0, unique_conversation_count: 0, cost_by_model: [] }, buckets: [] },
    tool_dashboard: { aggregates: [], time_series: [] },
    error_breakdown: { errors: [] },
  };
}

const mockPost = vi.fn();

beforeEach(() => {
  vi.mocked(createInternalApiClient).mockReturnValue({ post: mockPost } as unknown as ReturnType<typeof createInternalApiClient>);
  mockPost.mockReset();
});

describe('GenAIMetricsTab', () => {
  it('fetches and renders span rows', async () => {
    const body = makeGenAi();
    mockPost.mockResolvedValue({ ok: true, json: async () => body });

    const { container } = render(GenAIMetricsTab, { props: { traceId: 't1' } });

    // Wait for the table row to appear
    expect(await screen.findByText('s1')).toBeTruthy();
    expect(container.textContent).toContain('gpt-4o-mini');
    expect(container.textContent).toContain('10');
  });

  it('shows empty state when no spans', async () => {
    const resp = makeGenAi();
    resp.has_genai_spans = false;
    mockPost.mockResolvedValue({ ok: true, json: async () => resp });

    const { container } = render(GenAIMetricsTab, { props: { traceId: 't1' } });
    expect(await screen.findByText('No GenAI spans found for this trace.')).toBeTruthy();
  });

  it('renders error message when fetch fails', async () => {
    mockPost.mockResolvedValue({ ok: false, status: 500 });
    const { container } = render(GenAIMetricsTab, { props: { traceId: 't1' } });
    expect(await screen.findByText(/Failed to load GenAI metrics/i)).toBeTruthy();
  });
});
