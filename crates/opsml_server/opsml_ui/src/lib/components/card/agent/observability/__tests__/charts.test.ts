import { describe, it, expect, vi } from 'vitest';
import { buildVolumeChart, buildLatencyChart, buildTokenChart, buildCostChart, buildErrorRateChart, buildToolStackChart, buildOperationBarChart, buildSpanDurationBar } from '../charts';
import type { AgentMetricBucket, ModelCostBreakdown, ToolTimeBucket } from '../types';
import type { GenAiOperationBreakdown, GenAiSpanRecord } from '$lib/components/scouter/genai/types';
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
  const costRow: ModelCostBreakdown = {
    model: 'gpt-4o',
    total_input_tokens: 1000,
    total_output_tokens: 500,
    total_cache_creation_tokens: 0,
    total_cache_read_tokens: 100,
    total_cost: 0.01,
  };

  it('has spend dataset', () => {
    const config = buildCostChart([costRow]);
    expect(config.data.datasets[0].label).toBe('spend ($)');
  });

  it('uses total_cost values', () => {
    const config = buildCostChart([costRow]);
    const data = config.data.datasets[0].data as number[];
    expect(data[0]).toBe(0.01);
  });

  it('skips rows with null or zero total_cost', () => {
    const nullCostRow: ModelCostBreakdown = { ...costRow, total_cost: null };
    const config = buildCostChart([nullCostRow]);
    const data = config.data.datasets[0].data as number[];
    expect(data).toHaveLength(0);
  });

  it('sorts models by descending cost', () => {
    const high: ModelCostBreakdown = { ...costRow, model: 'high', total_cost: 5 };
    const low: ModelCostBreakdown = { ...costRow, model: 'low', total_cost: 1 };
    const config = buildCostChart([low, high]);
    expect(config.data.labels).toEqual(['high', 'low']);
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

describe('buildOperationBarChart', () => {
  it('returns bar type', () => {
    const operations: GenAiOperationBreakdown[] = [
      {
        operation_name: 'llm.call',
        provider_name: 'openai',
        span_count: 10,
        avg_duration_ms: 100,
        total_input_tokens: 500,
        total_output_tokens: 200,
        error_rate: 0.1,
      },
    ];
    const config = buildOperationBarChart(operations);
    expect(config.type).toBe('bar');
  });

  it('sorts labels by span_count descending', () => {
    const operations: GenAiOperationBreakdown[] = [
      {
        operation_name: 'retrieval',
        provider_name: null,
        span_count: 5,
        avg_duration_ms: 50,
        total_input_tokens: 0,
        total_output_tokens: 0,
        error_rate: 0,
      },
      {
        operation_name: 'llm.call',
        provider_name: 'openai',
        span_count: 20,
        avg_duration_ms: 100,
        total_input_tokens: 500,
        total_output_tokens: 200,
        error_rate: 0.1,
      },
      {
        operation_name: 'embedding',
        provider_name: null,
        span_count: 12,
        avg_duration_ms: 75,
        total_input_tokens: 300,
        total_output_tokens: 0,
        error_rate: 0.05,
      },
    ];
    const config = buildOperationBarChart(operations);
    const labels = config.data.labels as string[];
    expect(labels).toEqual(['llm.call', 'embedding', 'retrieval']);
  });
});

describe('buildSpanDurationBar', () => {
  it('uses errorSoft color for spans with error_type', () => {
    const spans: GenAiSpanRecord[] = [
      {
        trace_id: 'trace1',
        span_id: 'span_000001',
        service_name: 'test-svc',
        start_time: '2026-01-01T00:00:00Z',
        end_time: '2026-01-01T00:00:01Z',
        duration_ms: 100,
        status_code: 500,
        operation_name: 'llm.call',
        provider_name: 'openai',
        request_model: 'gpt-4',
        response_model: null,
        response_id: null,
        input_tokens: 100,
        output_tokens: 50,
        cache_creation_input_tokens: null,
        cache_read_input_tokens: null,
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
        request_top_p: null,
        request_choice_count: null,
        request_seed: null,
        request_frequency_penalty: null,
        request_presence_penalty: null,
        request_stop_sequences: [],
        server_address: null,
        server_port: null,
        error_type: 'timeout',
        openai_api_type: null,
        openai_service_tier: null,
        label: 'my_operation',
        entity_id: null,
        input_messages: null,
        output_messages: null,
        system_instructions: null,
        tool_definitions: null,
        eval_results: [],
      },
      {
        trace_id: 'trace1',
        span_id: 'span_000002',
        service_name: 'test-svc',
        start_time: '2026-01-01T00:00:00Z',
        end_time: '2026-01-01T00:00:01Z',
        duration_ms: 50,
        status_code: 200,
        operation_name: 'embedding',
        provider_name: null,
        request_model: null,
        response_model: null,
        response_id: null,
        input_tokens: null,
        output_tokens: null,
        cache_creation_input_tokens: null,
        cache_read_input_tokens: null,
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
        request_top_p: null,
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
        label: 'embed_call',
        entity_id: null,
        input_messages: null,
        output_messages: null,
        system_instructions: null,
        tool_definitions: null,
        eval_results: [],
      },
    ];
    const config = buildSpanDurationBar(spans);
    const colors = (config.data.datasets[0].backgroundColor as string[]);
    expect(colors[0]).toContain('254, 108, 107, 0.55'); // errorSoft
    expect(colors[1]).toContain('135, 170, 240, 0.55'); // tertiarySoft (no error)
  });

  it('falls back to span_id slice when label is null', () => {
    const spans: GenAiSpanRecord[] = [
      {
        trace_id: 'trace1',
        span_id: 'abc123456789',
        service_name: 'test-svc',
        start_time: '2026-01-01T00:00:00Z',
        end_time: '2026-01-01T00:00:01Z',
        duration_ms: 100,
        status_code: 200,
        operation_name: null,
        provider_name: null,
        request_model: null,
        response_model: null,
        response_id: null,
        input_tokens: null,
        output_tokens: null,
        cache_creation_input_tokens: null,
        cache_read_input_tokens: null,
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
        request_top_p: null,
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
        entity_id: null,
        input_messages: null,
        output_messages: null,
        system_instructions: null,
        tool_definitions: null,
        eval_results: [],
      },
    ];
    const config = buildSpanDurationBar(spans);
    const labels = config.data.labels as string[];
    expect(labels[0]).toBe('abc12345');
  });
});
