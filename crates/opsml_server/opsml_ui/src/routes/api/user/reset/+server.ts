import type { RequestHandler } from "./$types";
import { setTokenInCookies } from "$lib/server/auth/validateToken";
import type { LogOutResponse } from "$lib/components/user/types";
import { resetUserPassword } from "$lib/server/user/util";
import { RoutePaths } from "$lib/components/api/routes";
import { opsmlClient } from "$lib/components/api/client.svelte";
import { json } from "@sveltejs/kit";

/**
 * Handles login requests and sets JWT cookie.
 * Only authentication and cookie logic here; UI navigation is handled client-side.
 */
export const GET: RequestHandler = async ({ cookies }) => {
  let loggedOut = await logout(cookies.get("jwt_token"));

  if (loggedOut) {
    // update the user store
    setTokenInCookies(cookies, ""); // clear the cookie
  }

  return json(loggedOut);
};
