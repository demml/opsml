import type {
  BinnedMetrics,
  BinnedPsiFeatureMetrics,
  BinnedSpcFeatureMetrics,
  LLMDriftServerRecord,
  LLMPageResponse,
  PaginationCursor,
} from "./types";
import { Status } from "./types";
import type { Alert } from "./alert/types";

const sampleCustomMetrics: BinnedMetrics = {
  metrics: {
    custom: {
      metric: "custom",
      created_at: [
        "2025-03-25 00:43:59",
        "2025-03-26 10:00:00",
        "2025-03-27 11:00:00",
        "2025-03-28 12:00:00",
        "2025-03-29 12:00:00",
      ],
      stats: [
        {
          avg: 0.95,
          lower_bound: 0.92,
          upper_bound: 0.98,
        },
        {
          avg: 0.94,
          lower_bound: 0.91,
          upper_bound: 0.97,
        },
        {
          avg: 0.96,
          lower_bound: 0.93,
          upper_bound: 0.99,
        },
        {
          avg: 0.9,
          lower_bound: 0.93,
          upper_bound: 0.99,
        },
        {
          avg: 0.4,
          lower_bound: 0.93,
          upper_bound: 0.99,
        },
      ],
    },
    f1_score: {
      metric: "f1_score",
      created_at: [
        "2024-03-26T10:00:00",
        "2024-03-26T11:00:00",
        "2024-03-26T12:00:00",
      ],
      stats: [
        {
          avg: 0.88,
          lower_bound: 0.85,
          upper_bound: 0.91,
        },
        {
          avg: 0.87,
          lower_bound: 0.84,
          upper_bound: 0.9,
        },
        {
          avg: 0.89,
          lower_bound: 0.86,
          upper_bound: 0.92,
        },
      ],
    },
    latency_ms: {
      metric: "latency_ms",
      created_at: [
        "2024-03-26T10:00:00",
        "2024-03-26T11:00:00",
        "2024-03-26T12:00:00",
      ],
      stats: [
        {
          avg: 150.5,
          lower_bound: 145.0,
          upper_bound: 156.0,
        },
        {
          avg: 148.2,
          lower_bound: 143.5,
          upper_bound: 153.0,
        },
        {
          avg: 152.8,
          lower_bound: 147.2,
          upper_bound: 158.4,
        },
      ],
    },
  },
};

const sampleLLMMetrics: BinnedMetrics = {
  metrics: {
    reformulation_quality: {
      metric: "reformulation_quality",
      created_at: [
        "2025-03-25 00:43:59",
        "2025-03-26 10:00:00",
        "2025-03-27 11:00:00",
        "2025-03-28 12:00:00",
        "2025-03-29 12:00:00",
      ],
      stats: [
        {
          avg: 0.95,
          lower_bound: 0.92,
          upper_bound: 0.98,
        },
        {
          avg: 0.94,
          lower_bound: 0.91,
          upper_bound: 0.97,
        },
        {
          avg: 0.96,
          lower_bound: 0.93,
          upper_bound: 0.99,
        },
        {
          avg: 0.9,
          lower_bound: 0.93,
          upper_bound: 0.99,
        },
        {
          avg: 0.4,
          lower_bound: 0.93,
          upper_bound: 0.99,
        },
      ],
    },
    coherence: {
      metric: "coherence",
      created_at: [
        "2024-03-26T10:00:00",
        "2024-03-26T11:00:00",
        "2024-03-26T12:00:00",
      ],
      stats: [
        {
          avg: 0.88,
          lower_bound: 0.85,
          upper_bound: 0.91,
        },
        {
          avg: 0.87,
          lower_bound: 0.84,
          upper_bound: 0.9,
        },
        {
          avg: 0.89,
          lower_bound: 0.86,
          upper_bound: 0.92,
        },
      ],
    },
  },
};

const sampleSpcMetrics: BinnedSpcFeatureMetrics = {
  features: {
    col_0: {
      created_at: [
        "2025-03-25 00:43:59",
        "2025-03-26 10:00:00",
        "2025-03-27 11:00:00",
        "2025-03-28 12:00:00",
        "2025-03-29 12:00:00",
      ],
      values: [100, 105, 200, 1025, 101],
    },
    col_1: {
      created_at: [
        "2025-03-25 00:43:59",
        "2025-03-26 10:00:00",
        "2025-03-27 11:00:00",
        "2025-03-28 12:00:00",
        "2025-03-29 12:00:00",
      ],
      values: [100, 105, 200, 1025, 101],
    },
  },
};

const samplePsiMetrics: BinnedPsiFeatureMetrics = {
  features: {
    col_0: {
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
    col_1: {
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

export {
  sampleSpcMetrics,
  samplePsiMetrics,
  sampleCustomMetrics,
  sampleLLMMetrics,
};

export const sampleAlerts: Alert[] = [
  {
    created_at: "2024-03-28 10:30:00",
    name: "credit_model",
    space: "models",
    version: "1.0.0",
    entity_name: "credit_score",
    alert: { type: "drift_detected", message: "PSI value exceeded threshold" },
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
    alert: { type: "spc_violation", message: "Value outside control limits" },
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
    alert: { type: "custom_metric", message: "Metric below threshold" },
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
    alert: { type: "drift_detected", message: "Distribution shift detected" },
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
    alert: { type: "spc_violation", message: "Consecutive points above mean" },
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
    alert: { type: "psi_threshold", message: "PSI above 0.2" },
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
    alert: { type: "custom_metric", message: "Accuracy below target" },
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
    alert: { type: "drift_detected", message: "Significant feature drift" },
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
    alert: { type: "spc_violation", message: "Point beyond 3 sigma" },
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
    alert: { type: "custom_metric", message: "Data freshness warning" },
    id: 10,
    drift_type: "custom",
    active: true,
  },
];

function randomStatus(): Status {
  const statuses = [
    Status.Pending,
    Status.Processing,
    Status.Processed,
    Status.Failed,
  ];
  return statuses[Math.floor(Math.random() * statuses.length)];
}

function randomDate(offsetDays: number = 0): string {
  const date = new Date();
  date.setDate(date.getDate() - offsetDays);
  return date.toISOString();
}

export const mockLLMDriftServerRecords: LLMDriftServerRecord[] = Array.from(
  { length: 30 },
  (_, i) => ({
    created_at: randomDate(30 - i),
    space: `space_${(i % 5) + 1}`,
    name: `card_${(i % 10) + 1}`,
    version: `v${(i % 3) + 1}.0.${i}`,
    prompt: i % 2 === 0 ? `Prompt for card_${(i % 10) + 1}` : undefined,
    context: `Context for card_${(i % 10) + 1}`,
    status: randomStatus(),
    id: i + 1,
    uid: `uid_${i + 1}`,
    score: (Math.random() * 100).toFixed(2),
    updated_at: randomDate(29 - i),
    processing_started_at: i % 3 === 0 ? randomDate(30 - i) : undefined,
    processing_ended_at: i % 4 === 0 ? randomDate(29 - i) : undefined,
  })
);

let paginationCursor: PaginationCursor = {
  id: mockLLMDriftServerRecords.length,
};
export const mockLLMDriftPageResponse: LLMPageResponse = {
  items: mockLLMDriftServerRecords,
  next_cursor: paginationCursor,
  has_more: true,
};
