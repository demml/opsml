interface CardRequest {
  registry_type: string;
  limit: number;
}

interface CardJson {
  date: string;
  app_env: string;
  uid: string;
  repository: string;
  contact: string;
  name: string;
  version: string;
  timestamp: number;
  tags: Map<string, string>;
}

interface CardResponse {
  cards: CardJson[];
}

interface RecentCards {
  modelcards: CardJson[];
  datacards: CardJson[];
  runcards: CardJson[];
}

async function getCards(registry: string): Promise<CardJson[]> {
  const modelcards = await fetch("/opsml/cards/list", {
    method: "POST",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ registry_type: registry, limit: 10 }),
  });

  const response: CardResponse = await modelcards.json();
  return response.cards;
}

async function getRecentCards(): Promise<RecentCards> {
  const modelcards: CardJson[] = await getCards("model");
  const datacards: CardJson[] = await getCards("data");
  const runcards: CardJson[] = await getCards("run");

  const recentCards: RecentCards = {
    modelcards,
    datacards,
    runcards,
  };

  return recentCards;
}

export { getRecentCards, getCards };
export type { CardJson, RecentCards };
