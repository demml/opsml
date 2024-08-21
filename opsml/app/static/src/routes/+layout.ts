import { authStore } from "$lib/scripts/authStore";

export const prerender = true;

/** @type {import('./$types').LayoutLoad} */
export async function load({ fetch, params, url }) {
  return { authStore, previousPath: url.pathname };
}
