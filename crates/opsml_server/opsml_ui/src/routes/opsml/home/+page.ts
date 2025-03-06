import { authManager } from "$lib/components/auth/AuthStore.svelte";

/** @type {import('./$types').PageLoad} */
export async function load() {
  await authManager.validateAuth();
}
