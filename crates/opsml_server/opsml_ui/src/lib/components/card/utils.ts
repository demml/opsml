import { opsmlClient } from "$lib/components/api/client.svelte";
import { RoutePaths } from "$lib/components/api/routes";
import { RegistryType } from "$lib/utils";
import type {
  QueryPageResponse,
  RepositoryResponse,
  RegistryStatsResponse,
  RegistryPageReturn,
  RegistryStatsRequest,
  VersionPageResponse,
  VersionPageRequest,
} from "$lib/components/card/types";
import type { CardQueryArgs } from "../api/schema";
import { type Card } from "$lib/components/home/types";

export async function getSpaces(
  registry_type: RegistryType
): Promise<RepositoryResponse> {
  let params = { registry_type: registry_type };
  const response = await opsmlClient.get(RoutePaths.LIST_SPACES, params);
  return await response.json();
}

export async function getRegistryStats(
  registry_type: RegistryType,
  searchTerm?: string,
  repository?: string
): Promise<RegistryStatsResponse> {
  let request: RegistryStatsRequest = {
    registry_type: registry_type,
    search_term: searchTerm,
    repository: repository,
  };

  const response = await opsmlClient.get(RoutePaths.GET_STATS, request);
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
  registry_type: RegistryType,
  space: string | undefined = undefined,
  name: string | undefined = undefined
): Promise<RegistryPageReturn> {
  const [spaces, registryStats, registryPage] = await Promise.all([
    getSpaces(registry_type),
    getRegistryStats(registry_type, name, space),
    getRegistryPage(registry_type, undefined, space, name),
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

export async function getCardUid(
  registry_type: RegistryType,
  name?: string,
  repository?: string,
  version?: string
): Promise<string> {
  const params: CardQueryArgs = {
    name: name,
    repository: repository,
    version: version,
    registry_type: registry_type,
    limit: 1,
  };

  const response = await opsmlClient.get(RoutePaths.LIST_CARDS, params);
  const data = (await response.json()) as Card[];

  // @ts-ignore
  return data[0].data.uid;
}

export async function getUID(
  url: URL,
  registry: RegistryType
): Promise<string> {
  const name = (url as URL).searchParams.get("name") as string | undefined;
  const repository = (url as URL).searchParams.get("repository") as
    | string
    | undefined;
  const version = (url as URL).searchParams.get("version") as
    | string
    | undefined;
  const uid = (url as URL).searchParams.get("uid") as string | undefined;

  // If uid is provided, return it
  if (uid) {
    return uid;
  }

  return await getCardUid(registry, name, repository, version);
}
export async function getCardMetadata(
  uid: string,
  registry_type: RegistryType
): Promise<any> {
  const params: CardQueryArgs = {
    uid: uid,
    registry_type: registry_type,
  };

  const response = await opsmlClient.get(RoutePaths.METADATA, params);
  return await response.json();
}

export async function getVersions(
  registry_type: RegistryType,
  repository?: string,
  name?: string,
  page?: number
): Promise<VersionPageResponse> {
  const params: VersionPageRequest = {
    registry_type: registry_type,
    repository: repository,
    name: name,
    page: page,
  };

  const response = await opsmlClient.get(RoutePaths.GET_VERSION_PAGE, params);
  return await response.json();
}
