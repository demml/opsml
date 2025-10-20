import type { RequestHandler } from "./$types";
import { registerUser } from "$lib/server/user/utils";
import { json } from "@sveltejs/kit";
import { logger } from "$lib/server/logger";

/**
 * Handles login requests and sets JWT cookie.
 * Only authentication and cookie logic here; UI navigation is handled client-side.
 */
export const POST: RequestHandler = async ({ request, cookies, fetch }) => {
  const { username, password, email } = await request.json();
  const response = await registerUser(username, password, email, fetch);
  return json(response);
};
