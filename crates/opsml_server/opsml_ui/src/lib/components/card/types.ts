import type { RegistryType } from "$lib/utils";

export type RepositoryResponse = {
  repositories: string[];
};

export type QueryStats = {
  nbr_names: number;
  nbr_repositories: number;
  nbr_versions: number;
};

export type RegistryStatsResponse = {
  stats: QueryStats;
};

export type CardSummary = {
  repository: string;
  name: string;
  version: string;
  versions: number;
  updated_at: string; // Assuming NaiveDateTime is serialized as a string
  created_at: string; // Assuming NaiveDateTime is serialized as a string
  row_num: number;
};

export type QueryPageResponse = {
  summaries: CardSummary[];
};

export interface RegistryPageReturn {
  spaces: string[];
  registry_type: RegistryType;
  registryStats: RegistryStatsResponse;
  registryPage: QueryPageResponse;
}
