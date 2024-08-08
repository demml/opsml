import { authStore } from "$lib/authStore";

export const prerender = true;

///** @type {import('./$types').PageLoad} */
export async function load({ fetch, params, url }) {
  return { authStore };
}
