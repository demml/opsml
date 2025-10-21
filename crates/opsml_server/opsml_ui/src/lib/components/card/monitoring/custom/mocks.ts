import { DriftType } from "../types";
import { AlertThreshold, type CustomDriftProfile } from "./custom";
import type { BinnedMetrics } from "../types";
/**
 * Mock CustomDriftProfile for UI development and testing.
 * Includes realistic metric values, config, and alert conditions.
 */
export const mockCustomDriftProfile: CustomDriftProfile = {
  metrics: {
    custom: 0.94,
    f1_score: 0.88,
    latency_ms: 250,
  },
  config: {
    sample_size: 100,
    sample: true,
    space: "services",
    name: "api_monitor",
    version: "2.1.0",
    drift_type: DriftType.Custom,
    alert_config: {
      dispatch_config: {
        Console: { enabled: true },
        Slack: { channel: "#custom-alerts" },
      },
      schedule: "0 */4 * * *", // Every 4 hours
      alert_conditions: {
        custom: {
          alert_threshold: AlertThreshold.Below,
          alert_threshold_value: 0.9,
        },
        f1_score: {
          alert_threshold: AlertThreshold.Above,
          alert_threshold_value: 0.85,
        },
        latency_ms: {
          alert_threshold: AlertThreshold.Below,
          alert_threshold_value: 1000,
        },
      },
    },
  },
  scouter_version: "1.0.0",
};

export const mockCustomMetrics: BinnedMetrics = {
  metrics: {
    custom: {
      metric: "custom",
      created_at: [
        "2025-03-25 00:43:59",
        "2025-03-26 10:00:00",
        "2025-03-27 11:00:00",
        "2025-03-28 12:00:00",
        "2025-03-29 12:00:00",
      ],
      stats: [
        {
          avg: 0.95,
          lower_bound: 0.92,
          upper_bound: 0.98,
        },
        {
          avg: 0.94,
          lower_bound: 0.91,
          upper_bound: 0.97,
        },
        {
          avg: 0.96,
          lower_bound: 0.93,
          upper_bound: 0.99,
        },
        {
          avg: 0.9,
          lower_bound: 0.93,
          upper_bound: 0.99,
        },
        {
          avg: 0.4,
          lower_bound: 0.93,
          upper_bound: 0.99,
        },
      ],
    },
    f1_score: {
      metric: "f1_score",
      created_at: [
        "2024-03-26T10:00:00",
        "2024-03-26T11:00:00",
        "2024-03-26T12:00:00",
      ],
      stats: [
        {
          avg: 0.88,
          lower_bound: 0.85,
          upper_bound: 0.91,
        },
        {
          avg: 0.87,
          lower_bound: 0.84,
          upper_bound: 0.9,
        },
        {
          avg: 0.89,
          lower_bound: 0.86,
          upper_bound: 0.92,
        },
      ],
    },
    latency_ms: {
      metric: "latency_ms",
      created_at: [
        "2024-03-26T10:00:00",
        "2024-03-26T11:00:00",
        "2024-03-26T12:00:00",
      ],
      stats: [
        {
          avg: 150.5,
          lower_bound: 145.0,
          upper_bound: 156.0,
        },
        {
          avg: 148.2,
          lower_bound: 143.5,
          upper_bound: 153.0,
        },
        {
          avg: 152.8,
          lower_bound: 147.2,
          upper_bound: 158.4,
        },
      ],
    },
  },
};
