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
} from "$lib/server/card/types";
import type { CardQueryArgs } from "$lib/components/api/schema";
import { type Card } from "$lib/components/home/types";
import { createOpsmlClient } from "../api/opsmlClient";

export async function getSpaces(
  registry_type: RegistryType,
  jwt_token: string | undefined,
  fetch: typeof globalThis.fetch
): Promise<CardSpaceResponse> {
  let params = { registry_type: registry_type };
  const opsmlClient = createOpsmlClient(fetch, jwt_token);
  const response = await opsmlClient.get(RoutePaths.LIST_CARD_SPACES, params);
  return await response.json();
}

export async function getTags(
  registry_type: RegistryType,
  jwt_token: string | undefined,
  fetch: typeof globalThis.fetch
): Promise<CardTagsResponse> {
  let params = { registry_type: registry_type };
  const opsmlClient = createOpsmlClient(fetch, jwt_token);
  const response = await opsmlClient.get(RoutePaths.LIST_CARD_TAGS, params);
  return await response.json();
}

export async function getRegistryStats(
  opsmlClient: ReturnType<typeof createOpsmlClient>,
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

  const response = await opsmlClient.post(RoutePaths.GET_STATS, request);
  return await response.json();
}

export async function getRegistryPage(
  opsmlClient: ReturnType<typeof createOpsmlClient>,
  registry_type: RegistryType,
  sort_by?: string,
  spaces?: string[],
  searchTerm?: string,
  tags?: string[],
  page?: number
): Promise<QueryPageResponse> {
  let request: QueryPageRequest = {
    registry_type: registry_type,
    sort_by: sort_by,
    spaces: spaces,
    search_term: searchTerm,
    tags: tags,
    page: page,
  };

  const response = await opsmlClient.post(
    RoutePaths.GET_REGISTRY_PAGE,
    request
  );

  console.log("Registry Page Response:", JSON.stringify(response));

  return await response.json();
}

export async function setupRegistryPage(
  registry_type: RegistryType,
  space: undefined | string = undefined,
  name: string | undefined = undefined,
  jwt_token: string | undefined,
  fetch: typeof globalThis.fetch
): Promise<RegistryPageReturn> {
  let opsmlClient = createOpsmlClient(fetch, jwt_token);
  const spaces = space ? [space] : undefined;
  const [registry_spaces, tags, registryStats, registryPage] =
    await Promise.all([
      getSpaces(opsmlClient, registry_type),
      getTags(opsmlClient, registry_type),
      getRegistryStats(opsmlClient, registry_type, name, spaces),
      getRegistryPage(opsmlClient, registry_type, undefined, spaces, name),
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
  registry_type: RegistryType
): Promise<any> {
  const params: CardQueryArgs = {
    name: name,
    space: space,
    version: version,
    uid: uid,
    registry_type: registry_type,
  };

  const response = await opsmlClient.get(RoutePaths.METADATA, params);
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

  const response = await opsmlClient.get(RoutePaths.GET_VERSION_PAGE, params);
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

  const response = await opsmlClient.get(RoutePaths.LIST_CARDS, params);
  const data = (await response.json()) as Card[];

  return data;
}

export async function getCardfromUid(
  registry_type: RegistryType,
  uid: string
): Promise<Card[]> {
  const params: CardQueryArgs = {
    uid: uid,
    registry_type: registry_type,
    sort_by_timestamp: true,
    limit: 10,
  };

  const response = await opsmlClient.get(RoutePaths.LIST_CARDS, params);
  const data = (await response.json()) as Card[];
  return data;
}
