import { initializeStores } from "@skeletonlabs/skeleton";
import { authStore } from "$lib/authStore";
import { goto } from "$app/navigation";

export const prerender = true;

///** @type {import('./$types').PageLoad} */
//export async function load({ fetch, params, url }) {
//  // get user and password
//  let token: string | null = authStore.GetToken();
//
//  // if token is null, redirect to login at (opsml/auth/login)
//  if (token === null) {
//    console.log("No token found, redirecting to login");
//    goto("opsml/auth/login?url=" + url.pathname);
//  }
//}
//
