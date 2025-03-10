import { opsmlClient } from "$lib/components/api/client.svelte";
import { RoutePaths } from "$lib/components/api/routes";
import type { RegistryType } from "$lib/utils";
import type {
  QueryPageResponse,
  RepositoryResponse,
  RegistryStatsResponse,
  RegistryPageReturn,
} from "$lib/components/card/types";

export async function getSpaces(
  registry_type: RegistryType
): Promise<RepositoryResponse> {
  let params = { registry_type: registry_type };
  const response = await opsmlClient.get(RoutePaths.LIST_SPACES, params);
  return await response.json();
}

export async function getRegistryStats(
  registry_type: RegistryType,
  searchTerm?: string
): Promise<RegistryStatsResponse> {
  let params: { registry_type: RegistryType; search_term?: string } = {
    registry_type: registry_type,
  };

  if (searchTerm) {
    params["search_term"] = searchTerm as string;
  }

  const response = await opsmlClient.get(RoutePaths.GET_STATS, params);
  return await response.json();
}

export async function getRegistryPage(
  registry_type: RegistryType,
  sort_by?: string,
  repository?: string,
  searchTerm?: string,
  page?: number
): Promise<QueryPageResponse> {
  let params: {
    registry_type: RegistryType;
    sort_by?: string;
    repository?: string;
    search_term?: string;
    page?: number;
  } = {
    registry_type: registry_type,
  };

  if (sort_by) {
    params["sort_by"] = sort_by;
  }

  if (repository) {
    params["repository"] = repository;
  }

  if (searchTerm) {
    params["search_term"] = searchTerm;
  }

  if (page) {
    params["page"] = page;
  }

  const response = await opsmlClient.get(RoutePaths.GET_REGISTRY_PAGE, params);
  return await response.json();
}

export async function setupRegistryPage(
  registry_type: RegistryType
): Promise<RegistryPageReturn> {
  const [spaces, registryStats, registryPage] = await Promise.all([
    getSpaces(registry_type),
    getRegistryStats(registry_type),
    getRegistryPage(registry_type),
  ]);

  return {
    spaces: spaces.repositories,
    registry_type: registry_type,
    registryStats: registryStats,
    registryPage: registryPage,
  };
}

export function getBgColor(): string {
  const classes = [
    "bg-primary-500",
    "bg-secondary-500",
    "bg-tertiary-500",
    "bg-success-500",
    "bg-warning-500",
    "bg-error-500",
  ];
  const randomIndex = Math.floor(Math.random() * classes.length);
  return classes[randomIndex];
}

export async function getMetadata(
  name: string,
  repository: string,
  version: string
): Promise<Any> {
  const params = {
    name: name,
    repository: repository,
    uid: uid,
    version: version,
  };

  const response = await opsmlClient.get(RoutePaths.GET_METADATA, params);
  return await response.json();
}
