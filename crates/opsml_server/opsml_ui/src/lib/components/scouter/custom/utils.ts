import type { AlertCondition } from "../types";
import type { CustomMetricDriftConfig } from "./types";
export function getCustomAlertCondition(
  config: CustomMetricDriftConfig,
  name: string
): AlertCondition | null {
  if (!config.alert_config.alert_conditions) {
    return null;
  }

  const condition = config.alert_config.alert_conditions[name];
  if (!condition) {
    return null;
  }

  return {
    alert_threshold: condition.alert_threshold,
    baseline_value: condition.baseline_value,
  };
}
