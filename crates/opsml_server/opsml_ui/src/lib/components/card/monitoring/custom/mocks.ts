import { DriftType } from "../types";
import { AlertThreshold, type CustomDriftProfile } from "./custom";

/**
 * Mock CustomDriftProfile for UI development and testing.
 * Includes realistic metric values, config, and alert conditions.
 */
export const mockCustomDriftProfile: CustomDriftProfile = {
  metrics: {
    response_time: 320,
    api_errors: 5,
    user_count: 1200,
  },
  config: {
    sample_size: 100,
    sample: true,
    space: "services",
    name: "api_monitor",
    version: "2.1.0",
    drift_type: DriftType.Custom,
    alert_config: {
      dispatch_config: {
        Console: { enabled: true },
        Slack: { channel: "#custom-alerts" },
      },
      schedule: "0 */4 * * *", // Every 4 hours
      alert_conditions: {
        response_time: {
          alert_threshold: AlertThreshold.Above,
          alert_threshold_value: 300,
        },
        api_errors: {
          alert_threshold: AlertThreshold.Above,
          alert_threshold_value: 10,
        },
        user_count: {
          alert_threshold: AlertThreshold.Below,
          alert_threshold_value: 1000,
        },
      },
    },
  },
  scouter_version: "1.0.0",
};
