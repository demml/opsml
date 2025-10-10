import type { RequestHandler } from "./$types";
import { setTokenInCookies } from "$lib/server/auth/validateToken";
import type { LogOutResponse } from "$lib/components/user/types";
import { RoutePaths } from "$lib/components/api/routes";
import { json } from "@sveltejs/kit";
import { createOpsmlClient } from "$lib/server/api/opsmlClient";

/**
 * Helper function for logging out a user via the api client
 * @param jwt_token - JWT token of the user to log out
 * @returns
 */
async function logout(
  fetch: typeof globalThis.fetch,
  jwt_token?: string
): Promise<LogOutResponse> {
  let opsmlClient = createOpsmlClient(fetch, jwt_token);
  let path = `${RoutePaths.LOGOUT}`;
  const response = await opsmlClient.get(path, undefined);
  return (await response.json()) as LogOutResponse;
}

/**
 * Handles login requests and sets JWT cookie.
 * Only authentication and cookie logic here; UI navigation is handled client-side.
 */
export const GET: RequestHandler = async ({ cookies, fetch }) => {
  let loggedOut = await logout(fetch, cookies.get("jwt_token"));

  if (loggedOut) {
    // update the user store
    setTokenInCookies(cookies, ""); // clear the cookie
  }

  return json(loggedOut);
};
