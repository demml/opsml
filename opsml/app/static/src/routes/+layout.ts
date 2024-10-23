import { authStore } from "$lib/scripts/auth/authStore";

export const prerender = true;

/** @type {import('./$types').LayoutLoad} */
export async function load({}) {
  return { authStore };
}
