import type { DateTime } from "$lib/types";
import type { RegistryType } from "$lib/utils";
import type { BinnedMetric, BinnedMetrics } from "./custom/types";
import type { BinnedPsiFeatureMetrics, BinnedPsiMetric } from "./psi/types";
import type { BinnedSpcFeatureMetrics, SpcDriftFeature } from "./spc/types";

export enum DriftType {
  Spc = "Spc",
  Psi = "Psi",
  Custom = "Custom",
  GenAI = "GenAI",
}

export interface DriftProfileUri {
  root_dir: string;
  uri: string;
  drift_type: DriftType;
}

export interface FeatureMap {
  features: Record<string, Record<string, number>>;
}

export enum AlertThreshold {
  Below = "Below",
  Above = "Above",
  Between = "Between",
}

export interface AlertCondition {
  alert_threshold: AlertThreshold;
  baseline_value: number;
  delta?: number;
}

export interface ConsoleDispatchConfig {
  enabled: boolean;
}

export interface SlackDispatchConfig {
  channel: string;
}

export interface OpsGenieDispatchConfig {
  team: string;
  priority: string;
}

export interface AlertDispatchConfig {
  Console?: ConsoleDispatchConfig;
  Slack?: SlackDispatchConfig;
  OpsGenie?: OpsGenieDispatchConfig;
}

export interface ProfileRequest {
  space: string;
  drift_type: DriftType;
  profile: string;
  active: boolean;
  deactivate_others: boolean;
}

export interface UpdateProfileRequest {
  uid: string;
  profile_uri: string;
  request: ProfileRequest;
  registry_type: RegistryType;
}

export type UpdateResponse = {
  uid: string;
  status: string;
};

export interface ServiceInfo {
  space: string;
  uid: string;
}

export interface RecordCursor {
  created_at: DateTime;
  id: number;
}

export enum AlertDispatchType {
  Slack = "Slack",
  Console = "Console",
  OpsGenie = "OpsGenie",
}

/**
 * Matches: Feature, Metric, GenAI
 */
export enum EntityType {
  Feature = "Feature",
  Metric = "Metric",
  GenAI = "GenAI",
}

export enum TimeInterval {
  FifteenMinutes = "FifteenMinutes",
  ThirtyMinutes = "ThirtyMinutes",
  OneHour = "OneHour",
  FourHours = "FourHours",
  SixHours = "SixHours",
  TwelveHours = "TwelveHours",
  TwentyFourHours = "TwentyFourHours",
  SevenDays = "SevenDays",
  ThirtyDays = "ThirtyDays",
  Custom = "Custom",
}

export interface DriftRequest {
  uid: string;
  space: string;
  time_interval: TimeInterval;
  max_data_points: number;
  drift_type: DriftType;
  start_custom_datetime?: string;
  end_custom_datetime?: string;
}

export type BinnedMetricUnion =
  | BinnedSpcFeatureMetrics
  | BinnedPsiFeatureMetrics
  | BinnedMetrics;

export type MetricData =
  | SpcDriftFeature
  | BinnedPsiMetric
  | BinnedMetric
  | null;
