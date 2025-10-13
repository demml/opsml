import { DriftType } from "$lib/components/card/monitoring/types";

import { type SpcDriftProfile } from "./spc";
import { AlertZone } from "./spc";

/**
 * Mock SpcDriftProfile for UI development and testing.
 * Includes realistic feature drift profiles, config, and alert settings.
 */
export const mockSpcDriftProfile: SpcDriftProfile = {
  features: {
    feature_a: {
      id: "feature_a",
      center: 50,
      one_ucl: 60,
      one_lcl: 40,
      two_ucl: 65,
      two_lcl: 35,
      three_ucl: 70,
      three_lcl: 30,
      timestamp: "2025-10-13T08:00:00Z",
    },
    feature_b: {
      id: "feature_b",
      center: 100,
      one_ucl: 110,
      one_lcl: 90,
      two_ucl: 115,
      two_lcl: 85,
      three_ucl: 120,
      three_lcl: 80,
      timestamp: "2025-10-13T08:00:00Z",
    },
  },
  config: {
    sample_size: 30,
    sample: true,
    space: "models",
    name: "credit_score",
    version: "1.0.0",
    drift_type: DriftType.Spc,
    feature_map: {
      features: {
        feature_a: { "2025-10-13T08:00:00Z": 52, "2025-10-13T09:00:00Z": 48 },
        feature_b: { "2025-10-13T08:00:00Z": 102, "2025-10-13T09:00:00Z": 98 },
      },
    },
    targets: ["feature_a", "feature_b"],
    alert_config: {
      rule: {
        rule: "Zone Rule",
        zones_to_monitor: [AlertZone.Zone1, AlertZone.Zone2, AlertZone.Zone3],
      },
      dispatch_config: {
        Console: { enabled: true },
        Slack: { channel: "#alerts" },
        OpsGenie: { team: "ML", priority: "high" },
      },
      schedule: "0 */6 * * *", // Every 6 hours
      features_to_monitor: ["feature_a", "feature_b"],
    },
  },
  scouter_version: "1.2.0",
};
