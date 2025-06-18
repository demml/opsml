import {
  DriftType,
  type FeatureMap,
  type AlertDispatchConfig,
  type PsiThreshold,
} from "../types";

export interface PsiDriftProfile {
  features: Record<string, PsiFeatureDriftProfile>;
  config: PsiDriftConfig;
  scouter_version: string;
}

export interface PsiFeatureDriftProfile {
  id: string;
  bins: Bin[];
  timestamp: string; // ISO DateTime string
  bin_type: BinType;
}

export interface Bin {
  id: number;
  lower_limit: number | null;
  upper_limit: number | null;
  proportion: number;
}

export enum BinType {
  Binary = "Binary",
  Numeric = "Numeric",
  Category = "Category",
}

export interface PsiDriftConfig {
  space: string;
  name: string;
  version: string;
  feature_map: FeatureMap; // You'll need to define FeatureMap type
  alert_config: PsiAlertConfig;
  targets: string[];
  drift_type: DriftType; // You'll need to define DriftType enum
}

export interface PsiAlertConfig {
  dispatch_config: AlertDispatchConfig;
  schedule: string;
  features_to_monitor: string[];
  threshold: PsiThreshold;
}
