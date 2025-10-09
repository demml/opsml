import { getUISettings } from "$lib/components/settings/getSettings.server";
import type { LayoutServerLoad } from "./$types";

export const load: LayoutServerLoad = async ({ cookies }) => {
  try {
    console.log("Loading layout server data...");
    const settings = await getUISettings();

    return {
      settings: {
        scouter_enabled: settings.scouter_enabled,
        sso_enabled: settings.sso_enabled,
      },
    };
  } catch (error) {
    console.error("Layout server load error:", error);

    // Return default settings if API is unavailable
    return {
      settings: {
        scouter_enabled: false,
        sso_enabled: false,
      },
    };
  }
};
