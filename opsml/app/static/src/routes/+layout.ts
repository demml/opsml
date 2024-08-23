import { authStore } from "$lib/scripts/auth/authStore";

export const prerender = true;

/** @type {import('./$types').LayoutLoad} */
export function load({ fetch, params, url }) {
  return { authStore, previousPath: (url as URL).pathname };
}
