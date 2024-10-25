import { checkAuthstore } from "$lib/scripts/auth/authManager";

/** @type {import('./$types').PageLoad} */
export async function load({}) {
  checkAuthstore();
}
