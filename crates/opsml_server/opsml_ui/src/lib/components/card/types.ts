import type { RegistryType } from "$lib/utils";

export interface RegistryStatsRequest {
  registry_type: RegistryType;
  search_term?: string;
  spaces?: string[];
  tags?: string[];
}

export interface CardCursor {
  offset: number;
  limit: number;
  sort_by: string;
  search_term?: string;
  spaces?: string[];
  tags?: string[];
}

export interface QueryPageRequest {
  registry_type: RegistryType;
  page?: number;
  cursor?: CardCursor;
  limit?: number;
  sort_by?: string;
  search_term?: string;
  spaces?: string[];
  tags?: string[];
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
  uid: string;
  space: string;
  name: string;
  version: string;
  versions: number;
  updated_at: string;
  created_at: string;
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

export interface FilterSummary {
  search_term?: string;
  spaces?: string[];
  tags?: string[];
  sort_by?: string;
}

export interface PageInfo {
  page_size: number;
  offset: number;
  filters: FilterSummary;
}

export interface QueryPageResponse {
  items: CardSummary[];
  has_next: boolean;
  next_cursor?: CardCursor;
  has_previous: boolean;
  previous_cursor?: CardCursor;
  page_info: PageInfo;
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
