import { string } from "zod";

export enum AlertDispatchType {
  Slack = "Slack",
  Console = "Console",
  OpsGenie = "OpsGenie",
}

export enum DriftType {
  Spc = "Spc",
  Psi = "Psi",
  Custom = "Custom",
}

export interface FeatureMap {
  features: Record<string, Record<string, number>>;
}

export enum TimeInterval {
  FiveMinutes = "FiveMinutes",
  FifteenMinutes = "FifteenMinutes",
  ThirtyMinutes = "ThirtyMinutes",
  OneHour = "OneHour",
  ThreeHours = "ThreeHours",
  SixHours = "SixHours",
  TwelveHours = "TwelveHours",
  TwentyFourHours = "TwentyFourHours",
  TwoDays = "TwoDays",
  FiveDays = "FiveDays",
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

// Add these type guard functions
export function hasConsoleConfig(config: AlertDispatchConfig): boolean {
  return config.Console !== undefined;
}

export function hasSlackConfig(config: AlertDispatchConfig): boolean {
  return config.Slack !== undefined;
}

export function hasOpsGenieConfig(config: AlertDispatchConfig): boolean {
  return config.OpsGenie !== undefined;
}

export interface SpcDriftFeature {
  created_at: string[]; // Array of ISO datetime strings
  values: number[]; // Array of floating point numbers
}

export interface BinnedSpcFeatureMetrics {
  features: { [key: string]: SpcDriftFeature }; // Map of string to SpcDriftFeature
}

export interface BinnedPsiMetric {
  created_at: string[]; // Array of ISO datetime strings
  psi: number[]; // Array of PSI values
  overall_psi: number; // Single PSI value
  bins: { [key: number]: number }; // Map of bin index to value
}

export interface BinnedPsiFeatureMetrics {
  features: { [key: string]: BinnedPsiMetric }; // Map of feature name to BinnedPsiMetric
}

export interface BinnedCustomMetricStats {
  avg: number;
  lower_bound: number;
  upper_bound: number;
}

export interface BinnedCustomMetric {
  metric: string;
  created_at: string[]; // Array of ISO datetime strings
  stats: BinnedCustomMetricStats[];
}

export interface BinnedCustomMetrics {
  metrics: { [key: string]: BinnedCustomMetric };
}

export interface DriftRequest {
  name: string;
  space: string;
  version: string;
  time_interval: TimeInterval;
  max_data_points: number;
  drift_type: DriftType;
  begin_custom_datetime?: string;
  end_custom_datetime?: string;
}

export type DriftMetrics = {
  [DriftType.Spc]: BinnedSpcFeatureMetrics;
  [DriftType.Psi]: BinnedPsiFeatureMetrics;
  [DriftType.Custom]: BinnedCustomMetrics;
};

export interface BinnedDriftMap extends Partial<DriftMetrics> {}

export type MetricData =
  | SpcDriftFeature
  | BinnedPsiMetric
  | BinnedCustomMetric
  | null;

export interface ProfileRequest {
  space: string;
  drift_type: DriftType;
  profile: string;
}

export interface UpdateProfileRequest {
  uid: string;
  request: ProfileRequest;
}

export type UpdateResponse = {
  uid: string;
  status: string;
};
