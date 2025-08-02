import type { Prompt } from "$lib/components/card/card_interfaces/promptcard";
import { DriftType, type AlertDispatchConfig } from "../types";

export enum AlertThreshold {
  Below = "Below",
  Above = "Above",
  Between = "Between",
}

export interface LLMMetricAlertCondition {
  alert_threshold: AlertThreshold;
  alert_threshold_value?: number;
}

export interface LLMMetric {
  name: string;
  value: number;
  prompt?: Prompt;
  alert_condition: LLMMetricAlertCondition;
}

export interface LLMDriftConfig {
  sample_rate: number;
  space: string;
  name: string;
  version: string;
  alert_config: LLMAlertConfig;
  drift_type: DriftType;
}

export interface LLMDriftProfile {
  config: LLMDriftConfig;
  metrics: LLMMetric[];
  metric_names: string[];
  scouter_version: string;
}

export interface LLMAlertConfig {
  dispatch_config: AlertDispatchConfig;
  schedule: string;
  alert_conditions?: Record<string, LLMMetricAlertCondition>;
}

export function getLLMAlertCondition(
  config: LLMDriftConfig,
  name: string
): LLMMetricAlertCondition | null {
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
