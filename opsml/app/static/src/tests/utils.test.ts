import { it, expect } from "vitest";
import * as page from "../lib/scripts/utils";
import {
  type CardRequest,
  type Message,
  type UpdateUserRequest,
  type ChartjsData,
} from "$lib/scripts/types";
import { server } from "./server";
import {
  metricsForTable,
  user,
  sampleRunMetics,
  barData,
  SpcDriftProfile,
  allFeatureDriftValues,
  featureDriftValues,
  exampleFeatureDistribution,
  exampleAlerts,
  exampleUpdateAlert,
  exampleObservabilityMetrics,
  exampleAlertMetrics,
  sampleModelMetadata,
} from "./constants";
import { graphs } from "./graphs";
import * as monitoring from "../lib/scripts/monitoring/utils";

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

// test calculateTimeBetween
it("calculateTimeBetween", () => {
  const ts = new Date().getTime();
  const timeBetween = page.calculateTimeBetween(ts);
  expect(timeBetween).toMatch(/(^\d+ hours ago$)|(^\d+ days ago$)/);
});

it("cardRequest", async () => {
  const cardRequest: CardRequest = {
    repository: "model",
    version: "1.0.0",
    uid: "test",
    limit: 10,
    page: 1,
    registry_type: "run".toString(),
  };
  const cards = await page.listCards(cardRequest);
  expect(cards.cards).toEqual([
    {
      uid: "f8dd058f-9006-4174-8d49-e3086bc39c21",
    },
  ]);
});

it("getMessage", async () => {
  const message = await page.getMessages("uid", "model");
  expect(message).toEqual([
    {
      message: "User this is a message",
      replies: [{ message: "User this is a reply" }],
    },
  ]);
});

it("putMessage", async () => {
  const messageRequest: Message = {
    uid: "uid",
    registry: "model",
    content: "User this is a message",
    user: "user",
    votes: 0,
    parent_id: 0,
    created_at: 98709870,
  };
  await page.putMessage(messageRequest);
});

// patch messages
it("patchMessage", async () => {
  const messageRequest: Message = {
    uid: "uid",
    registry: "model",
    content: "User this is a message",
    user: "user",
    votes: 0,
    parent_id: 0,
    created_at: 98709870,
  };

  await page.patchMessage(messageRequest);
});

// get datacard
it("getDataCard", async () => {
  const cardRequest: CardRequest = {
    repository: "model",
    version: "1.0.0",
    limit: 10,
    page: 1,
    uid: "uid",
    registry_type: "data".toString(),
  };

  const dataCard = await page.getDataCard(cardRequest);
  expect(dataCard).toEqual({
    name: "test",
    repository: "test",
    version: "1.0.0",
    uid: "test",
    contact: "test",
    interface_type: "polars",
  });
});

// get runcard
it("getRunCard", async () => {
  const cardRequest: CardRequest = {
    repository: "model",
    version: "1.0.0",
    limit: 10,
    page: 1,
    uid: "uid",
    registry_type: "data".toString(),
  };

  const runCard = await page.getRunCard(cardRequest);
  expect(runCard).toEqual({
    name: "test",
    repository: "test",
    version: "1.0.0",
    uid: "test",
    contact: "test",
  });
});

// get run metric names
it("getRunMetricNames", async () => {
  const runCard = await page.getRunMetricNames("uid");
  expect(runCard).toEqual({
    names: ["test"],
  });
});

it("getRunMetrics", async () => {
  const runCard = await page.getRunMetrics("uid");
  expect(runCard).toEqual({
    test: [
      {
        run_uid: "test",
        name: "test",
        value: 1,
        step: 1,
        timestamp: 1,
      },
      {
        run_uid: "test",
        name: "test",
        value: 2,
        step: 2,
        timestamp: 1,
      },
    ],
  });
});

// get run parameters

it("getRunParameters", async () => {
  const runCard = await page.getRunParameters("uid");
  expect(runCard).toEqual({
    parameter: [
      {
        name: "test",
        run_uid: "test",
        value: 1,
        step: 1,
        timestamp: 1,
      },
    ],
  });
});

// get readme
it("getReadme", async () => {
  const readme = await page.getReadme("markdown_path");
  expect(readme).toEqual({
    readme: "test",
    exists: true,
  });
});

// get modelMetadata
it("getModelMetadata", async () => {
  const metadata = await page.getModelMetadata(
    "name",
    "model",
    "test",
    undefined
  );
  expect(metadata).toEqual(sampleModelMetadata);
});

// test setup files
it("setupFiles", async () => {
  const files = await page.setupFiles(
    "opsml/bastpath",
    "model",
    "name",
    "1.0.0",
    "subdir"
  );
  expect(files).toEqual({
    displayPath: ["model", "name", "v1.0.0", "subdir"],
    fileInfo: {
      files: [
        {
          created: 234342,
          gid: 10,
          ino: 10,
          islink: false,
          mode: 10,
          mtime: 10,
          name: "test",
          nlink: 10,
          size: 10,
          suffix: ".md",
          type: "markdown",
          uid: 10,
          uri: "uri",
        },
      ],
      mtime: 10,
    },
    prevPath: "opsml/bastpath/",
  });
});

// test setup registry page
it("setupRegistryPage", async () => {
  const registryPage = await page.setupRegistryPage("model");
  expect(registryPage).toEqual({
    registry: "model",
    registryPage: {
      page: ["model", "repo", 10, 120, 110, 10],
    },
    registryStats: {
      nbr_names: 1,
      nbr_repos: 1,
      nbr_versions: 1,
    },
    repos: ["model", "run", "data"],
  });
});

// test getUser
it("getUser", async () => {
  const user = await page.getUser("username");
  expect(user).toEqual({
    error: undefined,
    user: {
      user: {
        is_active: true,
        scopes: {
          admin: true,
          delete: true,
          read: true,
          write: true,
        },
        username: "test",
        watchlist: {
          data: ["test"],
          model: ["test"],
          run: ["test"],
        },
      },
    },
  });
});

it("getRepos", async () => {
  const repos = await page.getRepos("model");
  expect(repos).toEqual(["model", "run", "data"]);
});

// test getRegistryPage
it("getRegistryPage", async () => {
  const pageData = await page.getRegistryPage(
    "model",
    undefined,
    "repo",
    "model",
    0
  );
  expect(pageData.page).toEqual(["model", "repo", 10, 120, 110, 10]);
});

// test update user
it("updateUser", async () => {
  const userRequest: UpdateUserRequest = {
    username: "username",
    updated_username: "newusername",
    full_name: "test",
    password: "test",
    email: "test",
    is_active: true,
    security_question: "test",
    security_answer: "test",
    scopes: user.scopes,
  };

  const updated = await page.updateUser(userRequest);
  expect(updated).toEqual({
    updated: true,
  });
});

// test password strength
it("passwordStrength", () => {
  const password = "testsd8@";
  const strength = page.checkPasswordStrength(password);
  expect(strength).toEqual({
    color: "green-500",
    message: "Missing:, uppercase",
    power: 80,
  });
});

// sort metrics
it("sortMetrics", () => {
  const metrics = {
    metric: [
      {
        run_uid: "test",
        name: "test",
        value: 1,
        step: 1,
        timestamp: 1,
      },
      {
        run_uid: "test",
        name: "test",
        value: 2,
        step: 2,
        timestamp: 1,
      },
    ],
  };

  const sortedMetrics = page.sortMetrics(metrics);
  expect(sortedMetrics).toEqual({
    test: [
      {
        name: "test",
        run_uid: "test",
        step: 1,
        timestamp: 1,
        value: 1,
      },
      {
        name: "test",
        run_uid: "test",
        step: 2,
        timestamp: 1,
        value: 2,
      },
    ],
  });
});

// test metricsToTable
it("metricsToTable", () => {
  const metricNames = ["accuracy"];
  const tableMetrics = page.metricsToTable(metricsForTable, metricNames);
  const expected = new Map();
  expected.set("run_1", [
    {
      name: "accuracy",
      step: 300,
      value: 0.97,
    },
  ]);
  expected.set("run_2", [
    {
      name: "accuracy",
      step: 150,
      value: 0.94,
    },
  ]);
  expect(tableMetrics).toEqual(expected);
});

// test createMetricBarVizData
it("createMetricBarVizData", () => {
  const metricVizData: ChartjsData = page.createMetricVizData(
    sampleRunMetics,
    "bar"
  );
  expect(metricVizData.data.datasets[0]).toEqual(barData.data.datasets[0]);
});

// test createMetricBarVizData
it("createMetricLINEVizData", () => {
  const metricVizData: ChartjsData = page.createMetricVizData(
    sampleRunMetics,
    "line"
  );
  expect(metricVizData.data.datasets[0]).toEqual({
    backgroundColor: "rgb(82, 224, 123)",
    borderColor: "rgb(82, 224, 123)",
    data: [0.92, 0.95, 0.97],
    label: "accuracy",
    pointRadius: 1,
  });
});

// test exportMetricsToCSV
it("downloadMetricCSV", () => {
  const csv = page.exportMetricsToCSV(sampleRunMetics);
  expect(csv).toContain(
    "run_uid,name,value,step,timestamp\nrun_1,accuracy,0.92,100,1593561600000\nrun_1,accuracy,0.95,200,1593648000000"
  );
});

// test createGroupMetricVizData
it("createGroupMetricVizData", () => {
  const metricVizDataBar: ChartjsData = page.createGroupMetricVizData(
    metricsForTable,
    ["accuracy"],
    "bar"
  );
  expect(metricVizDataBar.data.datasets[0]).toEqual({
    backgroundColor: "rgba(82, 224, 123, 0.2)",
    borderColor: "rgb(82, 224, 123)",
    borderRadius: 2,
    borderSkipped: false,
    borderWidth: 2,
    data: [0.97],
    label: "run_1",
  });

  const metricVizDataLine: ChartjsData = page.createGroupMetricVizData(
    metricsForTable,
    ["accuracy"],
    "line"
  );
  expect(metricVizDataLine.data.datasets[0]).toEqual({
    backgroundColor: "rgb(82, 224, 123)",
    borderColor: "rgb(82, 224, 123)",
    data: [0.92, 0.95, 0.97],
    label: "run_1-accuracy",
    pointRadius: 1,
  });
});

// test hardware metrics
it("getHardwareMetrics", async () => {
  const hardwareMetrics = await page.getHardwareMetrics("run_uid");
  expect(hardwareMetrics.metrics.length).toEqual(3);

  const parsedMetrics = page.parseHardwareMetrics(hardwareMetrics.metrics);
  const hardwareCharts = page.createHardwareCharts(parsedMetrics);

  expect(hardwareCharts.cpu_overall.data.datasets[0].data).toEqual([
    27.62, 27.62, 27.62,
  ]);

  // cpu_per_core should not be none
  if (!hardwareCharts.cpu_per_core) {
    throw new Error("cpu_per_core should not be none");
  }

  expect(hardwareCharts.cpu_per_core.data.datasets[0].data).toEqual([
    45.1, 45.1, 45.1,
  ]);
});

it("getGraphs", async () => {
  const _graphs = await page.getRunGraphs("repo", "name", "version");
  expect(_graphs).toEqual(graphs);
});

it("getDriftProfile", async () => {
  const _profile = await monitoring.getDriftProfile("repo", "name", "version");
  expect(_profile.profile).toEqual(SpcDriftProfile);
  let featureProfile = monitoring.getSpcFeatureProfile(
    "col1",
    _profile.profile!
  );

  expect(featureProfile.center).toEqual(0);
});

it("UpdateDriftProfile", async () => {
  const response = await monitoring.updateDriftProfile(
    "repo",
    "name",
    "version",
    "profile"
  );
  expect(response.complete).toEqual(true);
});

it("GetFeatureValues", async () => {
  const all_features_response = await monitoring.getFeatureDriftValues(
    "repo",
    "name",
    "version",
    "2day",
    100
  );
  expect(all_features_response).toEqual(allFeatureDriftValues);

  const feature_response = await monitoring.getFeatureDriftValues(
    "repo",
    "name",
    "version",
    "2day",
    100,
    "col1"
  );
  expect(feature_response).toEqual(featureDriftValues);

  const no_feature_response = await monitoring.getFeatureDriftValues(
    "repo",
    "name",
    "version",
    "2day",
    100,
    "no"
  );
  let numVals = no_feature_response.features["no"].values.length;
  let numDates = no_feature_response.features["no"].created_at.length;
  expect(numVals).toEqual(30);
  expect(numDates).toEqual(30);
});

it("GetFeatureDistributionValues", async () => {
  const featureDistResponse = await monitoring.getSpcFeatureDistributionValues(
    "repo",
    "name",
    "version",
    "2day",
    100,
    "feature"
  );
  expect(featureDistResponse).toEqual(exampleFeatureDistribution);
});

it("GetMonitorAlerts", async () => {
  const alerts = await monitoring.getMonitorAlerts("repo", "name", "version");
  expect(alerts).toEqual(exampleAlerts);
});

it("UpdateMonitorAlerts", async () => {
  const response = await monitoring.updateMonitorAlert(0, "acknowledged");
  expect(response).toEqual(exampleUpdateAlert);
});

it("GetAlertMetrics", async () => {
  const alertMetrics = await monitoring.getAlertMetrics(
    "repo",
    "name",
    "version",
    "2day",
    100
  );
  expect(alertMetrics).toEqual(exampleAlertMetrics);
});

it("GetObservabilityMetrics", async () => {
  const metrics = await monitoring.getObservabilityMetrics(
    "repo",
    "name",
    "version",
    "2day",
    100
  );
  expect(metrics).toEqual(exampleObservabilityMetrics);
});
