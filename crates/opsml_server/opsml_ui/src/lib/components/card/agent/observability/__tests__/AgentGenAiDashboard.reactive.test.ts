import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, cleanup } from '@testing-library/svelte';
import { tick } from 'svelte';
import AgentGenAiDashboard from '../AgentGenAiDashboard.svelte';
import { timeRangeState } from '$lib/components/utils/timeState.svelte';
import type { AgentGenAiBundle, GenAiDashboardResponse } from '../types';

// ─── Fixture builders ──────────────────────────────────────────────────────

function makeDashboard(overrides: Partial<GenAiDashboardResponse> = {}): GenAiDashboardResponse {
  return {
    applied_filters: {
      service_name: 'agent-service',
      service_namespace: null,
      service_version: null,
      service_instance_id: null,
      entity_id: null,
      agent_name: null,
      provider_name: null,
      operation_name: null,
      model: null,
      start_time: '2026-01-01T00:00:00Z' as unknown as GenAiDashboardResponse['applied_filters']['start_time'],
      end_time: '2026-01-02T00:00:00Z' as unknown as GenAiDashboardResponse['applied_filters']['end_time'],
      bucket_interval: 'hour',
    },
    available_filters: {
      agents: [],
      providers: ['openai'],
      models: ['gpt-4o', 'claude-3-5-sonnet'],
      operations: ['chat.completions'],
      service_namespaces: [],
      service_versions: [],
      service_instance_ids: [],
    },
    metadata: {
      generated_at: '2026-01-02T00:00:00Z' as unknown as GenAiDashboardResponse['metadata']['generated_at'],
      schema_version: 1,
      total_spans: 100,
    },
    token_metrics: { buckets: [] },
    operation_breakdown: { operations: [] },
    model_usage: { models: [] },
    agent_dashboard: {
      summary: {
        total_requests: 100,
        avg_duration_ms: 200,
        p50_duration_ms: 150,
        p95_duration_ms: 300,
        p99_duration_ms: 450,
        overall_error_rate: 0.01,
        total_input_tokens: 10000,
        total_output_tokens: 5000,
        total_cache_creation_tokens: 0,
        total_cache_read_tokens: 1000,
        unique_agent_count: 1,
        unique_conversation_count: 10,
        cost_by_model: [],
      },
      buckets: [],
    },
    tool_dashboard: { aggregates: [], time_series: [] },
    error_breakdown: { errors: [] },
    buckets_truncated: false,
    ...overrides,
  };
}

function makeBundle(): AgentGenAiBundle {
  return {
    dashboard: makeDashboard(),
    range: {
      start_time: '2026-01-01T00:00:00Z',
      end_time: '2026-01-02T00:00:00Z',
      bucket_interval: 'hour',
      selected_range: '24hours',
    },
    eval_profiles: [],
  };
}

// `await flush()` drains every queued microtask, $effect, and rerender so
// assertions run after the component has fully reacted to a state change.
async function flush(times = 5) {
  for (let i = 0; i < times; i++) {
    await tick();
    await Promise.resolve();
  }
}

// ─── Test setup ────────────────────────────────────────────────────────────

let fetchMock: ReturnType<typeof vi.fn>;

beforeEach(() => {
  // Each test resets fetch and the shared timeRangeState so cases don't
  // contaminate each other.
  fetchMock = vi.fn(async () =>
    new Response(JSON.stringify(makeDashboard()), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    }),
  );
  vi.stubGlobal('fetch', fetchMock);
  // Chart child components read theme via window.matchMedia — jsdom omits it.
  if (!window.matchMedia) {
    window.matchMedia = vi.fn().mockReturnValue({
      matches: false,
      media: '',
      onchange: null,
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      addListener: vi.fn(),
      removeListener: vi.fn(),
      dispatchEvent: vi.fn(),
    }) as unknown as typeof window.matchMedia;
  }
  timeRangeState.refreshSignal = 0;
  timeRangeState.isRefreshing = false;
});

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

// ─── The actual regression tests ───────────────────────────────────────────

describe('AgentGenAiDashboard — reactive fetch contract', () => {
  it('does NOT fetch on initial mount (loader bundle is fresh)', async () => {
    render(AgentGenAiDashboard, { props: { bundle: makeBundle() } });
    await flush();
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it('a single filter change triggers exactly ONE fetch (no infinite loop)', async () => {
    render(AgentGenAiDashboard, { props: { bundle: makeBundle() } });
    await flush();
    expect(fetchMock).not.toHaveBeenCalled();

    // Open the Model dropdown and pick an option — this is the exact path
    // a user takes. If the effect re-fires on its own output (the bundle
    // reassign), this count balloons past 1 and the test fails loudly.
    const modelTrigger = screen.getByLabelText('Model');
    await fireEvent.click(modelTrigger);
    const option = await screen.findByRole('option', { name: 'gpt-4o' });
    await fireEvent.click(option);
    await flush(10);

    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it('changing several filters sequentially fires exactly one fetch per change', async () => {
    render(AgentGenAiDashboard, { props: { bundle: makeBundle() } });
    await flush();

    await fireEvent.click(screen.getByLabelText('Model'));
    await fireEvent.click(await screen.findByRole('option', { name: 'gpt-4o' }));
    await flush(10);
    expect(fetchMock).toHaveBeenCalledTimes(1);

    await fireEvent.click(screen.getByLabelText('Provider'));
    await fireEvent.click(await screen.findByRole('option', { name: 'openai' }));
    await flush(10);
    expect(fetchMock).toHaveBeenCalledTimes(2);

    await fireEvent.click(screen.getByLabelText('Operation'));
    await fireEvent.click(await screen.findByRole('option', { name: 'chat.completions' }));
    await flush(10);
    expect(fetchMock).toHaveBeenCalledTimes(3);
  });

  it('timeRangeState.refresh() triggers exactly ONE fetch', async () => {
    render(AgentGenAiDashboard, { props: { bundle: makeBundle() } });
    await flush();

    timeRangeState.refresh();
    await flush(10);

    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it('the response settling does NOT trigger a second fetch (output is not an effect input)', async () => {
    // This is the core regression test. The original bug: `bundle` was both
    // input (read by refetch) and output (reassigned by refetch). Each fetch
    // settled → bundle reassign → effect refired → another fetch → infinite.
    render(AgentGenAiDashboard, { props: { bundle: makeBundle() } });
    await flush();

    timeRangeState.refresh();
    await flush(10);
    expect(fetchMock).toHaveBeenCalledTimes(1);

    // Generous wait: if the effect was self-triggering, more fetches would
    // appear in the next few microtask drains.
    await flush(20);
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it('stale response from a superseded request does not overwrite fresh data', async () => {
    // Two filter changes fire back-to-back; the first response is delayed
    // so it resolves AFTER the second. The component must discard the
    // stale (first) response and keep the fresh (second) one.
    let resolveFirst!: (v: Response) => void;
    const firstResponse = new Promise<Response>((r) => (resolveFirst = r));
    const firstDashboard = makeDashboard({
      applied_filters: {
        ...makeDashboard().applied_filters,
        model: 'gpt-4o',
      },
    });
    const secondDashboard = makeDashboard({
      applied_filters: {
        ...makeDashboard().applied_filters,
        model: 'claude-3-5-sonnet',
      },
    });

    let call = 0;
    fetchMock.mockImplementation(async () => {
      call += 1;
      if (call === 1) return firstResponse;
      return new Response(JSON.stringify(secondDashboard), { status: 200 });
    });

    render(AgentGenAiDashboard, { props: { bundle: makeBundle() } });
    await flush();

    // Change 1
    await fireEvent.click(screen.getByLabelText('Model'));
    await fireEvent.click(await screen.findByRole('option', { name: 'gpt-4o' }));
    await flush(2);
    // Change 2 (before first response settles)
    await fireEvent.click(screen.getByLabelText('Model'));
    await fireEvent.click(await screen.findByRole('option', { name: 'claude-3-5-sonnet' }));
    await flush(10);

    // Now resolve the first request — it's stale and must be discarded.
    resolveFirst(
      new Response(JSON.stringify(firstDashboard), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      }),
    );
    await flush(10);

    // FilterBar reflects the second response, not the first.
    expect(screen.getByLabelText('Model')).toHaveTextContent(
      'claude-3-5-sonnet',
    );
  });
});
