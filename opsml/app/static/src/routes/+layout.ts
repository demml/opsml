import { authStore } from "$lib/authStore";

export const prerender = true;

/** @type {import('./$types').LayoutLoad} */
export async function load({ fetch, params, url }) {
  return { authStore, previousPage: url.pathname };
}
