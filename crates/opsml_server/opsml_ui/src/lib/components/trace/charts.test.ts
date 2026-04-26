import { describe, expect, it } from "vitest";
import { createStackedTraceCountChart } from "./charts";
import type { TraceMetricBucket } from "./types";

const buckets: TraceMetricBucket[] = [
  {
    bucket_start: "2026-01-01T00:00:00Z",
    trace_count: 10,
    avg_duration_ms: 100,
    p50_duration_ms: 80,
    p95_duration_ms: 150,
    p99_duration_ms: 180,
    error_rate: 0.2,
  },
];

describe("createStackedTraceCountChart", () => {
  it("uses semantic success and error chart colors", () => {
    const config = createStackedTraceCountChart(buckets);
    const datasets = config.data?.datasets ?? [];

    expect(datasets).toHaveLength(2);
    expect(datasets[0]?.label).toBe("Success");
    expect(datasets[0]?.backgroundColor).toBe("rgba(95, 214, 141, 0.85)");
    expect(datasets[1]?.label).toBe("Error");
    expect(datasets[1]?.backgroundColor).toBe("rgba(254, 108, 107, 0.9)");
  });
});
