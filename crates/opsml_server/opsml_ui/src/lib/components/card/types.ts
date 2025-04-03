import type { RegistryType } from "$lib/utils";

export interface RegistryStatsRequest {
  registry_type: RegistryType;
  search_term?: string;
  repository?: string;
}
export interface RepositoryResponse {
  repositories: string[];
}

export interface QueryStats {
  nbr_names: number;
  nbr_repositories: number;
  nbr_versions: number;
}

export interface RegistryStatsResponse {
  stats: QueryStats;
}

export interface CardSummary {
  repository: string;
  name: string;
  version: string;
  versions: number;
  updated_at: string;
  created_at: string;
  row_num: number;
}

export interface VersionSummary {
  repository: string;
  name: string;
  version: string;
  created_at: string;
  row_num: number;
}

export interface VersionPageResponse {
  summaries: VersionSummary[];
}

export interface QueryPageResponse {
  summaries: CardSummary[];
}

export interface RegistryPageReturn {
  spaces: string[];
  registry_type: RegistryType;
  registryStats: RegistryStatsResponse;
  registryPage: QueryPageResponse;
}

export interface VersionPageRequest {
  registry_type: RegistryType;
  repository?: string;
  name?: string;
  page?: number;
}
