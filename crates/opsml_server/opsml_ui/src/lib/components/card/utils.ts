import { opsmlClient } from "$lib/components/api/client.svelte";
import { RoutePaths } from "$lib/components/api/routes";
import { RegistryType } from "$lib/utils";
import type {
  QueryPageResponse,
  CardSpaceResponse,
  RegistryStatsResponse,
  RegistryPageReturn,
  RegistryStatsRequest,
  VersionPageResponse,
  VersionPageRequest,
} from "$lib/components/card/types";
import type { CardQueryArgs } from "../api/schema";
import { type Card } from "$lib/components/home/types";
import { userStore } from "../user/user.svelte";

export async function getSpaces(
  registry_type: RegistryType
): Promise<CardSpaceResponse> {
  let params = { registry_type: registry_type };
  const response = await opsmlClient.get(
    RoutePaths.LIST_CARD_SPACES,
    params,
    userStore.jwt_token
  );
  return await response.json();
}

export async function getRegistryStats(
  registry_type: RegistryType,
  searchTerm?: string,
  space?: string
): Promise<RegistryStatsResponse> {
  let request: RegistryStatsRequest = {
    registry_type: registry_type,
    search_term: searchTerm,
    space: space,
  };

  const response = await opsmlClient.get(
    RoutePaths.GET_STATS,
    request,
    userStore.jwt_token
  );
  return await response.json();
}

export async function getRegistryPage(
  registry_type: RegistryType,
  sort_by?: string,
  space?: string,
  searchTerm?: string,
  page?: number
): Promise<QueryPageResponse> {
  let params: {
    registry_type: RegistryType;
    sort_by?: string;
    space?: string;
    search_term?: string;
    page?: number;
  } = {
    registry_type: registry_type,
  };

  if (sort_by) {
    params["sort_by"] = sort_by;
  }

  if (space) {
    params["space"] = space;
  }

  if (searchTerm) {
    params["search_term"] = searchTerm;
  }

  if (page) {
    params["page"] = page;
  }

  const response = await opsmlClient.get(
    RoutePaths.GET_REGISTRY_PAGE,
    params,
    userStore.jwt_token
  );
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
    spaces: spaces.spaces,
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

export async function getCardMetadata(
  space: string | undefined,
  name: string | undefined,
  version: string | undefined,
  uid: string | undefined,
  registry_type: RegistryType
): Promise<any> {
  const params: CardQueryArgs = {
    name: name,
    space: space,
    version: version,
    uid: uid,
    registry_type: registry_type,
  };

  const response = await opsmlClient.get(
    RoutePaths.METADATA,
    params,
    userStore.jwt_token
  );
  return await response.json();
}

export async function getVersionPage(
  registry_type: RegistryType,
  space?: string,
  name?: string,
  page?: number
): Promise<VersionPageResponse> {
  const params: VersionPageRequest = {
    registry_type: registry_type,
    space: space,
    name: name,
    page: page,
  };

  const response = await opsmlClient.get(
    RoutePaths.GET_VERSION_PAGE,
    params,
    userStore.jwt_token
  );
  return await response.json();
}

export async function listRecentSpaceCards(
  registry_type: RegistryType,
  space: string
): Promise<Card[]> {
  const params: CardQueryArgs = {
    space: space,
    registry_type: registry_type,
    sort_by_timestamp: true,
    limit: 10,
  };

  const response = await opsmlClient.get(
    RoutePaths.LIST_CARDS,
    params,
    userStore.jwt_token
  );
  const data = (await response.json()) as Card[];

  return data;
}
