import { mockOpenAIPrompt, mockGeminiPrompt } from "$lib/components/genai/mock";
import { DriftType, type AlertDispatchConfig } from "../types";
import {
  AlertThreshold,
  type LLMDriftProfile,
  type LLMDriftConfig,
  type LLMMetric,
  type LLMAlertConfig,
  type LLMMetricAlertCondition,
} from "./llm";

/**
 * Mock LLMDriftProfile for UI development and testing.
 * Includes realistic metrics, config, and alert conditions for LLM drift monitoring.
 */
export const mockLLMDriftProfile: LLMDriftProfile = {
  metrics: [
    {
      name: "toxicity_score",
      value: 0.12,
      prompt: mockOpenAIPrompt,
      alert_condition: {
        alert_threshold: AlertThreshold.Above,
        alert_threshold_value: 0.1,
      },
    },
    {
      name: "coherence_score",
      value: 0.85,
      prompt: mockGeminiPrompt,
      alert_condition: {
        alert_threshold: AlertThreshold.Below,
        alert_threshold_value: 0.8,
      },
    },
  ],
  metric_names: ["toxicity_score", "coherence_score"],
  config: {
    sample_rate: 50,
    space: "llm-services",
    name: "summarizer",
    version: "3.0.0",
    drift_type: DriftType.LLM,
    alert_config: {
      dispatch_config: {
        Console: { enabled: true },
        Slack: { channel: "#llm-alerts" },
      },
      schedule: "0 */2 * * *", // Every 2 hours
      alert_conditions: {
        toxicity_score: {
          alert_threshold: AlertThreshold.Above,
          alert_threshold_value: 0.1,
        },
        coherence_score: {
          alert_threshold: AlertThreshold.Below,
          alert_threshold_value: 0.8,
        },
      },
    },
  },
  scouter_version: "2.0.0",
};
