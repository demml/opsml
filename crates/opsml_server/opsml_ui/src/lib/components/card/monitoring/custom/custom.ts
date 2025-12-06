import { DriftType, type AlertDispatchConfig } from "../types";

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
  alert_conditions?: Record<string, CustomMetricAlertCondition>;
}

export interface CustomMetricAlertCondition {
  alert_threshold: AlertThreshold; // You'll need to define AlertThreshold type
  alert_threshold_value?: number;
}

export interface AlertConditionInfo {
  alert_threshold: AlertThreshold;
  alert_threshold_value?: number;
}
export function getCustomAlertCondition(
  config: CustomMetricDriftConfig,
  name: string
): AlertConditionInfo | null {
  if (!config.alert_config.alert_conditions) {
    return null;
  }

  const condition = config.alert_config.alert_conditions[name];
  if (!condition) {
    return null;
  }

  return {
    alert_threshold: condition.alert_threshold,
    alert_threshold_value: condition.alert_threshold_value,
  };
}
