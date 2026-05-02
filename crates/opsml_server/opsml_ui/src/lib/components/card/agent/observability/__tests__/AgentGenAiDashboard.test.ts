import { describe, it, expect } from 'vitest';
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
  agent_dashboard: { summary, buckets: [] },
  tool_dashboard: { aggregates: [], time_series: [] },
  model_usage: [],
  operation_breakdown: [],
  errors: [],
  agents: [],
  range: {
    start_time: '2026-01-01T00:00:00Z',
    end_time: '2026-01-02T00:00:00Z',
    bucket_interval: 'hour',
    selected_range: '24hours',
  },
};

describe('AgentGenAiBundle shape', () => {
  it('has agent_dashboard with summary and buckets', () => {
    expect(bundle.agent_dashboard).toHaveProperty('summary');
    expect(bundle.agent_dashboard).toHaveProperty('buckets');
  });

  it('has tool_dashboard with aggregates and time_series', () => {
    expect(bundle.tool_dashboard).toHaveProperty('aggregates');
    expect(bundle.tool_dashboard).toHaveProperty('time_series');
  });

  it('has model_usage as array', () => {
    expect(Array.isArray(bundle.model_usage)).toBe(true);
  });

  it('has operation_breakdown as array', () => {
    expect(Array.isArray(bundle.operation_breakdown)).toBe(true);
  });

  it('has errors as array', () => {
    expect(Array.isArray(bundle.errors)).toBe(true);
  });

  it('has agents as array', () => {
    expect(Array.isArray(bundle.agents)).toBe(true);
  });

  it('has range with required fields', () => {
    expect(bundle.range).toHaveProperty('start_time');
    expect(bundle.range).toHaveProperty('end_time');
    expect(bundle.range).toHaveProperty('bucket_interval');
    expect(bundle.range).toHaveProperty('selected_range');
  });

  it('summary total_requests matches', () => {
    expect(bundle.agent_dashboard.summary.total_requests).toBe(100);
  });

  it('summary cost_by_model is empty array', () => {
    expect(bundle.agent_dashboard.summary.cost_by_model).toHaveLength(0);
  });
});
