import {
  type User,
  type RunMetrics,
  type Card,
  type Artifact,
  type Parameter,
  type ModelMetadata,
  type DataCardMetadata,
} from "$lib/scripts/types";

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

export const driftProfile = {
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
      alert_dispatch_type: "Console",
      alert_rule: {
        process: {
          rule: "8 8 8 8 8 8 8 8",
          zones_to_monitor: ["Zone 1", "Zone 2", "Zone 3", "Zone 4"],
        },
        percentage: undefined,
      },
      schedule: "0 0 0 0 0 0 0 0",
      features_to_monitor: ["col1"],
      alert_kwargs: {},
    },
  },
  scouter_version: "1.0.0",
};
