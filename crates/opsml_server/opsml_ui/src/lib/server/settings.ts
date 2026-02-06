import { RoutePaths } from "$lib/components/api/routes";
import type { UiSettings } from "$lib/components/settings/types";
import { logger } from "$lib/server/logger";
import { createOpsmlClient } from "$lib/server/api/opsmlClient";

/**
 * Fetch UI settings from the server (this is server-side only).
 * @returns UI settings from the server
 */
export async function getUISettings(
  fetch: typeof globalThis.fetch,
): Promise<UiSettings> {
  try {
    logger.debug("Fetching UI settings...");
    const opsmlClient = createOpsmlClient(fetch);
    const response = await opsmlClient.get(RoutePaths.SETTINGS);

    if (!response.ok) {
      throw new Error(`Failed to fetch settings: ${response.status}`);
    }

    const data = (await response.json()) as UiSettings;
    logger.debug(`Settings fetched successfully: ${JSON.stringify(data)}`);
    return data;
  } catch (error) {
    logger.error(`Failed to fetch UI settings: ${error}`);

    return {
      scouter_enabled: false,
      sso_enabled: false,
    };
  }
}
