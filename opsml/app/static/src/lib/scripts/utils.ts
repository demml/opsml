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
  type ChartjsScatterDataset,
  type FileViewResponse,
  type UserUpdated,
  type RunGraph,
  type HardwareMetricsResponse,
  type HardwareMetricRecord,
  type ParsedHardwareMetrics,
  type HardwareCharts,
} from "$lib/scripts/types";
import { apiHandler } from "$lib/scripts/apiHandler";

export async function getRepos(registry: string) {
  const repos = await apiHandler.get(
    `${CommonPaths.REPOSITORIES}?${new URLSearchParams({
      registry_type: registry,
    }).toString()}`
  );

  const response = (await repos.json()) as repositories;
  return response.repositories;
}

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
): Promise<Map<string, RunGraph>> {
  const params = new URLSearchParams();
  params.append("repository", repository);
  params.append("name", name);
  params.append("version", version);

  const url = `${CommonPaths.GRAPHS}?${params.toString()}`;

  const graphs = (await apiHandler.get(url).then((res) => res.json())) as Map<
    string,
    RunGraph
  >;

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
 * @param {string | undefined} uid
 * @param {string} name
 * @param {string} repository
 * @param {string | undefined} version
 *
 * @returns {Promise<ModelMetadata>} metadata
 *
 */
export async function getModelMetadata(
  name: string,
  repository: string,
  uid?: string,
  version?: string
): Promise<ModelMetadata> {
  let metaAttr: metadataRequest = {};

  if (uid) {
    metaAttr = {
      uid,
    };
  } else {
    metaAttr = {
      name,
      repository,
    };

    if (version) {
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
 * @param {string | undefined} subdir
 *
 * @returns {Promise<FileSetup>} setup
 *
 */
export async function setupFiles(
  basePath: string,
  repository: string,
  name: string,
  version?: string,
  subdir?: string
): Promise<FileSetup> {
  let urlPath = `${CommonPaths.FILE_INFO}?path=${basePath}`;
  let displayPath = [repository, name, `v${version}`];
  let prevPath: string = basePath;

  if (subdir) {
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

// Function for searching a registry page given a registry, sort_by, repository, name, and page
//
// Args:
//   registry: string - the registry to search
//   sort_by: string - the sort_by to use
//   repository: string - the repository to use
//   name: string - the name to use
//   page: number - the page to use
//
// Returns:
//   registryQuery - the page for the registry
export async function getRegistryPage(
  registry: string,
  sort_by: string | undefined,
  repository: string | undefined,
  search_term: string | undefined,
  page: number | undefined
): Promise<registryPage> {
  // build request
  const params = new URLSearchParams();
  params.append("registry_type", registry);

  if (sort_by) {
    params.append("sort_by", sort_by);
  }
  if (repository) {
    params.append("repository", repository);
  }
  if (search_term) {
    params.append("search_term", search_term);
  }
  if (page) {
    params.append("page", page.toString());
  }

  const url = `${CommonPaths.QUERY_PAGE}?${params.toString()}`;
  const page_resp = await apiHandler.get(url);

  // const page_resp = await fetch(`/opsml/cards/registry/query/page?${params}`);

  const response = (await page_resp.json()) as registryPage;
  return response;
}

// Function for searching general stats given a registry and search term
//
// Args:
//   registry: string - the registry to search
//   searchTerm: string - the search term to use
//
// Returns:
//   registryQuery - the general stats for the registry
export async function getRegistryStats(
  registry: string,
  searchTerm: string | undefined
): Promise<registryStats> {
  const params = new URLSearchParams();
  params.append("registry_type", registry);
  if (searchTerm) {
    params.append("search_term", searchTerm);
  }

  const url = `${CommonPaths.REGISTRY_STATS}?${params.toString()}`;
  const page_resp = await apiHandler.get(url);

  const response = (await page_resp.json()) as registryStats;
  return response;
}

/**
 * Get user information
 * @param {string} username
 * @returns {Promise<UserResponse>} user
 *
 */
export async function getUser(username: string): Promise<UserResponse> {
  let user: User | undefined;
  let error: string | undefined;
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

export const handleResize = (chart) => {
  // eslint-disable-next-line @typescript-eslint/no-unsafe-member-access, @typescript-eslint/no-unsafe-call
  chart.resize();
};

export function buildDataforChart(
  x: number[] | string[],
  datasets:
    | ChartjsBarDataset[]
    | ChartjsLineDataset[]
    | ChartjsGroupedBarDataset[]
    | ChartjsScatterDataset[],
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

export function generateColors(count: number, opacity?: number): string[] {
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
    metric.step ? metric.step.toString() : "",
    metric.timestamp ? metric.timestamp.toString() : "",
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

export async function getHardwareMetrics(
  run_uid: string
): Promise<HardwareMetricsResponse> {
  const metrics = await apiHandler.get(
    `${CommonPaths.HARDWARE}?${new URLSearchParams({
      run_uid: run_uid,
    }).toString()}`
  );

  const response = (await metrics.json()) as HardwareMetricsResponse;
  return response;
}

export function parseHardwareMetrics(
  metrics: HardwareMetricRecord[]
): ParsedHardwareMetrics {
  const x: Date[] = [];
  const cpu_overall: number[] = [];
  const cpu_per_core: number[][] = [];
  const network_rx: number[] = [];
  const network_tx: number[] = [];
  const memory: number[] = [];
  const gpu_overall: number[] = [];
  const gpu_per_core: number[][] = [];

  for (const metric of metrics) {
    x.push(new Date(metric.created_at));

    // handle cpu
    cpu_overall.push(
      Number(metric.metrics.cpu.cpu_percent_utilization.toFixed(2))
    );

    // handle cpu cores
    if (metric.metrics.cpu.cpu_percent_per_core) {
      const _cpu_per_core = metric.metrics.cpu.cpu_percent_per_core.map(
        (core) => Number(core.toFixed(2))
      );
      cpu_per_core.push(_cpu_per_core);
    }

    // handle network
    network_rx.push(
      Number((metric.metrics.network.bytes_recv / 1024 ** 2).toFixed(2))
    );
    network_tx.push(
      Number((metric.metrics.network.bytes_sent / 1024 ** 2).toFixed(2))
    );

    // handle memory
    memory.push(Number(metric.metrics.memory.sys_ram_percent_used.toFixed(2)));

    // handle gpu
    if (metric.metrics.gpu) {
      gpu_overall.push(
        Number(metric.metrics.gpu.gpu_percent_utilization.toFixed(2))
      );

      // handle gpu cores
      if (metric.metrics.gpu.gpu_percent_per_core) {
        const _gpu_per_core = metric.metrics.gpu.gpu_percent_per_core.map(
          (core) => Number(core.toFixed(2))
        );
        gpu_per_core.push(_gpu_per_core);
      }
    }
  }

  return {
    x,
    cpu_overall,
    cpu_per_core,
    network_rx,
    network_tx,
    memory,
    gpu_overall,
    gpu_per_core,
  };
}

export function buildTimeChart(
  x: Date[],
  datasets: ChartjsLineDataset[],
  x_label: string,
  y_label: string,
  showLegend: boolean = false
): ChartjsData {
  const grace = "0%";
  let legend = {
    display: false,
  };

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
    type: "line",
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
          type: "time",
          time: {
            displayFormats: {
              hour: "HH:mm",
              minute: "HH:mm",
              second: "HH:mm:ss",
            },
          },
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

export function createTimeSeriesChart(
  x: Date[],
  y: number[],
  label: string,
  y_label: string
): ChartjsData {
  const datasets: ChartjsLineDataset[] = [];
  const borderColors = generateColors(3);
  const backgroundColors = generateColors(3, 0.2);

  datasets.push({
    label,
    data: y,
    borderColor: borderColors[2],
    backgroundColor: backgroundColors[2],
    pointRadius: 2,
    fill: true,
  });

  return buildTimeChart(x, datasets, "Time", y_label, false);
}

export function createTimeSeriesGroupedChart(
  x: Date[],
  y: number[][],
  labels: string[],
  y_label: string
): ChartjsData {
  const datasets: ChartjsLineDataset[] = [];
  const colors = generateColors(labels.length + 1);

  labels.forEach((label, index) => {
    datasets.push({
      label,
      data: y.map((row) => row[index]),
      borderColor: colors[index + 1],
      backgroundColor: colors[index + 1],
      pointRadius: 2,
      fill: false,
    });
  });

  return buildTimeChart(x, datasets, "Time", y_label, true);
}

export function createHardwareCharts(
  metrics: ParsedHardwareMetrics
): HardwareCharts {
  const cpu_overall = createTimeSeriesChart(
    metrics.x,
    metrics.cpu_overall,
    "CPU Utilization",
    "% Utilization"
  );

  let cpu_per_core;
  if (metrics.cpu_per_core.length > 0) {
    cpu_per_core = createTimeSeriesGroupedChart(
      metrics.x,
      metrics.cpu_per_core,
      Array.from({ length: metrics.cpu_per_core[0].length }, (_, i) => {
        return `CPU Core ${i}`;
      }),
      "% Utilization"
    );
  }

  const network_rx = createTimeSeriesChart(
    metrics.x,
    metrics.network_rx,
    "Network RX",
    "Bytes (MB)"
  );

  const network_tx = createTimeSeriesChart(
    metrics.x,
    metrics.network_tx,
    "Network TX",
    "Bytes (MB)"
  );

  const memory = createTimeSeriesChart(
    metrics.x,
    metrics.memory,
    "Utilization (%)",
    "Percentage"
  );

  let gpu_overall;
  let gpu_per_core;
  if (metrics.gpu_overall.length > 0) {
    gpu_overall = createTimeSeriesChart(
      metrics.x,
      metrics.gpu_overall,
      "GPU Utilization",
      "Percentage"
    );

    gpu_per_core = createTimeSeriesGroupedChart(
      metrics.x,
      metrics.gpu_per_core,
      Array.from({ length: metrics.gpu_per_core[0].length }, (_, i) => {
        return `GPU Core ${i}`;
      }),
      "Percentage"
    );
  }

  return {
    cpu_overall,

    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    cpu_per_core,
    network_rx,
    network_tx,
    memory,

    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    gpu_overall,

    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    gpu_per_core,
  };
}
