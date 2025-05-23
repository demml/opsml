export const prerender = true;
export const ssr = false;

import { opsmlClient } from "$lib/components/api/client.svelte";

// @ts-ignore
import type { LayoutServerLoad } from "./$types";

export const load: LayoutServerLoad = async () => {
  //await opsmlClient.validateAuth();
  return {};
};
