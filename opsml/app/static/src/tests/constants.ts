import {
  type User,
  type RunMetrics,
  type Card,
  type Artifact,
  type Parameter,
  type ModelMetadata,
  type DataCardMetadata,
  type MonitorAlert,
  type MonitorAlerts,
  type UpdateAlert,
  type AlertMetrics,
} from "$lib/scripts/types";

import {
  type DataProfile,
  type FeatureProfile,
  type NumericStats,
  type Distinct,
  type Quantiles,
  type Histogram,
  type WordStats,
  type CharStats,
  type StringStats,
} from "$lib/scripts/data/types";

export const user: User = {
  username: "test",
  security_question: "test",
  security_answer: "test",
  full_name: "test",
  email: "test",
  password: "test",
  is_active: true,
  scopes: {
    admin: true,
    delete: true,
    read: true,
    write: true,
    model_repository: ["test"],
    data_repository: ["test"],
    run_repository: ["test"],
  },
  watchlist: {
    model_repository: ["test"],
    data_repository: ["test"],
    run_repository: ["test"],
  },
};

const metricsForTable: Map<string, RunMetrics> = new Map();
metricsForTable.set("run_1", {
  accuracy: [
    {
      run_uid: "run_1",
      name: "accuracy",
      value: 0.92,
      step: 100,
      timestamp: 1593561600000,
    },
    {
      run_uid: "run_1",
      name: "accuracy",
      value: 0.95,
      step: 200,
      timestamp: 1593648000000,
    },
    {
      run_uid: "run_1",
      name: "accuracy",
      value: 0.97,
      step: 300,
      timestamp: 1593734400000,
    },
  ],
  loss: [
    {
      run_uid: "run_1",
      name: "loss",
      value: 0.25,
      step: 100,
      timestamp: 1593561600000,
    },
    {
      run_uid: "run_1",
      name: "loss",
      value: 0.18,
      step: 200,
      timestamp: 1593648000000,
    },
    {
      run_uid: "run_1",
      name: "loss",
      value: 0.12,
      step: 300,
      timestamp: 1593734400000,
    },
  ],
});

metricsForTable.set("run_2", {
  "f1-score": [
    {
      run_uid: "run_2",
      name: "f1-score",
      value: 0.88,
      step: 50,
      timestamp: 1593475200000,
    },
    {
      run_uid: "run_2",
      name: "f1-score",
      value: 0.91,
      step: 100,
      timestamp: 1593561600000,
    },
    {
      run_uid: "run_2",
      name: "f1-score",
      value: 0.93,
      step: 150,
      timestamp: 1593648000000,
    },
  ],
  precision: [
    {
      run_uid: "run_2",
      name: "precision",
      value: 0.9,
      step: 50,
      timestamp: 1593475200000,
    },
    {
      run_uid: "run_2",
      name: "precision",
      value: 0.92,
      step: 100,
      timestamp: 1593561600000,
    },
    {
      run_uid: "run_2",
      name: "precision",
      value: 0.94,
      step: 150,
      timestamp: 1593648000000,
    },
  ],
  accuracy: [
    {
      run_uid: "run_2",
      name: "precision",
      value: 0.9,
      step: 50,
      timestamp: 1593475200000,
    },
    {
      run_uid: "run_2",
      name: "precision",
      value: 0.92,
      step: 100,
      timestamp: 1593561600000,
    },
    {
      run_uid: "run_2",
      name: "precision",
      value: 0.94,
      step: 150,
      timestamp: 1593648000000,
    },
  ],
});

export { metricsForTable };

export const sampleRunMetics = metricsForTable.get("run_1")!;

export const barData = {
  data: {
    datasets: [
      {
        backgroundColor: ["rgba(82, 224, 123, 0.2)", "rgba(165, 82, 224, 0.2)"],
        borderColor: ["rgb(82, 224, 123)", "rgb(165, 82, 224)"],
        borderRadius: 2,
        borderSkipped: false,
        borderWidth: 2,
        data: [0.97, 0.12],
      },
    ],
    labels: ["accuracy", "loss"],
  },
  options: {
    layout: {
      padding: 10,
    },
    maintainAspectRatio: false,

    plugins: {
      legend: {
        display: false,
      },
      zoom: {
        pan: {
          enabled: true,
          mode: "xy",
          modifierKey: "ctrl",
        },
        zoom: {
          drag: {
            backgroundColor: "rgba(54, 162, 235, 0.3)",
            borderColor: "rgb(54, 162, 235)",
            borderWidth: 1,
            enabled: true,
          },
          mode: "xy",
        },
      },
    },
    responsive: true,
    scales: {
      x: {
        ticks: {
          maxTicksLimit: 30,
        },
        title: {
          display: true,
          text: "Metrics",
        },
      },
      y: {
        grace: "2%",
        ticks: {
          maxTicksLimit: 30,
        },
        title: {
          display: true,
          text: "Values",
        },
      },
    },
  },
  type: "bar",
};

const tags = new Map();
tags.set("test", "test");

const artifact_uris: Map<string, Artifact> = new Map();
artifact_uris.set("test", {
  local_path: "test",
  remote_path: "test",
  name: "test",
});

export const sampleParameters = [
  {
    name: "test",
    run_uid: "test",
    value: 1,
    step: 1,
    timestamp: 1,
  },
];

const runParams: Map<string, Parameter[]> = new Map();
runParams.set("test", sampleParameters);

export const sampleRunCard = {
  name: "test",
  repository: "test",
  version: "1.0.0",
  uid: "test",
  contact: "test",
  datacard_uids: ["test"],
  modelcard_uids: ["test"],
  pipelinecard_uid: undefined,
  parameters: runParams,
  artifact_uris: artifact_uris,
  tags: tags,
  project: "test",
  compute_environment: {
    cpu_count: 1,
    memory: 1,
    disk_space: 10,
    system: "linux",
    release: "1.20.0",
    architecture_bits: "64",
    python_version: "3.11.0",
    python_compiler: "gcc",
    gpu_count: 0,
    gpu_devices: [],
    gpu_device_memory: new Map(),
  },
};

export const sampleMetrics = [
  {
    run_uid: "test",
    name: "test",
    value: 1,
    step: 1,
    timestamp: 1,
  },
];

const sampleCards: Map<string, Card> = new Map();

sampleCards.set("card1", {
  date: "2021-09-01T00:00:00Z",
  uid: "test",
  repository: "test",
  contact: "test",
  name: "test",
  version: "0.1.0",
  timestamp: 1711563309,
  tags: new Map(),
  runcard_uid: "test",
  datacard_uid: "test",
  modelcard_uids: ["test"],
  datacard_uids: ["test"],
});

sampleCards.set("card2", {
  date: "2021-09-01T00:00:00Z",
  uid: "test",
  repository: "test",
  contact: "test",
  name: "test",
  version: "0.1.0",
  timestamp: 1711563309,
  tags: new Map(),
  runcard_uid: "test",
  datacard_uid: "test",
  modelcard_uids: ["test"],
  datacard_uids: ["test"],
});

export { sampleCards };

export const sampleCard = sampleCards.get("card1")!;

export const sampleModelMetadata: ModelMetadata = {
  model_name: "test",
  model_class: "test",
  model_type: "test",
  model_interface: "test",
  model_uri: "test",
  model_version: "test",
  model_repository: "test",
  opsml_version: "1.0.0",
  data_schema: {
    data_type: "test",
    input_features: "test",
    ouput_features: "test",
    onnx_input_features: "test",
    onnx_output_features: "test",
    onnx_data_type: "test",
    onnx_version: "test",
  },
  uid: "test",
  drift: undefined,
};

export const sampleDataMetadata: DataCardMetadata = {
  name: "test",
  repository: "test",
  version: "1.0.0",
  uid: "test",
  contact: "test",
  interface_type: "polars",
  data_splits: JSON.stringify({ test: 0.2, train: 0.8 }),
  feature_map: JSON.stringify({ test: 0.2, train: 0.8 }),
  sql_logic: new Map(),
  has_profile: true,
};

export const sampleFiles = {
  mtime: 1711563309,
  files: [
    {
      name: "test",
      size: 10,
      type: "test",
      created: 1711563309,
      islink: false,
      mode: 10,
      uid: 10,
      gid: 10,
      mtime: 1711563309,
      ino: 10,
      nlink: 10,
      uri: "test",
      suffix: ".md",
    },
  ],
};

export const sampleCardVersions = {
  nbr_cards: 10,
  name: "test",
  repository: "test",
  registry: "test",
  cards: {
    cards: [
      {
        date: "2021-09-01T00:00:00Z",
        uid: "test",
        repository: "test",
        contact: "test",
        name: "test",
        version: "0.1.0",
        timestamp: 1711563309,
        tags: new Map(),
        datacard_uid: "test",
        runcard_uid: "test",
      },
    ],
  },
};

export const SpcDriftProfile = {
  features: {
    col1: {
      id: "col1",
      center: 0.0,
      one_ucl: 0.0,
      one_lcl: 0.0,
      two_ucl: 0.0,
      two_lcl: 0.0,
      three_ucl: 0.0,
      three_lcl: 0.0,
      timestamp: "2024-08-29T01:10:45.652409",
    },
  },
  config: {
    sample_size: 100,
    sample: true,
    name: "test",
    repository: "test",
    version: "1.0.0",
    feature_map: undefined,
    targets: [],
    alert_config: {
      dispatch_type: "Console",
      rule: {
        rule: "8 8 8 8 8 8 8 8",
        zones_to_monitor: ["Zone 1", "Zone 2", "Zone 3", "Zone 4"],
      },
      schedule: "0 0 0 0 0 0 0 0",
      dispatch_kwargs: {},
    },
  },
  scouter_version: "1.0.0",
};

export const featureDriftValues = {
  features: {
    col_1: {
      created_at: [
        "2024-09-18T01:12:00",
        "2024-09-18T01:26:24",
        "2024-09-18T01:40:48",
        "2024-09-18T01:55:12",
        "2024-09-18T02:09:36",
      ],
      values: [
        1.0530614698813359, -0.03748357969929229, 0.1782311377309393,
        0.44125417583912063, -0.6577854789448841,
      ],
    },
  },
};

export const allFeatureDriftValues = {
  features: {
    all_features: {
      created_at: [
        "2024-09-18T01:12:00",
        "2024-09-18T01:26:24",
        "2024-09-18T01:40:48",
        "2024-09-18T01:55:12",
        "2024-09-18T02:09:36",
      ],
      values: [
        1.0530614698813359, -0.03748357969929229, 0.1782311377309393,
        0.44125417583912063, -0.6577854789448841,
      ],
    },
  },
};

export const exampleFeatureDistribution = {
  name: "test",
  repository: "test",
  version: "1.0.0",
  percentile_10: 0.0,
  percentile_20: 0.0,
  percentile_30: 0.0,
  percentile_40: 0.0,
  percentile_50: 0.0,
  percentile_60: 0.0,
  percentile_70: 0.0,
  percentile_80: 0.0,
  percentile_90: 0.0,
  percentile_100: 0.0,
  val_10: 0.0,
  val_20: 0.0,
  val_30: 0.0,
  val_40: 0.0,
  val_50: 0.0,
  val_60: 0.0,
  val_70: 0.0,
  val_80: 0.0,
  val_90: 0.0,
  val_100: 0.0,
};

// Example usage
export const exampleAlert: MonitorAlert = {
  created_at: "2023-10-01T12:34:56Z",
  name: "Example Alert",
  repository: "example-repo",
  version: "1.0.0",
  feature: "example-feature",
  alert: {
    alert1: "Description of alert 1",
    alert2: "Description of alert 2",
  },
  status: "active",
  id: 1,
};

export const exampleAlerts: MonitorAlerts = {
  alerts: [exampleAlert],
};

export const exampleUpdateAlert: UpdateAlert = {
  message: "Example message",
  status: "success",
};

export const exampleObservabilityMetrics = {
  metrics: [
    {
      route_name: "test",
      created_aty: ["2023-10-01T12:34:56Z"],
      total_request_count: 100,
      total_error_count: 10,
      p5: [1],
      p50: [1],
      p95: [2],
      p99: [3],
      request_count: [10],
      error_count: [1],
      error_latency: [1],
      status_counts: [{ "200": 10 }],
    },
    {
      route_name: "test2",
      created_aty: ["2023-10-01T12:34:56Z"],
      total_request_count: 100,
      total_error_count: 10,
      p5: [1],
      p50: [1],
      p95: [2],
      p99: [3],
      request_count: [10],
      error_count: [1],
      error_latency: [1],
      status_counts: [{ "200": 10 }],
    },
  ],
};

export const exampleAlertMetrics: AlertMetrics = {
  created_at: ["2023-10-01T12:34:56Z"],
  acknowledged: [1],
  active: [1],
  alert_count: [1],
};

const exampleDistinct: Distinct = {
  count: 0,
  percent: 0,
};

const exampleQuantiles: Quantiles = {
  q25: 0,
  q50: 0,
  q75: 0,
  q99: 0,
};

const exampleHistogram: Histogram = {
  bins: [0],
  bin_counts: [0],
};

const exampleWordStats: WordStats = {
  words: {},
};

const exampleCharStats: CharStats = {
  min_length: 0,
  max_length: 0,
  median_length: 0,
  mean_length: 0,
};

const exampleStringStats: StringStats = {
  distinct: exampleDistinct,
  char_stats: exampleCharStats,
  word_stats: exampleWordStats,
};

const exampleNumericStats: NumericStats = {
  mean: 0.0,
  stddev: 0.0,
  min: 0.0,
  max: 0.0,
  distinct: exampleDistinct,
  quantiles: exampleQuantiles,
  histogram: exampleHistogram,
};

const exampleFeatureProfileNum: FeatureProfile = {
  id: "col1",
  numeric_stats: exampleNumericStats,
  string_stats: undefined,
  timestamp: "2024-08-29T01:10:45.652409",
  correlations: { col2: 0.0 },
};

const exampleFeatureProfileString: FeatureProfile = {
  id: "col1",
  numeric_stats: undefined,
  string_stats: exampleStringStats,
  timestamp: "2024-08-29T01:10:45.652409",
  correlations: { col2: 0.0 },
};

export const exampleDataProfile: DataProfile = {
  features: {
    col1: exampleFeatureProfileNum,
    col2: exampleFeatureProfileString,
  },
};
