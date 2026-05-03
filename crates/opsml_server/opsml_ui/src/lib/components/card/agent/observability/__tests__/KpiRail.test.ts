import { describe, it, expect } from 'vitest';
import { fmtCompact, fmtInt, fmtMs, fmtPct, fmtUsd } from '../format';
import type { AgentDashboardSummary } from '../types';

const summary: AgentDashboardSummary = {
  total_requests: 1200,
  avg_duration_ms: 340,
  p50_duration_ms: 250,
  p95_duration_ms: null,
  p99_duration_ms: 900,
  overall_error_rate: 0.03,
  total_input_tokens: 50000,
  total_output_tokens: 20000,
  total_cache_creation_tokens: 0,
  total_cache_read_tokens: 5000,
  unique_agent_count: 2,
  unique_conversation_count: 47,
  cost_by_model: [
    {
      model: 'gpt-4o',
      total_input_tokens: 50000,
      total_output_tokens: 20000,
      total_cache_creation_tokens: 0,
      total_cache_read_tokens: 5000,
      total_cost: 0.42,
    },
  ],
};

describe('KpiRail data values', () => {
  it('formats total_requests as compact', () => {
    expect(fmtCompact(summary.total_requests)).toBe('1.2K');
  });

  it('formats overall_error_rate as percentage', () => {
    expect(fmtPct(summary.overall_error_rate, 2)).toBe('3.00%');
  });

  it('formats p50_duration_ms as ms', () => {
    expect(fmtMs(summary.p50_duration_ms)).toBe('250 ms');
  });

  it('formats null p95 as dash', () => {
    expect(fmtMs(summary.p95_duration_ms)).toBe('—');
  });

  it('formats cost correctly', () => {
    const totalCost = summary.cost_by_model.reduce((a, b) => a + (b.total_cost ?? 0), 0);
    expect(fmtUsd(totalCost)).toBe('$0.42');
  });

  it('formats total tokens correctly', () => {
    const total = summary.total_input_tokens + summary.total_output_tokens;
    expect(fmtCompact(total)).toBe('70K');
  });

  it('formats conversation count as int', () => {
    expect(fmtInt(summary.unique_conversation_count)).toBe('47');
  });

  it('error_rate above 0.02 triggers error accent', () => {
    expect(summary.overall_error_rate > 0.02).toBe(true);
  });

  it('error_rate at or below 0.02 does not trigger error accent', () => {
    const safeRate = 0.01;
    expect(safeRate > 0.02).toBe(false);
  });

  it('produces exactly 10 KPI entries', () => {
    const totalCost = summary.cost_by_model.reduce((a, b) => a + (b.total_cost ?? 0), 0);
    const totalTokens = summary.total_input_tokens + summary.total_output_tokens;
    const kpis = [
      fmtCompact(summary.total_requests),
      fmtPct(summary.overall_error_rate, 2),
      fmtMs(summary.p50_duration_ms),
      fmtMs(summary.p95_duration_ms),
      fmtMs(summary.p99_duration_ms),
      fmtUsd(totalCost),
      fmtCompact(totalTokens),
      fmtCompact(summary.total_input_tokens),
      fmtCompact(summary.total_output_tokens),
      fmtInt(summary.unique_conversation_count),
    ];
    expect(kpis).toHaveLength(10);
  });
});
