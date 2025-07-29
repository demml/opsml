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
  scouter_version: string;
}

export interface LLMAlertConfig {
  dispatch_config: AlertDispatchConfig;
  schedule: string;
  alert_conditions?: Record<string, LLMMetricAlertCondition>;
}
