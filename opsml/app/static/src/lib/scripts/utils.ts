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
): Promise<Metrics> {
  const request = { run_uid: uid };

  if (name) {
    request["name"] = name;
  }

  let metrics: Metrics = await apiHandler
    .post(CommonPaths.METRICS, request)
    .then((res) => res.json());

  return metrics;
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
