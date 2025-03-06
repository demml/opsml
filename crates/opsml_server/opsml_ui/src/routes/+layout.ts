export const prerender = true;
export const ssr = false;

import {
  user,
  type Authenticated,
} from "$lib/components/auth/AuthStore.svelte";
import { goto } from "$app/navigation";
import { RoutePaths } from "$lib/components/api/routes";
import { apiHandler } from "$lib/components/api/apiHandler";
import type { LayoutServerLoad } from "./$types";

export const load: LayoutServerLoad = async () => {
  console.log("parent layout");
  // attempt to authenticate, if not authenticated, redirect to login
  //piHandler.get(RoutePaths.VALIDATE_AUTH).then(async (response) => {
  // if (!response.ok) {
  //   console.error("Failed to validate auth");
  //   void goto(RoutePaths.LOGIN);
  // }

  // // extract to Authenticated type
  // const authenticated = (await response.json()) as Authenticated;

  // if (!authenticated.is_authenticated) {
  //   void goto(RoutePaths.LOGIN);
  // }
  //);
  return {};
};
