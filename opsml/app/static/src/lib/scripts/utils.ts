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
