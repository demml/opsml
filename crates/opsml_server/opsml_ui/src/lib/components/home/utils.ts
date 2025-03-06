import { apiHandler } from "$lib/components/api/apiHandler";
import { RoutePaths } from "$lib/components/api/routes";

interface BaseCardJson {
  uid: string;
  created_at: string;
  app_env: string;
  name: string;
  repository: string;
  version: string;
  timestamp: number;
  tags: string[];
}

// Type discriminated union for different card types
type CardJson = BaseCardJson & {
  type: "Data" | "Model" | "Experiment" | "Audit" | "Prompt";
  data: Record<string, any>; // Type for additional fields specific to each card type
};

interface RecentCards {
  modelcards: CardJson[];
  datacards: CardJson[];
  runcards: CardJson[];
}

interface CardQueryArgs {
  registry_type: string;
  limit?: number;
  sort_by_timestamp?: boolean;
}

async function getCards(registry: string): Promise<CardJson[]> {
  const response = await apiHandler.post(
    RoutePaths.LIST_CARDS,
    {
      registry_type: registry,
      limit: 10,
      sort_by_timestamp: true,
    } as CardQueryArgs,
    "application/json",
    { Accept: "application/json" }
  );

  const data = (await response.json()) as CardJson[];

  return data;
}

async function getRecentCards(): Promise<RecentCards> {
  const [modelcards, datacards, runcards] = await Promise.all([
    getCards("model"),
    getCards("data"),
    getCards("run"),
  ]);

  return {
    modelcards,
    datacards,
    runcards,
  };
}

export { getRecentCards, getCards };
export type { CardJson, RecentCards };
