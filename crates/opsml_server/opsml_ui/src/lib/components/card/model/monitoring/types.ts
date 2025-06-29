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

export interface PsiNormalThreshold {
  alpha: number;
}

export interface PsiChiSquareThreshold {
  alpha: number;
}

export interface PsiFixedThreshold {
  threshold: number;
}

export interface PsiThreshold {
  Normal?: PsiNormalThreshold;
  ChiSquare?: PsiChiSquareThreshold;
  Fixed?: PsiFixedThreshold;
}

export function getPsiThresholdKeyValue(threshold: PsiThreshold): {
  type: string;
  value: number;
} {
  if (threshold.Normal) {
    return { type: "Normal", value: threshold.Normal.alpha };
  } else if (threshold.ChiSquare) {
    return { type: "ChiSquare", value: threshold.ChiSquare.alpha };
  } else if (threshold.Fixed) {
    return { type: "Fixed", value: threshold.Fixed.threshold };
  }
  throw new Error("Invalid PsiThreshold configuration");
}

export function updatePsiThreshold(type: string, value: number): PsiThreshold {
  const numericValue = Number(value);

  if (isNaN(numericValue)) {
    throw new Error(`Invalid numeric value: ${value}`);
  }

  switch (type) {
    case "Normal":
      return { Normal: { alpha: numericValue } };
    case "ChiSquare":
      return { ChiSquare: { alpha: numericValue } };
    case "Fixed":
      return { Fixed: { threshold: numericValue } };
    default:
      throw new Error(`Unknown threshold type: ${type}`);
  }
}

// Add these type guard functions
export function hasConsoleConfig(config: AlertDispatchConfig): boolean {
  return !!config.Console;
}

export function hasSlackConfig(config: AlertDispatchConfig): boolean {
  return !!config.Slack;
}

export function hasOpsGenieConfig(config: AlertDispatchConfig): boolean {
  return !!config.OpsGenie;
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
  profile_uri: string;
  request: ProfileRequest;
}

export type UpdateResponse = {
  uid: string;
  status: string;
};
