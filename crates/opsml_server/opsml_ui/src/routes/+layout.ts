export const prerender = true;
export const ssr = false;

import { uiSettingsStore } from "$lib/components/settings/settings.svelte";

// @ts-ignore
import type { LayoutServerLoad } from "./$types";

export const load: LayoutServerLoad = async () => {
  await uiSettingsStore.getSettings();
  return {};
};
