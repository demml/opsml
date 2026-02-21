import { getUISettings } from "$lib/server/settings";
import { logger } from "$lib/server/logger";
import type { LayoutServerLoad } from "./$types";

export const load: LayoutServerLoad = async ({ fetch }) => {
  try {
    logger.debug("Loading layout server data...");
    const settings = await getUISettings(fetch);
    return { settings };
  } catch (error) {
    logger.error(`Layout server load error: ${error}`);
    return { settings: { scouter_enabled: false, sso_enabled: false } };
  }
};
