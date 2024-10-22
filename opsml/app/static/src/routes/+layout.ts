import { authStore } from "$lib/scripts/auth/newAuthStore";
import { get } from "svelte/store";
import { setupAuth } from "$lib/scripts/auth/setupAuth.js";
export const prerender = true;

/** @type {import('./$types').LayoutLoad} */
export async function load({ url }) {
  console.log("layout load");

  await setupAuth();
  const auth = get(authStore);
  return {
    auth,
    previousPath: (url as URL).pathname,
  };
}
