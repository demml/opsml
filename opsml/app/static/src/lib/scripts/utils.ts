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
} from "$lib/scripts/types";
import { apiHandler } from "$lib/scripts/apiHandler";

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

  let cards = await apiHandler
    .post(CommonPaths.LIST_CARDS, request, "application/json")
    .then((res) => res.json());

  return cards;
}

export async function getMessages(
  uid: string,
  registry: string
): Promise<MessageThread> {
  const comments: MessageThread = await apiHandler
    .get(`/opsml/${registry}/messages?uid=${uid}`)
    .then((res) => res.json());

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
  let dataCard = await apiHandler
    .post(CommonPaths.DATACARD, request)
    .then((res) => res.json());

  return dataCard;
}

export async function getRunCard(request: CardRequest): Promise<RunCard> {
  let runCard = await apiHandler
    .post(CommonPaths.RUNCARD, request)
    .then((res) => res.json());

  return runCard;
}

export async function getRunMetricNames(uid: string): Promise<MetricNames> {
  const request = { run_uid: uid, names_only: true };

  let names: MetricNames = await apiHandler
    .post(CommonPaths.METRICS, request)
    .then((res) => res.json());

  return names;
}

export async function getRunMetrics(
  uid: string,
  name?: string[]
): Promise<RunMetrics> {
  const request = { run_uid: uid };

  if (name) {
    request["name"] = name;
  }

  let metrics: Metrics = await apiHandler
    .post(CommonPaths.METRICS, request)
    .then((res) => res.json());

  const runMetrics: RunMetrics = {};

  if (metrics.metric.length > 0) {
    // create loop for metricNames.metric
    for (let metric of metrics.metric) {
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

  let params: Parameters = await apiHandler
    .post(CommonPaths.PARAMETERS, request)
    .then((res) => res.json());

  return params;
}

export async function getRunGraphs(
  repository: string,
  name: string,
  version: string
): Promise<Map<string, Graph>> {
  let params = new URLSearchParams();
  params.append("repository", repository);
  params.append("name", name);
  params.append("version", version);

  let url = CommonPaths.GRAPHS + "?" + params.toString();
  let graphs = await apiHandler.get(url).then((res) => res.json());

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
  let markdown: FileExists = await apiHandler
    .get(
      CommonPaths.FILE_EXISTS +
        "?" +
        new URLSearchParams({
          path: markdownPath,
        }).toString()
    )
    .then((res) => res.json());

  let readme: string = "";

  if (markdown.exists) {
    // fetch markdown

    let viewData = await apiHandler
      .get(
        CommonPaths.FILES_VIEW +
          "?" +
          new URLSearchParams({
            path: markdownPath,
          }).toString()
      )
      .then((res) => res.json());

    readme = viewData.content.content;
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
  uid: string | null,
  name: string,
  repository: string,
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

    if (version) {
      metaAttr.version = version;
    }
  }

  let res: ModelMetadata = await apiHandler
    .post(CommonPaths.MODEL_METADATA, metaAttr)
    .then((res) => res.json());

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
  let urlPath = CommonPaths.FILE_INFO + `?path=${basePath}`;
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

  let fileInfo: Files = await apiHandler.get(urlPath).then((res) => res.json());

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
  let repos: repositories = await apiHandler
    .get(
      CommonPaths.REPOSITORIES +
        "?" +
        new URLSearchParams({
          registry_type: registry,
        }).toString()
    )
    .then((res) => res.json());

  let stats: registryStats = await apiHandler
    .get(
      CommonPaths.REGISTRY_STATS +
        "?" +
        new URLSearchParams({
          registry_type: registry,
        }).toString()
    )
    .then((res) => res.json());

  let page: registryPage = await apiHandler
    .get(
      CommonPaths.QUERY_PAGE +
        "?" +
        new URLSearchParams({
          registry_type: registry,
          page: "0",
        }).toString()
    )
    .then((res) => res.json());

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
  let url: string = CommonPaths.USER_AUTH + "?username=" + username;

  let response = await apiHandler.get(url);
  if (response.ok) {
    user = await response.json();
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
  let response = await apiHandler.put(CommonPaths.USER_AUTH, user);
  if (!response.ok) {
    return {
      updated: false,
    };
  } else {
    let res = await response.json();
    return {
      updated: res["updated"],
    };
  }
}

export function goTop() {
  document.body.scrollIntoView();
}

export function checkPasswordStrength(password: string): PasswordStrength {
  let point = 0;
  let widthPower = [0, 20, 40, 60, 80, 100];
  let colorPower = [
    "red-600",
    "orange-600",
    "yellow-500",
    "lime-500",
    "green-500",
  ];
  let message = "Missing:";

  let isLength = password.length >= 8;
  let hasNum = /[0-9]/.test(password);
  let hasLower = /[a-z]/.test(password);
  let hasUpper = /[A-Z]/.test(password);
  let hasSpecial = /[^0-9a-zA-Z]/.test(password);

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

  let power = widthPower[point];
  let color = colorPower[point];

  return { power, color, message };
}

export function delay(fn, ms: number) {
  let timer = 0;
  return function (...args) {
    clearTimeout(timer);

    // @ts-ignore
    timer = window.setTimeout(fn.bind(this, ...args), ms || 0);
  };
}

export const sleep = (ms: number) =>
  new Promise((resolve) => setTimeout(resolve, ms));

export function sortMetrics(metrics: Metrics): RunMetrics {
  let sorted: RunMetrics = {};

  // create loop for metricNames.metric
  for (let metric of metrics.metric) {
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
  let table: Map<string, TableMetric[]> = new Map();
  for (let [key, value] of metrics) {
    table.set(key, []);

    metricsToPlot.forEach((metric) => {
      let metricValue: Metric[] = value[metric];

      if (metricValue) {
        table.get(key)!.push({
          name: metric,
          value: metricValue[metricValue.length - 1].value,
        });
      } else {
        table.get(key)!.push({
          name: metric,
          value: "N/A",
        });
      }
    });
  }
  return table;
}

function parseMetric(type: string, metric: Metric[]): ChartData {
  let x: any = [];
  let y: number[] = [];

  if (type == "line") {
    for (let data of metric) {
      y.push(data.value);
      x.push(data.step || 0);
    }
  } else {
    y.push(metric[metric.length - 1].value);
    x.push(metric[metric.length - 1].name);
  }

  return { x, y };
}

const handleResize = (chart) => {
  chart.resize();
};

export function buildDataforChart(
  x: number[] | string[],
  datasets: ChartjsBarDataset[] | ChartjsLineDataset[],
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
      datasets: datasets,
    },
    options: {
      plugins: {
        zoom: zoomOptions,
        legend: legend,
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
          grace: grace,
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
    } else {
      return `rgb(${r}, ${g}, ${b})`;
    }
  });
}

function hslToRgb(h: number, s: number, l: number): [number, number, number] {
  h /= 360;
  let r: number, g: number, b: number;

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
  let x: any[] = [];
  let y: number[] = [];
  let backgroundColor: string[] = [];
  let borderColor: string[] = [];
  let data;
  let dataset: ChartjsBarDataset[] = [];

  let colors = generateColors(Object.keys(metrics).length + 1, 0.2);
  let borders = generateColors(Object.keys(metrics).length + 1);

  let metricKeys = Object.keys(metrics);

  // if metrics keys are not empty
  if (metricKeys.length !== 0) {
    metricKeys.forEach(function (key, index) {
      let metricData: Metric[] = metrics[key];

      // parse x and y
      let chartData: ChartData = parseMetric("bar", metricData);

      x.push(...chartData.x);
      y.push(...chartData.y);
      backgroundColor.push(colors[index + 1]);
      borderColor.push(borders[index + 1]);
    });

    dataset.push({
      data: y,
      borderColor: borderColor,
      backgroundColor: backgroundColor,
      borderWidth: 2,
      borderRadius: 2,
      borderSkipped: false,
    });
    data = buildDataforChart(x, dataset, "Metrics", "Values", "bar");
  }

  return data;
}

export function createMetricLineVizData(metrics: RunMetrics): ChartjsData {
  let x: any[] = [];
  let datasets: ChartjsLineDataset[] = [];
  let metricKeys = Object.keys(metrics);
  let colors = generateColors(Object.keys(metrics).length + 1);
  let data;

  // if metrics keys are not empty
  if (metricKeys.length !== 0) {
    // loop over keys
    // append to the x and y arrays
    metricKeys.forEach(function (key, index) {
      let metricData: Metric[] = metrics[key];
      // parse x and y
      let chartData: ChartData = parseMetric("line", metricData);

      if (chartData.x.length > x.length) {
        x = chartData.x;
      }

      datasets.push({
        label: key,
        data: chartData.y,
        borderColor: colors[index + 1],
        backgroundColor: colors[index + 1],
      });
    });

    data = buildDataforChart(x, datasets, "Steps", "Values", "line");
  }
  return data;
}

export function exportMetricsToCSV(runMetrics: RunMetrics): string {
  // Define the header
  let metrics = Object.values(runMetrics).flat();

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
  } else {
    return createMetricLineVizData(metrics);
  }
}

export function createGroupedMetricBarVizData(
  metrics: Map<string, RunMetrics>,
  metricNames: string[]
): ChartjsData {
  // x will be the metric names
  let datasets: ChartjsGroupedBarDataset[] = [];
  let data;

  let colors = generateColors(metrics.size + 1, 0.2);
  let borders = generateColors(metrics.size + 1);
  let runIdMetricMap = new Map<string, number[]>();

  for (let metricName of metricNames) {
    for (let runId of metrics.keys()) {
      let metricData: Metric[] = metrics.get(runId)![metricName];

      if (!runIdMetricMap.has(runId)) {
        runIdMetricMap.set(runId, []);
      }
      if (metricData) {
        let chartData = parseMetric("bar", metricData);
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

  data = buildDataforChart(
    metricNames,
    datasets,
    "Metrics",
    "Values",
    "bar",
    true
  );

  return data;
}

export function createGroupMetricVizData(
  metrics: Map<string, RunMetrics>,
  metricNames: string[],
  chartType: string
) {
  if (chartType === "bar") {
    return createGroupedMetricBarVizData(metrics, metricNames);
  }
}
