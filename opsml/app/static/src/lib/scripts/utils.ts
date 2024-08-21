import {
  type CardRequest,
  type CardResponse,
  type DataCardMetadata,
  type RunCard,
  type Metrics,
  type MetricNames,
  type Parameters,
  type Graph,
  type RunMetrics,
  type Message,
  type MessageThread,
  type FileExists,
  type Readme,
  CommonPaths,
  type ModelMetadata,
  type metadataRequest,
  type Files,
  type FileSetup,
  type registryStats,
  type repositories,
  type registryPage,
  type registryPageReturn,
  type User,
  type UserResponse,
  type UpdateUserRequest,
  type UpdateUserResponse,
  type PasswordStrength,
  type Metric,
  type TableMetric,
  type ChartData,
  type ChartjsData,
  type ChartjsLineDataset,
  type ChartjsBarDataset,
  type ChartjsGroupedBarDataset,
  type FileViewResponse,
  type UserUpdated,
} from "$lib/scripts/types";
import { apiHandler } from "$lib/scripts/apiHandler";
import type { Mode } from "chartjs-plugin-zoom/types/options";

export function calculateTimeBetween(timestamp: number): string {
  const presentDate: Date = new Date();

  const epoch = timestamp;
  const date1: Date = new Date(epoch);

  const hours = Math.abs(presentDate.getTime() - date1.getTime()) / 3600000;
  if (hours > 24) {
    const days = Math.round(hours / 24);
    return `${days} days ago`;
  }
  return `${Math.round(hours)} hours ago`;
}

export async function listCards(request: CardRequest): Promise<CardResponse> {
  // get card info

  const cards = (await apiHandler
    .post(CommonPaths.LIST_CARDS, request, "application/json")
    .then((res) => res.json())) as CardResponse;

  return cards;
}

export async function getMessages(
  uid: string,
  registry: string
): Promise<MessageThread> {
  const comments = (await apiHandler
    .get(`/opsml/${registry}/messages?uid=${uid}`)
    .then((res) => res.json())) as MessageThread;

  return comments;
}

export async function putMessage(message: Message): Promise<void> {
  const request = {
    uid: message.uid,
    registry: message.registry,
    content: message.content,
    user: message.user,
    votes: message.votes,
    parent_id: message.parent_id,
    created_at: message.created_at,
  };

  await apiHandler
    .put(`/opsml/${message.registry}/messages`, request)
    .then((res) => res.json());
}

export async function patchMessage(message: Message): Promise<void> {
  const request = {
    uid: message.uid,
    registry: message.registry,
    content: message.content,
    user: message.user,
    votes: message.votes,
    parent_id: message.parent_id,
    created_at: message.created_at,
  };

  await apiHandler
    .patch(`/opsml/${message.registry}/messages`, request)
    .then((res) => res.json());
}

export async function getDataCard(
  request: CardRequest
): Promise<DataCardMetadata> {
  const dataCard = (await apiHandler
    .post(CommonPaths.DATACARD, request)
    .then((res) => res.json())) as DataCardMetadata;

  return dataCard;
}

export async function getRunCard(request: CardRequest): Promise<RunCard> {
  const runCard = (await apiHandler
    .post(CommonPaths.RUNCARD, request)
    .then((res) => res.json())) as RunCard;

  return runCard;
}

export async function getRunMetricNames(uid: string): Promise<MetricNames> {
  const request = { run_uid: uid, names_only: true };

  const names = (await apiHandler
    .post(CommonPaths.METRICS, request)
    .then((res) => res.json())) as MetricNames;

  return names;
}

export async function getRunMetrics(
  uid: string,
  name?: string[]
): Promise<RunMetrics> {
  const request = { run_uid: uid, name };

  const metrics = (await apiHandler
    .post(CommonPaths.METRICS, request)
    .then((res) => res.json())) as Metrics;

  const runMetrics: RunMetrics = {};

  if (metrics.metric.length > 0) {
    // create loop for metricNames.metric
    for (const metric of metrics.metric) {
      // check if metric.name is in metrics
      if (runMetrics[metric.name] === undefined) {
        runMetrics[metric.name] = [];
      }

      // push metric
      runMetrics[metric.name].push(metric);
    }
  }

  return runMetrics;
}

export async function getRunParameters(uid: string): Promise<Parameters> {
  const request = { run_uid: uid };

  const params = (await apiHandler
    .post(CommonPaths.PARAMETERS, request)
    .then((res) => res.json())) as Parameters;

  return params;
}

export async function getRunGraphs(
  repository: string,
  name: string,
  version: string
): Promise<Map<string, Graph>> {
  const params = new URLSearchParams();
  params.append("repository", repository);
  params.append("name", name);
  params.append("version", version);

  const url = `${CommonPaths.GRAPHS}?${params.toString()}`;

  // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
  const graphs = await apiHandler.get(url).then((res) => res.json());

  // eslint-disable-next-line @typescript-eslint/no-unsafe-return
  return graphs;
}

/**
 * Get the readme for a given markdown path
 * @param {string} markdownPath
 *
 * @returns {Promise<string>} readme
 *
 */
export async function getReadme(markdownPath: string): Promise<Readme> {
  const markdown = (await apiHandler
    .get(
      `${CommonPaths.FILE_EXISTS}?${new URLSearchParams({
        path: markdownPath,
      }).toString()}`
    )
    .then((res) => res.json())) as FileExists;

  let readme: string = "";

  if (markdown.exists) {
    // fetch markdown

    const viewData = (await apiHandler
      .get(
        `${CommonPaths.FILES_VIEW}?${new URLSearchParams({
          path: markdownPath,
        }).toString()}`
      )
      .then((res) => res.json())) as FileViewResponse;

    readme = viewData.content.content!;
  }

  // return readme and markdown exists
  return { readme, exists: markdown.exists };
}

/**
 * Get metadata for a model
 * @param {string | null} uid
 * @param {string} name
 * @param {string} repository
 * @param {string | null} version
 *
 * @returns {Promise<ModelMetadata>} metadata
 *
 */
export async function getModelMetadata(
  name: string,
  repository: string,
  uid: string | null,
  version: string | null
): Promise<ModelMetadata> {
  let metaAttr: metadataRequest = {};

  if (uid !== null) {
    metaAttr = {
      uid,
    };
  } else {
    metaAttr = {
      name,
      repository,
    };

    if (version !== null) {
      metaAttr.version = version;
    }
  }

  const res = (await apiHandler
    .post(CommonPaths.MODEL_METADATA, metaAttr)
    .then((res) => res.json())) as ModelMetadata;

  return res;
}

/**
 * Generic function for setting up filesystem view
 * @param {string} basePath
 * @param {string} repository
 * @param {string} name
 * @param {string} version
 * @param {string | null} subdir
 *
 * @returns {Promise<FileSetup>} setup
 *
 */
export async function setupFiles(
  basePath: string,
  repository: string,
  name: string,
  version: string | null,
  subdir: string | null
): Promise<FileSetup> {
  let urlPath = `${CommonPaths.FILE_INFO}?path=${basePath}`;
  let displayPath = [repository, name, `v${version}`];
  let prevPath: string = basePath;

  if (subdir !== null) {
    urlPath = `${urlPath}&subdir=${subdir}`;

    // split the subdir path
    displayPath = displayPath.concat(subdir.split("/"));

    const subPath = subdir.split("/");
    const prevDir = subPath.slice(0, subPath.length - 1).join("/");
    prevPath = `${basePath}/${prevDir}`;
  }

  const fileInfo = (await apiHandler
    .get(urlPath)
    .then((res) => res.json())) as Files;

  return {
    fileInfo,
    prevPath,
    displayPath,
  };
}

/**
 * Setup the registry page
 * @param {string} registry
 *
 * @returns {Promise<registryPageReturn>} page
 *
 */
export async function setupRegistryPage(
  registry: string
): Promise<registryPageReturn> {
  const repos = (await apiHandler
    .get(
      `${CommonPaths.REPOSITORIES}?${new URLSearchParams({
        registry_type: registry,
      }).toString()}`
    )
    .then((res) => res.json())) as repositories;

  const stats = (await apiHandler
    .get(
      `${CommonPaths.REGISTRY_STATS}?${new URLSearchParams({
        registry_type: registry,
      }).toString()}`
    )
    .then((res) => res.json())) as registryStats;

  const page = (await apiHandler
    .get(
      `${CommonPaths.QUERY_PAGE}?${new URLSearchParams({
        registry_type: registry,
        page: "0",
      }).toString()}`
    )
    .then((res) => res.json())) as registryPage;

  return {
    repos: repos.repositories,
    registry,
    registryStats: stats,
    registryPage: page,
  };
}

/**
 * Get user information
 * @param {string} username
 * @returns {Promise<UserResponse>} user
 *
 */
export async function getUser(username: string): Promise<UserResponse> {
  let user: User | null = null;
  let error: string | null = null;
  const url: string = `${CommonPaths.USER_AUTH}?username=${username}`;

  const response = await apiHandler.get(url);
  if (response.ok) {
    user = (await response.json()) as User;
  } else {
    error = await response.text();
  }
  return { user, error };
}

/**
 * Update user information
 *
 * @param {UpdateUserRequest} user
 * @returns {Promise<UpdateUserResponse>} updated
 *
 */
export async function updateUser(
  user: UpdateUserRequest
): Promise<UpdateUserResponse> {
  const response = await apiHandler.put(CommonPaths.USER_AUTH, user);
  if (!response.ok) {
    return {
      updated: false,
    };
  }
  const res = (await response.json()) as UserUpdated;
  return {
    updated: res.updated,
  };
}

export function goTop() {
  document.body.scrollIntoView();
}

export function checkPasswordStrength(password: string): PasswordStrength {
  let point = 0;
  const widthPower = [0, 20, 40, 60, 80, 100];
  const colorPower = [
    "red-600",
    "orange-600",
    "yellow-500",
    "lime-500",
    "green-500",
  ];
  let message = "Missing:";

  const isLength = password.length >= 8;
  const hasNum = /[0-9]/.test(password);
  const hasLower = /[a-z]/.test(password);
  const hasUpper = /[A-Z]/.test(password);
  const hasSpecial = /[^0-9a-zA-Z]/.test(password);

  if (isLength) {
    point += 1;
  } else {
    message += " 8 chars";
  }

  if (hasNum) {
    point += 1;
  } else {
    message += ", number";
  }

  if (hasLower) {
    point += 1;
  } else {
    message += ", lowercase";
  }

  if (hasUpper) {
    point += 1;
  } else {
    message += ", uppercase";
  }

  if (hasSpecial) {
    point += 1;
  } else {
    message += ", special char";
  }

  const power = widthPower[point];
  const color = colorPower[point];

  return { power, color, message };
}

export function delay(fn, ms: number) {
  let timer = 0;
  return function (...args) {
    clearTimeout(timer);

    // @ts-expect-error "ignore"
    // eslint-disable-next-line @typescript-eslint/no-unsafe-member-access,  @typescript-eslint/no-unsafe-call, @typescript-eslint/no-unsafe-argument
    timer = window.setTimeout(fn.bind(this, ...args), ms || 0);
  };
}

export const sleep = (ms: number) =>
  new Promise((resolve) => setTimeout(resolve, ms));

export function sortMetrics(metrics: Metrics): RunMetrics {
  const sorted: RunMetrics = {};

  // create loop for metricNames.metric
  for (const metric of metrics.metric) {
    // check if metric.name is in metrics
    if (sorted[metric.name] === undefined) {
      sorted[metric.name] = [];
    }

    // push metric
    sorted[metric.name].push(metric);
  }

  return sorted;
}

export function metricsToTable(
  metrics: Map<string, RunMetrics>,
  metricsToPlot: string[]
): Map<string, TableMetric[]> {
  const table: Map<string, TableMetric[]> = new Map();
  for (const [key, value] of metrics) {
    table.set(key, []);

    metricsToPlot.forEach((metric) => {
      const metricValue: Metric[] = value[metric];

      if (metricValue) {
        table.get(key)!.push({
          name: metric,
          value: metricValue[metricValue.length - 1].value,
          step: metricValue[metricValue.length - 1].step || 0,
        });
      } else {
        table.get(key)!.push({
          name: metric,
          value: "N/A",
          step: "N/A",
        });
      }
    });
  }

  return table;
}

function parseMetric(type: string, metric: Metric[]): ChartData {
  const x: number[] | string[] = [];
  const y: number[] = [];

  if (type == "line") {
    for (const data of metric) {
      y.push(data.value);

      // @ts-expect-error "mismatch types"
      x.push(data.step || 0);
    }
  } else {
    y.push(metric[metric.length - 1].value);

    // @ts-expect-error "mismatch types"
    x.push(metric[metric.length - 1].name);
  }

  return { x, y };
}

const handleResize = (chart) => {
  // eslint-disable-next-line @typescript-eslint/no-unsafe-member-access, @typescript-eslint/no-unsafe-call
  chart.resize();
};

export function buildDataforChart(
  x: number[] | string[],
  datasets:
    | ChartjsBarDataset[]
    | ChartjsLineDataset[]
    | ChartjsGroupedBarDataset[],
  x_label: string,
  y_label: string,
  chartType: string,
  showLegend: boolean = false
): ChartjsData {
  let grace = "2%";
  let legend = {
    display: false,
  };

  if (chartType === "line") {
    grace = "0%";
  }

  if (showLegend) {
    legend = {
      display: true,

      // @ts-expect-error "ignore"
      position: "bottom",
    };
  }

  const zoomOptions = {
    pan: {
      enabled: true,
      mode: "xy",
      modifierKey: "ctrl",
    },
    zoom: {
      mode: "xy",
      drag: {
        enabled: true,
        borderColor: "rgb(54, 162, 235)",
        borderWidth: 1,
        backgroundColor: "rgba(54, 162, 235, 0.3)",
      },
    },
  };

  return {
    type: chartType,
    data: {
      labels: x,
      datasets,
    },
    options: {
      plugins: {
        zoom: zoomOptions,
        legend,
      },
      responsive: true,
      onresize: handleResize,
      maintainAspectRatio: false,
      scales: {
        x: {
          title: { display: true, text: x_label },
          ticks: {
            maxTicksLimit: 30,
          },
        },
        y: {
          title: { display: true, text: y_label },
          ticks: {
            maxTicksLimit: 30,
          },
          grace,
        },
      },
      layout: {
        padding: 10,
      },
    },
  };
}

function generateColors(count: number, opacity?: number): string[] {
  return Array.from({ length: count }, (_, index) => {
    const hue = (index * 137.508) % 360; // Golden angle approximation
    const [r, g, b] = hslToRgb(hue, 0.7, 0.6);

    if (opacity !== undefined) {
      return `rgba(${r}, ${g}, ${b}, ${opacity})`;
    }
    return `rgb(${r}, ${g}, ${b})`;
  });
}

function hslToRgb(h: number, s: number, l: number): [number, number, number] {
  h /= 360;
  let r: number;
  let g: number;
  let b: number;

  if (s === 0) {
    r = g = b = l;
  } else {
    const hue2rgb = (p: number, q: number, t: number) => {
      if (t < 0) t += 1;
      if (t > 1) t -= 1;
      if (t < 1 / 6) return p + (q - p) * 6 * t;
      if (t < 1 / 2) return q;
      if (t < 2 / 3) return p + (q - p) * (2 / 3 - t) * 6;
      return p;
    };

    const q = l < 0.5 ? l * (1 + s) : l + s - l * s;
    const p = 2 * l - q;
    r = hue2rgb(p, q, h + 1 / 3);
    g = hue2rgb(p, q, h);
    b = hue2rgb(p, q, h - 1 / 3);
  }

  return [Math.round(r * 255), Math.round(g * 255), Math.round(b * 255)];
}

/**
 * Create metric settings for visualizations
 * @param {RunMetrics} metrics
 * @returns {Map<string, Graph>} mapping
 *
 *
 */
export function createMetricBarVizData(metrics: RunMetrics): ChartjsData {
  const x: number[] | string[] = [];
  const y: number[] = [];
  const backgroundColor: string[] = [];
  const borderColor: string[] = [];
  let data;
  const dataset: ChartjsBarDataset[] = [];

  const colors = generateColors(Object.keys(metrics).length + 1, 0.2);
  const borders = generateColors(Object.keys(metrics).length + 1);

  const metricKeys = Object.keys(metrics);

  // if metrics keys are not empty
  if (metricKeys.length !== 0) {
    metricKeys.forEach((key, index) => {
      const metricData: Metric[] = metrics[key];

      // parse x and y
      const chartData: ChartData = parseMetric("bar", metricData);

      // @ts-expect-error "ignore"
      x.push(...chartData.x);
      y.push(...chartData.y);
      backgroundColor.push(colors[index + 1]);
      borderColor.push(borders[index + 1]);
    });

    dataset.push({
      data: y,
      borderColor,
      backgroundColor,
      borderWidth: 2,
      borderRadius: 2,
      borderSkipped: false,
    });
    data = buildDataforChart(x, dataset, "Metrics", "Values", "bar");
  }

  // eslint-disable-next-line @typescript-eslint/no-unsafe-return
  return data;
}

export function createMetricLineVizData(metrics: RunMetrics): ChartjsData {
  let x: number[] | string[] = [];
  const datasets: ChartjsLineDataset[] = [];
  const metricKeys = Object.keys(metrics);
  const colors = generateColors(Object.keys(metrics).length + 1);
  let data;

  // if metrics keys are not empty
  if (metricKeys.length !== 0) {
    // loop over keys
    // append to the x and y arrays
    metricKeys.forEach((key, index) => {
      const metricData: Metric[] = metrics[key];
      // parse x and y
      const chartData: ChartData = parseMetric("line", metricData);

      if (chartData.x.length > x.length) {
        x = chartData.x;
      }

      datasets.push({
        label: key,
        data: chartData.y,
        borderColor: colors[index + 1],
        backgroundColor: colors[index + 1],
        pointRadius: 1,
      });
    });

    data = buildDataforChart(x, datasets, "Steps", "Values", "line");
  }

  // eslint-disable-next-line @typescript-eslint/no-unsafe-return
  return data;
}

export function exportMetricsToCSV(runMetrics: RunMetrics): string {
  // Define the header
  const metrics = Object.values(runMetrics).flat();

  const header = ["run_uid", "name", "value", "step", "timestamp"];

  // Create the CSV content
  const csvContent = metrics.map((metric) => [
    metric.run_uid,
    metric.name,
    metric.value.toString(),
    metric.step !== null ? metric.step.toString() : "",
    metric.timestamp !== null ? metric.timestamp.toString() : "",
  ]);

  // Combine header and content
  const allRows = [header, ...csvContent];

  // Join rows and columns
  return allRows.map((row) => row.join(",")).join("\n");
}

function downloadCSV(data: string, filename: string) {
  const blob = new Blob([data], { type: "text/csv;charset=utf-8;" });
  const url = window.URL.createObjectURL(blob);

  const link = document.createElement("a");
  link.setAttribute("href", url);
  link.setAttribute("download", `${filename}.csv`);
  link.style.visibility = "hidden";
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

export function downloadMetricCSV(metrics: RunMetrics, filename: string) {
  const csv = exportMetricsToCSV(metrics);
  downloadCSV(csv, filename);
}

export function createMetricVizData(
  metrics: RunMetrics,
  chartType: string
): ChartjsData {
  if (chartType === "bar") {
    return createMetricBarVizData(metrics);
  }
  return createMetricLineVizData(metrics);
}

export function createGroupedMetricBarVizData(
  metrics: Map<string, RunMetrics>,
  metricNames: string[]
): ChartjsData {
  // x will be the metric names
  const datasets: ChartjsGroupedBarDataset[] = [];
  let data;

  const colors = generateColors(metrics.size + 1, 0.2);
  const borders = generateColors(metrics.size + 1);
  const runIdMetricMap = new Map<string, number[]>();

  for (const metricName of metricNames) {
    for (const runId of metrics.keys()) {
      const metricData: Metric[] = metrics.get(runId)![metricName];

      if (!runIdMetricMap.has(runId)) {
        runIdMetricMap.set(runId, []);
      }
      if (metricData) {
        const chartData = parseMetric("bar", metricData);
        runIdMetricMap.get(runId)!.push(chartData.y[0]);
      } else {
        runIdMetricMap.get(runId)!.push(0);
      }
    }
  }

  Array.from(runIdMetricMap.entries()).forEach(([key, value], index) => {
    datasets.push({
      label: key.slice(0, 8),
      data: value,
      borderColor: borders[index + 1],
      backgroundColor: colors[index + 1],
      borderWidth: 2,
      borderRadius: 2,
      borderSkipped: false,
    });
  });

  return buildDataforChart(
    metricNames,
    datasets,
    "Metrics",
    "Values",
    "bar",
    true
  );
}

export function createGroupedMetricLineVizData(
  metrics: Map<string, RunMetrics>,
  metricNames: string[]
): ChartjsData {
  const datasets: ChartjsLineDataset[] = [];

  let x: number[] | string[] = [];
  const colors = generateColors(metrics.size + 1, 0.2);
  const borders = generateColors(metrics.size + 1);
  const runIdMetricMap = new Map<string, Map<string, number[]>>();

  for (const metricName of metricNames) {
    for (const runId of metrics.keys()) {
      const metricData: Metric[] = metrics.get(runId)![metricName];

      if (!runIdMetricMap.has(runId)) {
        runIdMetricMap.set(runId, new Map<string, number[]>());
      }
      if (metricData) {
        const chartData = parseMetric("line", metricData);
        if (chartData.x.length > x.length) {
          x = chartData.x;
        }
        runIdMetricMap.get(runId)!.set(metricName, chartData.y);
      } else {
        runIdMetricMap.get(runId)!.set(metricName, [0]);
      }
    }
  }

  Array.from(runIdMetricMap.entries()).forEach(([key, value], index) => {
    const color = colors[index + 1];
    const borderColor = borders[index + 1];

    Array.from(value.entries()).forEach(([metricName, metricData]) => {
      datasets.push({
        label: `${key.slice(0, 8)}-${metricName}`,
        data: metricData,
        borderColor,
        backgroundColor: borderColor,
        pointRadius: 1,
      });
    });
  });

  return buildDataforChart(x, datasets, "Steps", "Value", "line", true);
}

export function createGroupMetricVizData(
  metrics: Map<string, RunMetrics>,
  metricNames: string[],
  chartType: string
) {
  if (chartType === "bar") {
    return createGroupedMetricBarVizData(metrics, metricNames);
  }
  return createGroupedMetricLineVizData(metrics, metricNames);
}

function compareMetrics(
  currentMetric: number | string,
  compareMetric: number | string | undefined
): string {
  if (typeof compareMetric === "string" || compareMetric === undefined) {
    return "N/A";
  }

  if (typeof currentMetric === "string") {
    return "N/A";
  }

  if (currentMetric === compareMetric) {
    return "equal";
  }
  if (currentMetric > compareMetric) {
    return "greater";
  }
  return "lesser";
}

export function downloadTableMetricsToCSV(
  tableMetrics: Map<string, TableMetric[]>,
  referenceMetrics: Map<string, number>,
  currentUID: string
) {
  const header = ["run_uid", "comparison", "name", "value", "step", "result"];
  const allRows = [header];

  for (const [key, value] of tableMetrics) {
    const comparison = currentUID === key ? "current" : "comparison";
    // Create the CSV content
    const csvContent = value.map((metric) => [
      key,
      comparison,
      metric.name,
      metric.value.toString(),
      metric.step.toString(),
      compareMetrics(metric.value, referenceMetrics.get(metric.name)),
    ]);

    allRows.push(...csvContent);
  }

  // Join rows and columns
  const csv: string = allRows.map((row) => row.join(",")).join("\n");

  downloadCSV(csv, "comparison_metrics");
}
