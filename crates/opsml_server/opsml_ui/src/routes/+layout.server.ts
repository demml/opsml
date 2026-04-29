import { getUISettings } from "$lib/server/settings";
import { logger } from "$lib/server/logger";
import { isDevMockEnabled } from "$lib/server/mock/mode";
import type { LayoutServerLoad } from "./$types";

export const load: LayoutServerLoad = async ({ fetch, cookies }) => {
  const username = cookies.get("username") ?? "";
  const devMockEnabled = isDevMockEnabled(cookies);
  try {
    logger.debug("Loading layout server data...");
    const settings = await getUISettings(fetch);
    return { settings, username, devMockEnabled };
  } catch (error) {
    logger.error(`Layout server load error: ${error}`);
    return {
      settings: { scouter_enabled: false, sso_enabled: false },
      username,
      devMockEnabled,
    };
  }
};
