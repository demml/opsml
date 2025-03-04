export const prerender = true;
import {
  user,
  type Authenticated,
} from "$lib/components/auth/AuthStore.svelte";
import { goto } from "$app/navigation";
import { RoutePaths } from "$lib/components/api/routes";
import { apiHandler } from "$lib/components/api/apiHandler";

/** @type {import('./$types').LayoutLoad} */
export async function load() {
  // attempt to authenticate, if not authenticated, redirect to login
  apiHandler.get(RoutePaths.VALIDATE_AUTH).then(async (response) => {
    // extract to Authenticated type
    const authenticated = (await response.json()) as Authenticated;

    if (!authenticated.is_authenticated) {
      void goto(RoutePaths.LOGIN);
      if (!response.ok) {
        void goto(RoutePaths.LOGIN);
      }
    }
  });
  return {};
}
