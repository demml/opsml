/**
 * Types for GenAI metrics used by the UI.
 * These are strict, minimal shapes consumed by dashboard components and charts.
 */

/**
 * Metrics measured for a single GenAI span or call.
 */
export interface GenAISpanMetrics {
  /** Number of input tokens consumed by the request. */
  token_count_input: number;
  /** Number of output tokens produced by the response. */
  token_count_output: number;
  /** Canonical model identifier used for the request (e.g. "gpt-4o-mini"). */
  model_name: string;
  /** Latency for the call in milliseconds. */
  latency_ms: number;
  /** Monetary cost for this call in USD (may be 0). */
  cost: number;
}

/**
 * Aggregate metrics over a timeframe or window.
 */
export interface GenAIAggregateMetrics {
  /** Total tokens (input + output) observed in the aggregation window. */
  total_tokens: number;
  /** Average latency in milliseconds across the window. */
  avg_latency: number;
  /**
   * Distribution of usage by model. Key is `model_name`, value is either a
   * count of spans or a fractional share (consumer should document meaning).
   */
  model_distribution: { [modelName: string]: number };
  /** Time period covered by this aggregate. ISO 8601 strings. */
  time_period: {
    /** Inclusive start timestamp (ISO 8601). */
    start_time: string;
    /** Inclusive or exclusive end timestamp (ISO 8601). */
    end_time: string;
  };
}

/**
 * Single timeseries point for a named metric.
 */
export interface GenAITimeseriesPoint {
  /** ISO 8601 timestamp for the point. */
  timestamp: string;
  /** Metric name (e.g. "input_tokens", "latency_ms", "cost"). */
  metric_name: string;
  /** Numeric value for the metric at this timestamp. */
  value: number;
}

/**
 * Response shape for timeseries endpoints used by the UI.
 */
export interface GenAITimeseriesResponse {
  /** Ordered list of timeseries points. */
  points: GenAITimeseriesPoint[];
  /** Labels used for chart axes or legend (e.g. bucket labels). */
  labels: string[];
}
