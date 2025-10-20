import type { Metric } from "../card_interfaces/experimentcard";
import type { HardwareMetrics } from "./types";

const BYTES_TO_MB = 1024 * 1024;

// Parse the metrics into a map
export function parseMetricsToMap(metrics: Metric[]): Map<string, Metric[]> {
  const metricsMap = new Map<string, Metric[]>();
  for (const metric of metrics) {
    const metricName = metric.name;
    if (!metricsMap.has(metricName)) {
      metricsMap.set(metricName, []);
    }
    metricsMap.get(metricName)?.push(metric);
  }
  return metricsMap;
}

/**
 * Extract all hardware metrics with timestamps in a single pass for UI rendering
 * Converts network bytes to kilobytes
 */
export function extractAllHardwareMetrics(metrics: HardwareMetrics[]): {
  createdAt: string[];
  cpuUtilization: number[];
  usedPercentMemory: number[];
  networkMbRecv: number[];
  networkMbSent: number[];
} {
  return {
    createdAt: metrics.map((m) => m.created_at),
    cpuUtilization: metrics.map((m) => m.cpu.cpu_percent_utilization),
    usedPercentMemory: metrics.map((m) => m.memory.used_percent_memory),
    networkMbRecv: metrics.map((m) => m.network.bytes_recv / BYTES_TO_MB),
    networkMbSent: metrics.map((m) => m.network.bytes_sent / BYTES_TO_MB),
  };
}
