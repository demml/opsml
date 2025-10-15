import { createInternalApiClient } from "$lib/api/internalClient";
import type { DataCard } from "../card_interfaces/datacard";
import { ServerPaths } from "$lib/components/api/routes";

export async function getDataProfile(
  fetch: typeof window.fetch,
  card: DataCard
) {
  const client = createInternalApiClient(fetch);
  const response = await client.post(ServerPaths.DATA_PROFILE, { card });
  return response.json();
}
