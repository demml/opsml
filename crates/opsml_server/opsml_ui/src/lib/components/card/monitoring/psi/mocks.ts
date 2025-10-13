import { DriftType } from "../types";
import { BinType, type PsiDriftProfile } from "./psi";

/**
 * Mock PsiDriftProfile for UI development and testing.
 * Provides realistic bins, config, and alert settings for PSI drift monitoring.
 */
export const mockPsiDriftProfile: PsiDriftProfile = {
  features: {
    age: {
      id: "age",
      bins: [
        { id: 0, lower_limit: 18, upper_limit: 25, proportion: 0.15 },
        { id: 1, lower_limit: 26, upper_limit: 35, proportion: 0.35 },
        { id: 2, lower_limit: 36, upper_limit: 50, proportion: 0.3 },
        { id: 3, lower_limit: 51, upper_limit: null, proportion: 0.2 },
      ],
      timestamp: "2025-10-13T08:00:00Z",
      bin_type: BinType.Numeric,
    },
    gender: {
      id: "gender",
      bins: [
        { id: 0, lower_limit: null, upper_limit: null, proportion: 0.55 }, // Male
        { id: 1, lower_limit: null, upper_limit: null, proportion: 0.45 }, // Female
      ],
      timestamp: "2025-10-13T08:00:00Z",
      bin_type: BinType.Binary,
    },
  },
  config: {
    space: "models",
    name: "credit_score",
    version: "1.0.0",
    drift_type: DriftType.Psi,
    feature_map: {
      features: {
        age: { "2025-10-13T08:00:00Z": 30, "2025-10-13T09:00:00Z": 32 },
        gender: { "2025-10-13T08:00:00Z": 0.5, "2025-10-13T09:00:00Z": 0.52 },
      },
    },
    targets: ["age", "gender"],
    alert_config: {
      dispatch_config: {
        Console: { enabled: true },
        Slack: { channel: "#psi-alerts" },
      },
      schedule: "0 */12 * * *", // Every 12 hours
      features_to_monitor: ["age", "gender"],
      threshold: {
        Normal: { alpha: 0.05 },
      },
    },
  },
  scouter_version: "1.2.0",
};
