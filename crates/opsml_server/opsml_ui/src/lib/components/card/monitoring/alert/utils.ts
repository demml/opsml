import { createInternalApiClient } from "$lib/api/internalClient";
import { ServerPaths } from "$lib/components/api/routes";

export async function acknowledgeMonitoringAlert(
  fetch: typeof globalThis.fetch,
  id: number,
  space: string
): Promise<boolean> {
  let response = await createInternalApiClient(fetch).put(
    ServerPaths.ACKNOWLEDGE_ALERT,
    {
      id: id,
      active: false,
      space: space,
    }
  );

  let booleanResponse = (await response.json()) as boolean;
  return booleanResponse;
}
