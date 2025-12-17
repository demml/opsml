import { DriftType } from "./types";
import { mockPsiDriftProfile } from "./psi/mocks";
import { mockCustomDriftProfile } from "./custom/mocks";
import { mockSpcDriftProfile } from "./spc/mocks";
import { mockLLMDriftProfile } from "./llm/mocks";
import type { UiProfile } from "./utils";
import type {
  Alert,
  DriftAlertPaginationRequest,
  DriftAlertPaginationResponse,
} from "./alert/types";

/**
 * Mock DriftProfileResponse for testing and UI development.
 * Each profile uses a realistic mock and a sample URI.
 */
export const mockDriftProfileResponse: Record<DriftType, UiProfile> = {
  [DriftType.Spc]: {
    profile_uri: "/profiles/spc/mock.json",
    profile: {
      Spc: mockSpcDriftProfile,
      Psi: mockPsiDriftProfile,
      Custom: mockCustomDriftProfile,
      LLM: mockLLMDriftProfile,
    },
  },
  [DriftType.Psi]: {
    profile_uri: "/profiles/psi/mock.json",
    profile: {
      Spc: mockSpcDriftProfile,
      Psi: mockPsiDriftProfile,
      Custom: mockCustomDriftProfile,
      LLM: mockLLMDriftProfile,
    },
  },
  [DriftType.Custom]: {
    profile_uri: "/profiles/custom/mock.json",
    profile: {
      Spc: mockSpcDriftProfile,
      Psi: mockPsiDriftProfile,
      Custom: mockCustomDriftProfile,
      LLM: mockLLMDriftProfile,
    },
  },
  [DriftType.LLM]: {
    profile_uri: "/profiles/llm/mock.json",
    profile: {
      Spc: mockSpcDriftProfile,
      Psi: mockPsiDriftProfile,
      Custom: mockCustomDriftProfile,
      LLM: mockLLMDriftProfile,
    },
  },
};

const mockAlerts: Alert[] = [
  {
    created_at: "2024-03-28 10:30:00",
    name: "credit_model",
    space: "models",
    version: "1.0.0",
    entity_name: "credit_score",
    alert:
      '{ type: "drift_detected", message: "PSI value exceeded threshold" }',
    id: 1,
    drift_type: "psi",
    active: true,
  },
  {
    created_at: "2024-03-28 09:45:00",
    name: "fraud_detection",
    space: "models",
    version: "2.1.0",
    entity_name: "transaction_amount",
    alert: '{ type: "spc_violation", message: "Value outside control limits" }',
    id: 2,
    drift_type: "spc",
    active: true,
  },
  {
    created_at: "2024-03-28 09:00:00",
    name: "customer_churn",
    space: "ml_models",
    version: "1.2.3",
    entity_name: "usage_frequency",
    alert: '{ type: "custom_metric", message: "Metric below threshold" }',
    id: 3,
    drift_type: "custom",
    active: true,
  },
  {
    created_at: "2024-03-27 23:15:00",
    name: "recommendation_engine",
    space: "recsys",
    version: "3.0.1",
    entity_name: "user_engagement",
    alert: '{ type: "drift_detected", message: "Distribution shift detected" }',
    id: 4,
    drift_type: "psi",
    active: false,
  },
  {
    created_at: "2024-03-27 22:30:00",
    name: "credit_model",
    space: "models",
    version: "1.0.0",
    entity_name: "debt_ratio",
    alert:
      '{ type: "spc_violation", message: "Consecutive points above mean" }',
    id: 5,
    drift_type: "spc",
    active: true,
  },
  {
    created_at: "2024-03-27 21:45:00",
    name: "fraud_detection",
    space: "models",
    version: "2.1.0",
    entity_name: "ip_velocity",
    alert: '{ type: "psi_threshold", message: "PSI above 0.2" }',
    id: 6,
    drift_type: "psi",
    active: true,
  },
  {
    created_at: "2024-03-27 20:00:00",
    name: "price_optimization",
    space: "pricing",
    version: "1.1.0",
    entity_name: "demand_forecast",
    alert: '{ type: "custom_metric", message: "Accuracy below target" }',
    id: 7,
    drift_type: "custom",
    active: false,
  },
  {
    created_at: "2024-03-27 19:15:00",
    name: "customer_churn",
    space: "ml_models",
    version: "1.2.3",
    entity_name: "support_tickets",
    alert: '{ type: "drift_detected", message: "Significant feature drift" }',
    id: 8,
    drift_type: "psi",
    active: true,
  },
  {
    created_at: "2024-03-27 18:30:00",
    name: "recommendation_engine",
    space: "recsys",
    version: "3.0.1",
    entity_name: "click_through_rate",
    alert: '{ type: "spc_violation", message: "Point beyond 3 sigma" }',
    id: 9,
    drift_type: "spc",
    active: true,
  },
  {
    created_at: "2024-03-27 17:45:00",
    name: "price_optimization",
    space: "pricing",
    version: "1.1.0",
    entity_name: "competitor_prices",
    alert: '{ type: "custom_metric", message: "Data freshness warning" }',
    id: 10,
    drift_type: "custom",
    active: true,
  },
];

export const mockDriftAlertResponse: DriftAlertPaginationResponse = {
  items: mockAlerts,
  has_next: false,
  has_previous: false,
  next_cursor: undefined,
  previous_cursor: undefined,
};
