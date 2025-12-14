import { createInternalApiClient } from "$lib/api/internalClient";
import { ServerPaths } from "../api/routes";
import type {
  ScouterEntityIdResponse,
  ScouterEntityIdTagsRequest,
  Tag,
} from "./types";

export async function getScouterServerEntityIdFromTags(
  fetch: typeof globalThis.fetch,
  request: ScouterEntityIdTagsRequest
): Promise<ScouterEntityIdResponse> {
  const resp = await createInternalApiClient(fetch).post(
    ServerPaths.ENTITY_ID_TAGS,
    request
  );

  const { response, error } = await resp.json();

  if (error) {
    throw new Error(error);
  }

  return response as ScouterEntityIdResponse;
}
