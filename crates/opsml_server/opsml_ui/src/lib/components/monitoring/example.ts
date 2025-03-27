import type {
  BinnedCustomMetrics,
  BinnedPsiFeatureMetrics,
  BinnedSpcFeatureMetrics,
} from "./types";

const sampleCustomMetrics: BinnedCustomMetrics = {
  metrics: {
    accuracy: {
      metric: "accuracy",
      created_at: [
        "2024-03-26T10:00:00",
        "2024-03-26T11:00:00",
        "2024-03-26T12:00:00",
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

const sampleSpcMetrics: BinnedSpcFeatureMetrics = {
  features: {
    numeric_feature_1: {
      created_at: [
        "2024-03-26T10:00:00",
        "2024-03-26T11:00:00",
        "2024-03-26T12:00:00",
      ],
      values: [0.82, 0.85, 0.89],
    },
    numeric_feature_2: {
      created_at: [
        "2024-03-26T10:00:00",
        "2024-03-26T11:00:00",
        "2024-03-26T12:00:00",
      ],
      values: [1.2, 1.4, 1.1],
    },
  },
};

const samplePsiMetrics: BinnedPsiFeatureMetrics = {
  features: {
    categorical_feature_1: {
      created_at: [
        "2024-03-26T10:00:00",
        "2024-03-26T11:00:00",
        "2024-03-26T12:00:00",
      ],
      psi: [0.05, 0.07, 0.04],
      overall_psi: 0.053,
      bins: {
        0: 0.1,
        1: 0.2,
        2: 0.3,
        3: 0.25,
        4: 0.15,
      },
    },
    categorical_feature_2: {
      created_at: [
        "2024-03-26T10:00:00",
        "2024-03-26T11:00:00",
        "2024-03-26T12:00:00",
      ],
      psi: [0.02, 0.03, 0.025],
      overall_psi: 0.025,
      bins: {
        0: 0.3,
        1: 0.4,
        2: 0.3,
      },
    },
  },
};

export { sampleSpcMetrics, samplePsiMetrics, sampleCustomMetrics };
