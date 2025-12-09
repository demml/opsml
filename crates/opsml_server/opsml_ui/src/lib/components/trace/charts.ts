import type { ChartConfiguration } from "chart.js";
import type { TraceMetricBucket } from "./types";
import { buildTimeChart } from "$lib/components/viz/timeseries";
import type { ChartjsLineDataset } from "$lib/components/viz/utils";
import { generateColors } from "$lib/components/viz/utils";

/**
 * Create bar chart for trace counts
 */
export function createTraceCountChart(
  buckets: TraceMetricBucket[]
): ChartConfiguration {
  const labels = buckets.map((b) => new Date(b.bucket_start));
  const data = buckets.map((b) => b.trace_count);

  const datasets: ChartjsLineDataset[] = [
    {
      label: "Traces",
      data: data,
      borderColor: generateColors(2)[1],
      backgroundColor: generateColors(2, 0.2)[1],
      pointRadius: 2,
      fill: true,
    },
  ];

  return buildTimeChart(
    labels,
    datasets,
    "Time",
    "Requests",
    false,
    undefined,
    "line",
    false,
    false,
    0,
    0
  );
}

/**
 * Create bar chart for error rates
 */
export function createErrorRateChart(
  buckets: TraceMetricBucket[]
): ChartConfiguration {
  const labels = buckets.map((b) => new Date(b.bucket_start));
  const data = buckets.map((b) => b.error_rate * 100);

  const datasets: ChartjsLineDataset[] = [
    {
      label: "Errors",
      data: data,
      borderColor: generateColors(6)[5],
      backgroundColor: generateColors(6, 0.2)[5],
      pointRadius: 2,
      fill: true,
    },
  ];

  return buildTimeChart(
    labels,
    datasets,
    "Time",
    "Requests",
    false,
    undefined,
    "line",
    false,
    false,
    0,
    0
  );
}

/**
 * Create line chart for latency percentiles
 */
export function createLatencyChart(
  buckets: TraceMetricBucket[]
): ChartConfiguration {
  const labels = buckets.map((b) => new Date(b.bucket_start));
  const p50 = buckets.map((b) => b.p50_duration_ms) as number[];
  const p95 = buckets.map((b) => b.p95_duration_ms) as number[];
  const p99 = buckets.map((b) => b.p99_duration_ms) as number[];
  const colors = generateColors(3);
  const backgroundColors = generateColors(3, 0.2);

  const datasets: ChartjsLineDataset[] = [
    {
      label: "P50",
      data: p50,
      borderColor: colors[0],
      backgroundColor: backgroundColors[0],
      pointRadius: 2,
      fill: true,
    },
    {
      label: "P95",
      data: p95,
      borderColor: colors[1],
      backgroundColor: backgroundColors[1],
      pointRadius: 2,
      fill: true,
    },
    {
      label: "P99",
      data: p99,
      borderColor: colors[2],
      backgroundColor: backgroundColors[2],
      pointRadius: 2,
      fill: true,
    },
  ];

  return buildTimeChart(
    labels,
    datasets,
    "Time",
    "Requests",
    true,
    undefined,
    "line",
    false,
    false,
    0,
    0
  );
}
