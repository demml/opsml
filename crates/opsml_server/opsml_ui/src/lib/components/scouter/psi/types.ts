import type { AlertDispatchConfig, DriftType, FeatureMap } from "../types";

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

export interface BinnedPsiMetric {
  created_at: string[]; // Array of ISO datetime strings
  psi: number[]; // Array of PSI values
  overall_psi: number; // Single PSI value
  bins: { [key: number]: number }; // Map of bin index to value
}

export interface BinnedPsiFeatureMetrics {
  features: { [key: string]: BinnedPsiMetric }; // Map of feature name to BinnedPsiMetric
}

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
  uid: string;
  feature_map: FeatureMap;
  alert_config: PsiAlertConfig;
  targets: string[];
  drift_type: DriftType;
}

export interface PsiAlertConfig {
  dispatch_config: AlertDispatchConfig;
  schedule: string;
  features_to_monitor: string[];
  threshold: PsiThreshold;
}
