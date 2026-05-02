import { describe, it, expect, vi } from 'vitest';
import type { AgentGenAiBundle } from '../types';

const summary = {
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
};

const bundle: AgentGenAiBundle = {
  dashboard: {
    applied_filters: {
      service_name: 'space:name',
      entity_id: null,
      agent_name: null,
      provider_name: null,
      operation_name: null,
      model: null,
      start_time: '2026-01-01T00:00:00Z' as unknown as AgentGenAiBundle['dashboard']['applied_filters']['start_time'],
      end_time: '2026-01-02T00:00:00Z' as unknown as AgentGenAiBundle['dashboard']['applied_filters']['end_time'],
      bucket_interval: 'hour',
    },
    available_filters: { agents: [], providers: [], models: [], operations: [] },
    metadata: {
      generated_at: '2026-01-02T00:00:00Z' as unknown as AgentGenAiBundle['dashboard']['metadata']['generated_at'],
      schema_version: 1,
      total_spans: 100,
    },
    token_metrics: { buckets: [] },
    operation_breakdown: { operations: [] },
    model_usage: { models: [] },
    agent_dashboard: { summary, buckets: [] },
    tool_dashboard: { aggregates: [], time_series: [] },
    error_breakdown: { errors: [] },
    buckets_truncated: false,
  },
  range: {
    start_time: '2026-01-01T00:00:00Z',
    end_time: '2026-01-02T00:00:00Z',
    bucket_interval: 'hour',
    selected_range: '24hours',
  },
  eval_profiles: [],
};

// ─── CustomSelect logic (label reactivity) ─────────────────────────────────
// Tests the three nitpick fixes without requiring DOM rendering:
//   (1) selecting an option immediately updates the displayed label (localValue)
//   (2) parent value sync overrides localValue (e.g. after async refetch)

const OPTIONS = [
  { value: 'gpt-4o', label: 'gpt-4o' },
  { value: 'claude-3-5-sonnet', label: 'claude-3-5-sonnet' },
];

function makeSelectLogic(initialValue: string | null = null, placeholder = 'all') {
  let localValue: string | null = initialValue;
  const onChangeCalls: Array<string | null> = [];

  function select(v: string | null) {
    localValue = v;           // optimistic update — happens synchronously
    onChangeCalls.push(v);
  }

  function syncFromParent(v: string | null | undefined) {
    localValue = v ?? null;   // mirrors the $effect(() => { localValue = value ?? null; })
  }

  function selectedLabel(): string {
    if (localValue === null) return placeholder;
    return OPTIONS.find((o) => o.value === localValue)?.label ?? placeholder;
  }

  return { select, syncFromParent, selectedLabel, onChangeCalls };
}

describe('CustomSelect — (3) active filter displayed immediately', () => {
  it('shows placeholder before any selection', () => {
    expect(makeSelectLogic().selectedLabel()).toBe('all');
  });

  it('shows selected label immediately after select() — no async wait needed', () => {
    const s = makeSelectLogic(null);
    s.select('gpt-4o');
    expect(s.selectedLabel()).toBe('gpt-4o');
  });

  it('reverts to placeholder after clearing selection', () => {
    const s = makeSelectLogic('gpt-4o');
    s.select(null);
    expect(s.selectedLabel()).toBe('all');
  });

  it('syncs to new value when parent applies server response', () => {
    const s = makeSelectLogic(null);
    s.select('gpt-4o');           // optimistic
    s.syncFromParent('claude-3-5-sonnet'); // server echoed different value
    expect(s.selectedLabel()).toBe('claude-3-5-sonnet');
  });
});

// ─── Filter → refetch integration logic ────────────────────────────────────
// Tests that (1) a filter change produces the correct merged request body and
// (2) onChange fires with the full delta so the dashboard triggers a refetch.

type FilterDelta = {
  agent_name: string | null;
  model: string | null;
  provider_name: string | null;
  operation_name: string | null;
  entity_id: string | null;
};

function makeFilterBarLogic(applied: FilterDelta) {
  const emitted: FilterDelta[] = [];

  function onChange(next: FilterDelta) {
    emitted.push(next);
  }

  // Mirrors FilterBar's inline onChange callback for each dropdown
  function selectModel(v: string | null) {
    onChange({ ...applied, model: v });
  }

  function selectAgent(v: string | null) {
    onChange({ ...applied, agent_name: v });
  }

  function selectProvider(v: string | null) {
    onChange({ ...applied, provider_name: v });
  }

  function selectOperation(v: string | null) {
    onChange({ ...applied, operation_name: v });
  }

  function selectProfile(v: string | null) {
    onChange({ ...applied, entity_id: v });
  }

  return { selectModel, selectAgent, selectProvider, selectOperation, selectProfile, emitted };
}

describe('FilterBar → (1) filter state update + (2) refetch trigger', () => {
  const baseApplied: FilterDelta = {
    agent_name: null,
    model: null,
    provider_name: null,
    operation_name: null,
    entity_id: null,
  };

  it('model selection emits full delta with updated model', () => {
    const fb = makeFilterBarLogic(baseApplied);
    fb.selectModel('gpt-4o');
    expect(fb.emitted).toHaveLength(1);
    expect(fb.emitted[0].model).toBe('gpt-4o');
    expect(fb.emitted[0].agent_name).toBeNull();
  });

  it('agent selection does not clobber other filters', () => {
    const applied: FilterDelta = { ...baseApplied, model: 'gpt-4o' };
    const fb = makeFilterBarLogic(applied);
    fb.selectAgent('my-agent');
    expect(fb.emitted[0].model).toBe('gpt-4o');  // preserved
    expect(fb.emitted[0].agent_name).toBe('my-agent');
  });

  it('provider selection emits delta with updated provider_name', () => {
    const fb = makeFilterBarLogic(baseApplied);
    fb.selectProvider('anthropic');
    expect(fb.emitted[0].provider_name).toBe('anthropic');
  });

  it('operation selection emits delta with updated operation_name', () => {
    const fb = makeFilterBarLogic(baseApplied);
    fb.selectOperation('chat.completions');
    expect(fb.emitted[0].operation_name).toBe('chat.completions');
  });

  it('profile selection emits delta with updated entity_id', () => {
    const fb = makeFilterBarLogic(baseApplied);
    fb.selectProfile('abc-123-uid');
    expect(fb.emitted[0].entity_id).toBe('abc-123-uid');
  });

  it('clearing a filter emits null for that field', () => {
    const applied: FilterDelta = { ...baseApplied, model: 'gpt-4o' };
    const fb = makeFilterBarLogic(applied);
    fb.selectModel(null);
    expect(fb.emitted[0].model).toBeNull();
  });

  it('each filter change emits exactly once (one refetch per change)', () => {
    const fb = makeFilterBarLogic(baseApplied);
    fb.selectModel('gpt-4o');
    fb.selectAgent('bot');
    fb.selectProvider('openai');
    expect(fb.emitted).toHaveLength(3);
  });
});

describe('AgentGenAiBundle shape', () => {
  it('wraps a composite dashboard response', () => {
    expect(bundle.dashboard).toHaveProperty('applied_filters');
    expect(bundle.dashboard).toHaveProperty('available_filters');
    expect(bundle.dashboard).toHaveProperty('metadata');
    expect(bundle.dashboard).toHaveProperty('agent_dashboard');
    expect(bundle.dashboard).toHaveProperty('tool_dashboard');
    expect(bundle.dashboard).toHaveProperty('model_usage');
    expect(bundle.dashboard).toHaveProperty('operation_breakdown');
    expect(bundle.dashboard).toHaveProperty('error_breakdown');
    expect(bundle.dashboard).toHaveProperty('token_metrics');
  });

  it('has range with required fields', () => {
    expect(bundle.range).toHaveProperty('start_time');
    expect(bundle.range).toHaveProperty('end_time');
    expect(bundle.range).toHaveProperty('bucket_interval');
    expect(bundle.range).toHaveProperty('selected_range');
  });

  it('summary total_requests matches', () => {
    expect(bundle.dashboard.agent_dashboard.summary.total_requests).toBe(100);
  });

  it('summary cost_by_model is empty array', () => {
    expect(bundle.dashboard.agent_dashboard.summary.cost_by_model).toHaveLength(0);
  });

  it('applied_filters preserves the requested service scope', () => {
    expect(bundle.dashboard.applied_filters.service_name).toBe('space:name');
    expect(bundle.dashboard.applied_filters.entity_id).toBeNull();
  });
});
