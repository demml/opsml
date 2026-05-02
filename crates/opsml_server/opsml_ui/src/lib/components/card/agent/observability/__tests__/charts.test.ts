import { describe, it, expect, vi } from 'vitest';
import { buildVolumeChart, buildLatencyChart, buildTokenChart, buildCostChart, buildErrorRateChart, buildToolStackChart } from '../charts';
import type { AgentMetricBucket, ToolTimeBucket } from '../types';
import type { ChartDataset } from 'chart.js';

vi.mock('$lib/components/viz/utils', () => ({
  getChartTheme: () => ({
    textColor: '#000',
    gridColor: '#ccc',
    axisColor: '#000',
    tooltipBg: '#fff',
    tooltipBorder: '#000',
    tooltipText: '#000',
    zoomBorder: '#000',
    zoomBg: '#fff',
  }),
  getTooltip: () => ({}),
}));

vi.mock('date-fns', () => ({
  format: () => '00:00',
}));

const bucket: AgentMetricBucket = {
  bucket_start: '2026-01-01T00:00:00Z',
  span_count: 10,
  error_count: 2,
  error_rate: 0.2,
  avg_duration_ms: 100,
  p50_duration_ms: 80,
  p95_duration_ms: 150,
  p99_duration_ms: 180,
  total_input_tokens: 1000,
  total_output_tokens: 500,
  total_cache_creation_tokens: 0,
  total_cache_read_tokens: 100,
  total_cost: 0.01,
};

describe('buildVolumeChart', () => {
  it('has correct number of labels', () => {
    const config = buildVolumeChart([bucket]);
    expect(config.data.labels).toHaveLength(1);
  });

  it('has success and error datasets', () => {
    const config = buildVolumeChart([bucket, bucket]);
    expect(config.data.datasets[0].label).toBe('Success');
    expect(config.data.datasets[1].label).toBe('Error');
    expect(config.data.labels).toHaveLength(2);
  });

  it('calculates success count correctly', () => {
    const config = buildVolumeChart([bucket]);
    const successData = config.data.datasets[0].data as number[];
    expect(successData[0]).toBe(bucket.span_count - bucket.error_count);
  });

  it('returns bar type', () => {
    const config = buildVolumeChart([bucket]);
    expect(config.type).toBe('bar');
  });
});

describe('buildLatencyChart', () => {
  it('has p50/p95/p99 datasets', () => {
    const config = buildLatencyChart([bucket]);
    const datasets = config.data.datasets as ChartDataset[];
    const labels = datasets.map((d) => d.label);
    expect(labels).toContain('p50');
    expect(labels).toContain('p95');
    expect(labels).toContain('p99');
  });

  it('returns line type', () => {
    const config = buildLatencyChart([bucket]);
    expect(config.type).toBe('line');
  });
});

describe('buildTokenChart', () => {
  it('has input/output/cache_read datasets', () => {
    const config = buildTokenChart([bucket]);
    const datasets = config.data.datasets as ChartDataset[];
    const labels = datasets.map((d) => d.label);
    expect(labels).toContain('input');
    expect(labels).toContain('output');
    expect(labels).toContain('cache_read');
  });
});

describe('buildCostChart', () => {
  it('has spend dataset', () => {
    const config = buildCostChart([bucket]);
    expect(config.data.datasets[0].label).toBe('spend ($)');
  });

  it('uses total_cost values', () => {
    const config = buildCostChart([bucket]);
    const data = config.data.datasets[0].data as number[];
    expect(data[0]).toBe(0.01);
  });

  it('falls back to 0 for null total_cost', () => {
    const nullCostBucket = { ...bucket, total_cost: null };
    const config = buildCostChart([nullCostBucket]);
    const data = config.data.datasets[0].data as number[];
    expect(data[0]).toBe(0);
  });
});

describe('buildErrorRateChart', () => {
  it('multiplies error_rate by 100', () => {
    const config = buildErrorRateChart([bucket]);
    const data = config.data.datasets[0].data as number[];
    expect(data[0]).toBeCloseTo(20);
  });
});

describe('buildToolStackChart', () => {
  it('groups by tool_name', () => {
    const series: ToolTimeBucket[] = [
      { bucket_start: '2026-01-01T00:00:00Z', tool_name: 'search', tool_type: null, call_count: 5, avg_duration_ms: 100, error_rate: 0 },
      { bucket_start: '2026-01-01T01:00:00Z', tool_name: 'search', tool_type: null, call_count: 3, avg_duration_ms: 80, error_rate: 0 },
      { bucket_start: '2026-01-01T00:00:00Z', tool_name: 'calculator', tool_type: null, call_count: 2, avg_duration_ms: 50, error_rate: 0 },
    ];
    const config = buildToolStackChart(series);
    expect(config.data.datasets).toHaveLength(2);
    const datasets = config.data.datasets as ChartDataset[];
    const labels = datasets.map((d) => d.label);
    expect(labels).toContain('search');
    expect(labels).toContain('calculator');
  });

  it('returns bar type', () => {
    const config = buildToolStackChart([]);
    expect(config.type).toBe('bar');
  });

  it('handles empty series', () => {
    const config = buildToolStackChart([]);
    expect(config.data.datasets).toHaveLength(0);
    expect(config.data.labels).toHaveLength(0);
  });

  it('uses unknown for null tool_name', () => {
    const series: ToolTimeBucket[] = [
      { bucket_start: '2026-01-01T00:00:00Z', tool_name: null, tool_type: null, call_count: 1, avg_duration_ms: 50, error_rate: 0 },
    ];
    const config = buildToolStackChart(series);
    const datasets = config.data.datasets as ChartDataset[];
    const labels = datasets.map((d) => d.label);
    expect(labels).toContain('unknown');
  });
});
