import type { RegistryType } from "$lib/utils";

export interface RegistryStatsRequest {
  registry_type: RegistryType;
  search_term?: string;
  spaces?: string[];
  tags?: string[];
}
export interface QueryPageRequest {
  registry_type: RegistryType;
  sort_by?: string;
  spaces?: string[];
  search_term?: string;
  tags?: string[];
  page?: number;
}
export interface CardSpaceResponse {
  spaces: string[];
}

export interface CardTagsResponse {
  tags: string[];
}

export interface QueryStats {
  nbr_names: number;
  nbr_spaces: number;
  nbr_versions: number;
}

export interface RegistryStatsResponse {
  stats: QueryStats;
}

export interface CardSummary {
  space: string;
  name: string;
  version: string;
  versions: number;
  updated_at: string;
  created_at: string;
  row_num: number;
}

export interface VersionSummary {
  space: string;
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
  tags: string[];
  registry_type: RegistryType;
  registryStats: RegistryStatsResponse;
  registryPage: QueryPageResponse;
}

export interface VersionPageRequest {
  registry_type: RegistryType;
  space?: string;
  name?: string;
  page?: number;
}
