import type { RequestHandler } from "./$types";
import { resetUserPassword } from "$lib/server/user/utils";
import { json } from "@sveltejs/kit";

/**
 * Handles login requests and sets JWT cookie.
 * Only authentication and cookie logic here; UI navigation is handled client-side.
 */
export const POST: RequestHandler = async ({ request, fetch }) => {
  const { username, recovery_code, new_password } = await request.json();
  const response = await resetUserPassword(
    username,
    recovery_code,
    new_password,
    fetch
  );
  return json(response);
};
