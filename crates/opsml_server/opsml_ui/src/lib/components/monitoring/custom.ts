import {
  DriftType,
  AlertDispatchType,
  type FeatureMap,
  type AlertDispatchConfig,
} from "./types";

export enum AlertThreshold {
  Below = "Below",
  Above = "Above",
  Between = "Between",
}

export interface CustomDriftProfile {
  config: CustomMetricDriftConfig;
  metrics: Record<string, number>;
  scouter_version: string;
}

export interface CustomMetricDriftConfig {
  sample_size: number;
  sample: boolean;
  repository: string;
  name: string;
  version: string;
  alert_config: CustomMetricAlertConfig;
  drift_type: DriftType; // You'll need to define DriftType enum
}

export interface CustomMetricAlertConfig {
  dispatch_config: AlertDispatchConfig;
  schedule: string;
  alert_conditions?: Record<string, CustomMetricAlertCondition>;
}

export interface CustomMetricAlertCondition {
  alert_threshold: AlertThreshold; // You'll need to define AlertThreshold type
  alert_threshold_value?: number;
}
