import { DriftType } from "../types";
import { BinType, type PsiDriftProfile } from "./psi";
import type { BinnedPsiFeatureMetrics } from "../types";
/**
 * Mock PsiDriftProfile for UI development and testing.
 * Provides realistic bins, config, and alert settings for PSI drift monitoring.
 */
export const mockPsiDriftProfile: PsiDriftProfile = {
  features: {
    feature_a: {
      id: "feature_a",
      bins: [
        { id: 0, lower_limit: 18, upper_limit: 25, proportion: 0.15 },
        { id: 1, lower_limit: 26, upper_limit: 35, proportion: 0.35 },
        { id: 2, lower_limit: 36, upper_limit: 50, proportion: 0.3 },
        { id: 3, lower_limit: 51, upper_limit: null, proportion: 0.2 },
      ],
      timestamp: "2025-10-13T08:00:00Z",
      bin_type: BinType.Numeric,
    },
    feature_b: {
      id: "feature_b",
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
        feature_a: { "2025-10-13T08:00:00Z": 30, "2025-10-13T09:00:00Z": 32 },
        feature_b: {
          "2025-10-13T08:00:00Z": 0.5,
          "2025-10-13T09:00:00Z": 0.52,
        },
      },
    },
    targets: ["feature_a", "feature_b"],
    alert_config: {
      dispatch_config: {
        Console: { enabled: true },
        Slack: { channel: "#psi-alerts" },
      },
      schedule: "0 */12 * * *", // Every 12 hours
      features_to_monitor: ["feature_a", "feature_b"],
      threshold: {
        Normal: { alpha: 0.05 },
      },
    },
  },
  scouter_version: "1.2.0",
};

export const mockPsiMetrics: BinnedPsiFeatureMetrics = {
  features: {
    feature_a: {
      created_at: [
        "2025-03-25 00:43:59",
        "2025-03-26 10:00:00",
        "2025-03-27 11:00:00",
        "2025-03-28 12:00:00",
        "2025-03-29 12:00:00",
      ],
      psi: [0.05, 0.07, 0.04, 0.1, 0.05],
      overall_psi: 0.053,
      bins: {
        0: 0.1,
        1: 0.2,
        2: 0.3,
        3: 0.25,
        4: 0.15,
      },
    },
    feature_b: {
      created_at: [
        "2025-03-25 00:43:59",
        "2025-03-25 01:43:59",
        "2025-03-25 02:43:59",
        "2025-03-25 03:43:59",
        "2025-03-25 04:43:59",
        "2025-03-25 05:43:59",
        "2025-03-25 06:43:59",
        "2025-03-25 07:43:59",
        "2025-03-25 08:43:59",
        "2025-03-25 09:43:59",
      ],
      psi: [1, 2, 3, 4, 5, 1, 2, 3, 4, 5],
      overall_psi: 0.053,
      bins: {
        0: 0.1,
        1: 0.2,
        2: 0.3,
        3: 0.25,
        4: 0.15,
      },
    },
  },
};
