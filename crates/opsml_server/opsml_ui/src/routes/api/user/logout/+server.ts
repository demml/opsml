import type { RequestHandler } from "./$types";
import type { LogOutResponse } from "$lib/components/user/types";
import { RoutePaths } from "$lib/components/api/routes";
import { json } from "@sveltejs/kit";
import { createOpsmlClient } from "$lib/server/api/opsmlClient";

/**
 * Helper function for logging out a user via the api client
 * @returns
 */
async function logout(
  fetch: typeof globalThis.fetch
): Promise<LogOutResponse> {
  let opsmlClient = createOpsmlClient(fetch);
  let path = `${RoutePaths.LOGOUT}`;
  const response = await opsmlClient.get(path, undefined);
  return (await response.json()) as LogOutResponse;
}

/**
 * Handles logout requests and clears JWT cookie.
 * Always clears cookies and returns success — backend failure (e.g. expired token) is not an error.
 */
export const GET: RequestHandler = async ({ cookies, fetch }) => {
  try {
    await logout(fetch);
  } catch {
    // Backend call failed (token already expired or invalid) — proceed with local cleanup
  }

  cookies.delete("jwt_token", { path: "/" });
  cookies.delete("username", { path: "/" });

  return json({ logged_out: true } satisfies LogOutResponse);
};
