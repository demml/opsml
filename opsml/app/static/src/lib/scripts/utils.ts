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
} from "$lib/scripts/types";

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
  const cards: CardResponse = await fetch("/opsml/cards/list", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
  }).then((res) => res.json());

  return cards;
}

export async function getMessages(
  uid: string,
  registry: string
): Promise<MessageThread> {
  const comments: MessageThread = await fetch(
    `/opsml/${registry}/messages?uid=${uid}`
  ).then((res) => res.json());

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

  await fetch(`/opsml/${message.registry}/messages`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
  }).then((res) => res.json());
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

  await fetch(`/opsml/${message.registry}/messages`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
  }).then((res) => res.json());
}

export async function getDataCard(
  request: CardRequest
): Promise<DataCardMetadata> {
  const dataCard: DataCardMetadata = await fetch("/opsml/data/card", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
  }).then((res) => res.json());

  return dataCard;
}

export async function getRunCard(request: CardRequest): Promise<RunCard> {
  const runCard: RunCard = await fetch("/opsml/run/card", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
  }).then((res) => res.json());

  return runCard;
}

export async function getRunMetricNames(uid: string): Promise<MetricNames> {
  const request = { run_uid: uid, names_only: true };

  const names: MetricNames = await fetch("/opsml/metrics", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
  }).then((res) => res.json());

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

  const metrics: Metrics = await fetch("/opsml/metrics", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
  }).then((res) => res.json());

  return metrics;
}

export async function getRunParameters(uid: string): Promise<Parameters> {
  const request = { run_uid: uid };

  const params: Parameters = await fetch("/opsml/parameters", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
  }).then((res) => res.json());

  return params;
}

export async function getRunGraphs(
  repository: string,
  name: string,
  version: string
): Promise<Map<string, Graph>> {
  const graphs = await fetch(
    `/opsml/runs/graphs?repository=${repository}&name=${name}&version=${version}`
  ).then((res) => res.json());

  return graphs;
}
