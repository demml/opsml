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
  QueryPageRequest,
  CardTagsResponse,
  CardCursor,
  VersionCursor,
  DashBoardStatsResponse,
} from "$lib/components/card/types";
import type { CardQueryArgs } from "$lib/components/api/schema";
import { type Card } from "$lib/components/home/types";
import { createOpsmlClient } from "../api/opsmlClient";

export async function getSpaces(
  fetch: typeof globalThis.fetch,
  registry_type: RegistryType
): Promise<CardSpaceResponse> {
  let params = { registry_type: registry_type };

  const response = await createOpsmlClient(fetch).get(
    RoutePaths.LIST_CARD_SPACES,
    params
  );
  return await response.json();
}

export async function getTags(
  fetch: typeof globalThis.fetch,
  registry_type: RegistryType
): Promise<CardTagsResponse> {
  let params = { registry_type: registry_type };

  const response = await createOpsmlClient(fetch).get(
    RoutePaths.LIST_CARD_TAGS,
    params
  );
  return await response.json();
}

export async function getRegistryStats(
  fetch: typeof globalThis.fetch,
  registry_type: RegistryType,
  searchTerm?: string,
  spaces?: string[],
  tags?: string[]
): Promise<RegistryStatsResponse> {
  let request: RegistryStatsRequest = {
    registry_type: registry_type,
    search_term: searchTerm,
    spaces: spaces,
    tags: tags,
  };

  const response = await createOpsmlClient(fetch).post(
    RoutePaths.GET_STATS,
    request
  );
  return await response.json();
}
export async function getRegistryPage(
  fetch: typeof globalThis.fetch,
  registry_type: RegistryType,
  sort_by?: string,
  spaces?: string[],
  searchTerm?: string,
  tags?: string[],
  page?: number,
  cursor?: CardCursor
): Promise<QueryPageResponse> {
  let request: QueryPageRequest = {
    registry_type: registry_type,
    sort_by: sort_by,
    spaces: spaces,
    search_term: searchTerm,
    tags: tags,
    page: page,
    cursor: cursor, // Include cursor in request
  };

  const response = await createOpsmlClient(fetch).post(
    RoutePaths.GET_REGISTRY_PAGE,
    request
  );
  return await response.json();
}

export async function setupRegistryPage(
  registry_type: RegistryType,
  space: undefined | string = undefined,
  name: string | undefined = undefined,
  fetch: typeof globalThis.fetch
): Promise<RegistryPageReturn> {
  const spaces = space ? [space] : undefined;
  const [registry_spaces, tags, registryStats, registryPage] =
    await Promise.all([
      getSpaces(fetch, registry_type),
      getTags(fetch, registry_type),
      getRegistryStats(fetch, registry_type, name, spaces),
      getRegistryPage(fetch, registry_type, undefined, spaces, name),
    ]);

  return {
    spaces: registry_spaces.spaces,
    tags: tags.tags,
    registry_type: registry_type,
    registryStats: registryStats,
    registryPage: registryPage,
  };
}

export async function getCardMetadata(
  space: string | undefined,
  name: string | undefined,
  version: string | undefined,
  uid: string | undefined,
  registry_type: RegistryType,
  fetch: typeof globalThis.fetch
): Promise<any> {
  const params: CardQueryArgs = {
    name: name,
    space: space,
    version: version,
    uid: uid,
    registry_type: registry_type,
  };

  const response = await createOpsmlClient(fetch).get(
    RoutePaths.METADATA,
    params
  );
  return await response.json();
}

export async function getVersionPage(
  fetch: typeof globalThis.fetch,
  registry_type: RegistryType,
  space: string,
  name: string,
  cursor?: VersionCursor,
  limit?: number
): Promise<VersionPageResponse> {
  const params: VersionPageRequest = {
    registry_type,
    space,
    name,
    cursor,
    limit,
  };

  const response = await createOpsmlClient(fetch).post(
    RoutePaths.GET_VERSION_PAGE,
    params
  );
  return await response.json();
}

export async function listRecentSpaceCards(
  registry_type: RegistryType,
  space: string,
  fetch: typeof globalThis.fetch
): Promise<Card[]> {
  const params: CardQueryArgs = {
    space: space,
    registry_type: registry_type,
    sort_by_timestamp: true,
    limit: 10,
  };

  const response = await createOpsmlClient(fetch).get(
    RoutePaths.LIST_CARDS,
    params
  );
  const data = (await response.json()) as Card[];

  return data;
}

export async function getCardfromUid(
  registry_type: RegistryType,
  uid: string,
  fetch: typeof globalThis.fetch
): Promise<Card[]> {
  const params: CardQueryArgs = {
    uid: uid,
    registry_type: registry_type,
    sort_by_timestamp: true,
    limit: 10,
  };

  const response = await createOpsmlClient(fetch).get(
    RoutePaths.LIST_CARDS,
    params
  );
  const data = (await response.json()) as Card[];
  return data;
}

/** Helper function to get the data profile for a card
 * @param card The DataCard to get the profile for
 * @returns The DataProfile object
 */
export async function getDashboardStats(
  fetch: typeof globalThis.fetch
): Promise<DashBoardStatsResponse> {
  const response = await createOpsmlClient(fetch).get(
    RoutePaths.GET_DASHBOARD_STATS
  );
  const data = (await response.json()) as DashBoardStatsResponse;
  return data;
}
