import { opsmlClient } from "$lib/components/api/client.svelte";
import { getUISettings } from "$lib/components/settings/getSettings.server";
import { logger } from "$lib/server/logger";
import type { LayoutServerLoad } from "./$types";

export const load: LayoutServerLoad = async ({ cookies }) => {
  try {
    logger.debug("Loading layout server data...");
    opsmlClient.setToken(cookies.get("jwt_token"));
    const settings = await getUISettings();

    return {
      settings: {
        scouter_enabled: settings.scouter_enabled,
        sso_enabled: settings.sso_enabled,
      },
    };
  } catch (error) {
    logger.error(`Layout server load error: ${error}`);

    // Return default settings if API is unavailable
    return {
      settings: {
        scouter_enabled: false,
        sso_enabled: false,
      },
    };
  }
};
