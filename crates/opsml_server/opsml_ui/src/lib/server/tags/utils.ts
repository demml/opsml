import { createOpsmlClient } from "../api/opsmlClient";
import { RoutePaths } from "$lib/components/api/routes";
import type {
  ScouterEntityIdResponse,
  ScouterEntityIdTagsRequest,
} from "$lib/components/tags/utils";

export async function getScouterEntityIdFromTags(
  fetch: typeof globalThis.fetch,
  request: ScouterEntityIdTagsRequest
): Promise<ScouterEntityIdResponse> {
  const response = await createOpsmlClient(fetch).get(
    RoutePaths.ENTITY_ID_TAGS,
    request
  );
  return (await response.json()) as ScouterEntityIdResponse;
}
