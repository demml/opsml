import { server } from "./server";
import { render } from "@testing-library/svelte";
import { afterAll, afterEach, beforeAll, it } from "vitest";
import * as utils from "../lib/scripts/utils";
import RunPage from "../routes/opsml/run/+page.svelte";
import RunCardPage from "../routes/opsml/run/card/home/+page.svelte";
import RunCardMetricPage from "../routes/opsml/run/card/metrics/+page.svelte";
import RunCardCompareMetricPage from "../routes/opsml/run/card/metrics/compare/+page.svelte";
import RunCardFilesPage from "../routes/opsml/run/card/files/+page.svelte";
import RunCardHardWare from "../routes/opsml/run/card/hardware/+page.svelte";
import RunCardGraphs from "../routes/opsml/run/card/graphs/+page.svelte";
import {
  sampleRunCard,
  sampleParameters,
  sampleMetrics,
  sampleRunMetics,
  sampleCards,
  sampleFiles,
} from "./constants";
import { RunPageStore, RunCardStore } from "$routes/store";

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

it("render runPage", async () => {
  const registryPage = await utils.setupRegistryPage("model");

  RunPageStore.update((store) => {
    store.selectedRepo = "model";
    store.registryStats = registryPage.registryStats;
    store.registryPage = registryPage.registryPage;
    return store;
  });

  const data = {
    args: {
      repos: ["model"],
      searchTerm: undefined,
      selectedRepo: "model",
      selectedVersion: undefined,
      selectedSubdir: undefined,
      selectedFile: undefined,
      selectedRegistry: "model",
      registryStats: registryPage.registryStats,
      registryPage: registryPage.registryPage,
      registry: "run",
    },
  };

  render(RunPage, { data });
});

it("render runCardPage", async () => {
  const data = {
    card: {
      date: "2021-09-01T00:00:00Z",
      uid: "test",
      repository: "test",
      contact: "test",
      name: "test",
      version: "0.1.0",
      timestamp: 1711563309,
      tags: new Map(),
      datacard_uid: "test",
      modelcard_uid: "test",
      modelcard_uids: ["test"],
      datacard_uids: ["test"],
    },
    metadata: sampleRunCard,
    metricNames: ["test"],
    parameters: sampleParameters,
    tableMetrics: sampleMetrics,
  };

  render(RunCardPage, { data });
});

it("render runCardMetricPage", () => {
  const metricViz = utils.createMetricVizData(sampleRunMetics, "bar");

  RunCardStore.update((store) => {
    store.MetricData = metricViz;
    store.TableMetrics = sampleMetrics;
    return store;
  });

  const data = {
    metrics: sampleRunMetics,
    metricNames: ["accuracy"],
    metricVizData: metricViz,
    tableMetrics: sampleMetrics,
  };

  render(RunCardMetricPage, { data });
});

it("render runCardMetricComparePage", async () => {
  const metricViz = utils.createMetricVizData(sampleRunMetics, "bar");
  const referenceMetrics = new Map();
  referenceMetrics.set("accuracy", 10);
  const data = {
    name: "test",
    repository: "test",
    registry: "run",
    version: "1.0.0",
    card: sampleRunCard,
    metricNames: ["accuracy"],
    searchableMetrics: ["accuracy"],
    metrics: sampleRunMetics,
    cards: sampleCards,
    metricVizData: metricViz,
    referenceMetrics: referenceMetrics,
    show: true,
  };

  render(RunCardCompareMetricPage, { data });
});

it("render RunCardFiles", async () => {
  const modifiedAt = utils.calculateTimeBetween(sampleFiles.mtime);
  const basePath = "test";

  const data = {
    repository: "test",
    registry: "test",
    name: "test",
    version: "test",
    displayPath: ["test"],
    subdir: "test",
    prevPath: "test",
    files: sampleFiles,
    modifiedAt,
    basePath,
  };

  render(RunCardFilesPage, { data });
});

it("render RunCardHardware", async () => {
  const data = {
    metadata: sampleRunCard,
  };

  render(RunCardHardWare, { data });
});

it("render RunCardHardware with hardware", async () => {
  const data = {
    metadata: sampleRunCard,
  };

  const hardwareMetrics = await utils.getHardwareMetrics("run_uid");
  const parsedMetrics = utils.parseHardwareMetrics(hardwareMetrics.metrics);
  const charts = utils.createHardwareCharts(parsedMetrics);

  RunCardStore.update((store) => {
    store.HardwareMetrics = parsedMetrics;
    store.HardwareCharts = charts;
    return store;
  });

  render(RunCardHardWare, { data });
  expect(document.getElementById("renderedChart")).toBeTruthy();
});

it("render RunGraphs", async () => {
  const graphs = await utils.getRunGraphs("name", "repository", "version");

  RunCardStore.update((store) => {
    store.Graphs = graphs;
    return store;
  });

  render(RunCardGraphs);
  expect(document.getElementById("renderGraphs")).toBeTruthy();
});

it("render no RunGraphs", async () => {
  RunCardStore.update((store) => {
    store.Graphs = undefined;
    return store;
  });
  render(RunCardGraphs);
  expect(document.getElementById("notRendered")).toBeTruthy();
});
