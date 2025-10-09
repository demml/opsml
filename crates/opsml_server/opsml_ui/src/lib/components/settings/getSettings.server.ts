import { RoutePaths } from "../api/routes";
import { opsmlClient } from "../api/client.svelte";
import type { UiSettings } from "./types";
import { logger } from "$lib/server/logger";

/**
 * Fetch UI settings from the server (this is server-side only).
 * @returns UI settings from the server
 */
export async function getUISettings(): Promise<UiSettings> {
  try {
    logger.debug("Fetching UI settings...");
    const response = await opsmlClient.get(RoutePaths.SETTINGS);

    if (!response.ok) {
      throw new Error(`Failed to fetch settings: ${response.status}`);
    }

    const data = (await response.json()) as UiSettings;
    logger.debug(`Settings fetched successfully: ${JSON.stringify(data)}`);
    return data;
  } catch (error) {
    logger.error(`Failed to fetch UI settings: ${error}`);
    // Return default settings on error
    return {
      scouter_enabled: false,
      sso_enabled: false,
    };
  }
}
