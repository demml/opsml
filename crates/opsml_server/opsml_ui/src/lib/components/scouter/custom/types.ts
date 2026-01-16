import type { AlertCondition, AlertDispatchConfig, DriftType } from "../types";

export interface BinnedMetricStats {
  avg: number;
  lower_bound: number;
  upper_bound: number;
}

export interface BinnedMetric {
  metric: string;
  created_at: string[]; // Array of ISO datetime strings
  stats: BinnedMetricStats[];
}

export interface BinnedMetrics {
  metrics: { [key: string]: BinnedMetric };
}

export interface CustomDriftProfile {
  config: CustomMetricDriftConfig;
  metrics: Record<string, number>;
  scouter_version: string;
}

export interface CustomMetricDriftConfig {
  sample_size: number;
  sample: boolean;
  space: string;
  name: string;
  version: string;
  uid: string;
  alert_config: CustomMetricAlertConfig;
  drift_type: DriftType;
}

export interface CustomMetricAlertConfig {
  dispatch_config: AlertDispatchConfig;
  schedule: string;
  alert_conditions?: Record<string, AlertCondition>;
}
