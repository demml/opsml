import { createInternalApiClient } from "$lib/api/internalClient";
import type {
  RegistryStatsResponse,
  QueryPageResponse,
  VersionPageResponse,
  CardCursor,
  VersionCursor,
} from "$lib/components/card/types";
import { RegistryType } from "$lib/utils";
import { ServerPaths } from "$lib/components/api/routes";

/** Helper function to call the server registry page endpoint */
export async function getRegistryPage(
  fetch: typeof globalThis.fetch,
  registry_type: RegistryType,
  sort_by: string | undefined,
  spaces: string[] | undefined,
  searchTerm: string | undefined,
  tags: string[] | undefined,
  page: number | undefined
): Promise<QueryPageResponse> {
  let resp = await createInternalApiClient(fetch).post(
    ServerPaths.REGISTRY_PAGE,
    {
      registry_type,
      sort_by,
      spaces,
      searchTerm,
      tags,
      page,
    }
  );
  return (await resp.json()) as QueryPageResponse;
}

/** Helper function to call the server registry stats endpoint */
export async function getRegistryStats(
  fetch: typeof globalThis.fetch,
  registry_type: RegistryType,
  searchTerm: string | undefined,
  spaces: string[] | undefined,
  tags: string[] | undefined
): Promise<RegistryStatsResponse> {
  let resp = await createInternalApiClient(fetch).post(
    ServerPaths.REGISTRY_STATS,
    {
      registry_type,
      searchTerm,
      spaces,
      tags,
    }
  );
  return (await resp.json()) as RegistryStatsResponse;
}

export async function getVersionPageWithCursor(
  fetch: typeof globalThis.fetch,
  registry_type: RegistryType,
  cursor: VersionCursor
): Promise<VersionPageResponse> {
  let resp = await createInternalApiClient(fetch).post(
    ServerPaths.VERSION_PAGE,
    {
      registry_type,
      space: cursor.space,
      name: cursor.name,
      cursor,
    }
  );

  return (await resp.json()) as VersionPageResponse;
}

/** Fetch next/previous page using cursor-based pagination */
export async function getRegistryPageWithCursor(
  fetch: typeof globalThis.fetch,
  registry_type: RegistryType,
  cursor: CardCursor
): Promise<QueryPageResponse> {
  let resp = await createInternalApiClient(fetch).post(
    ServerPaths.REGISTRY_PAGE,
    {
      registry_type,
      cursor,
    }
  );

  const data = (await resp.json()) as QueryPageResponse;
  return data;
}
