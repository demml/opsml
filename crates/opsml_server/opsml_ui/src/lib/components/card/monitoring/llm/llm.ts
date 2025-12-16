import type { Prompt } from "$lib/components/genai/types";
import type { DateTime } from "$lib/types";
import {
  DriftType,
  type AlertDispatchConfig,
  type RecordCursor,
  type ServiceInfo,
} from "../types";

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
  uid: string;
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

export enum Status {
  All = "All",
  Pending = "pending",
  Processing = "processing",
  Processed = "processed",
  Failed = "failed",
}

export interface LLMDriftServerRecord {
  created_at: string; // ISO datetime string
  space: string;
  name: string;
  version: string;
  prompt?: string;
  context: string;
  status: Status;
  id: number;
  uid: string;
  score: any; // This is an object (serde_json::Value in Rust)
  updated_at: string; // ISO datetime string
  processing_started_at?: string; // ISO datetime string
  processing_ended_at?: string; // ISO datetime string
  processing_duration?: number; // Duration in seconds
}

export interface LLMDriftRecordPaginationRequest {
  service_info: ServiceInfo;
  status?: Status;
  limit?: number;
  cursor_created_at?: DateTime;
  cursor_id?: number;
  direction?: "next" | "previous";
}

export interface LLMPageResponse {
  items: LLMDriftServerRecord[];
  has_next: boolean;
  next_cursor?: RecordCursor;
  has_previous: boolean;
  previous_cursor?: RecordCursor;
}
