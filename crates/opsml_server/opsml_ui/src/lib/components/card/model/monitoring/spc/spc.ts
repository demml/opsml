import {
  DriftType,
  AlertDispatchType,
  type FeatureMap,
  type AlertDispatchConfig,
} from "../types";

export enum AlertZone {
  Zone1 = "Zone 1",
  Zone2 = "Zone 2",
  Zone3 = "Zone 3",
  Zone4 = "Zone 4",
  NotApplicable = "NA",
}

export interface SpcAlertRule {
  rule: string;
  zones_to_monitor: AlertZone[];
}

export interface SpcDriftProfile {
  features: Record<string, SpcFeatureDriftProfile>;
  config: SpcDriftConfig;
  scouter_version: string;
}

export interface SpcFeatureDriftProfile {
  id: string;
  center: number;
  one_ucl: number;
  one_lcl: number;
  two_ucl: number;
  two_lcl: number;
  three_ucl: number;
  three_lcl: number;
  timestamp: string; // ISO DateTime string
}

export interface SpcDriftConfig {
  sample_size: number;
  sample: boolean;
  space: string;
  name: string;
  version: string;
  alert_config: SpcAlertConfig;
  feature_map: FeatureMap; // You'll need to define FeatureMap type
  targets: string[];
  drift_type: DriftType; // You'll need to define DriftType enum
}

export interface SpcAlertConfig {
  rule: SpcAlertRule; // You'll need to define SpcAlertRule type
  dispatch_config: AlertDispatchConfig;
  schedule: string;
  features_to_monitor: string[];
}
