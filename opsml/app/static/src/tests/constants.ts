import { type User, type RunMetrics } from "$lib/scripts/types";

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
  updated_username: null,
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
