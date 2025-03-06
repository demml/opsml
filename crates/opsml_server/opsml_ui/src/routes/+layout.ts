export const prerender = true;
export const ssr = false;
import { authManager } from "$lib/components/auth/AuthStore.svelte";
import type { LayoutServerLoad } from "./$types";

export const load: LayoutServerLoad = async () => {
  console.log("parent layout");
  await authManager.validateAuth();
  return {};
};
