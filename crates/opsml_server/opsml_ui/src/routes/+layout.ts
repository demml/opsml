export const prerender = true;
export const ssr = false;
import { opsmlClient } from "$lib/components/api/client.svelte";

// @ts-ignore
import type { LayoutServerLoad } from "./$types";

export const load: LayoutServerLoad = async () => {
  console.log("parent layout");
  await opsmlClient.validateAuth(true);
  return {};
};
