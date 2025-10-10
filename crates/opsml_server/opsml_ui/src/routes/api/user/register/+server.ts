import type { RequestHandler } from "./$types";
import { registerUser } from "$lib/server/user/util";
import { json } from "@sveltejs/kit";
import { logger } from "$lib/server/logger";

/**
 * Handles login requests and sets JWT cookie.
 * Only authentication and cookie logic here; UI navigation is handled client-side.
 */
export const POST: RequestHandler = async ({ request, cookies }) => {
  logger.debug(`Handling user registration request...`);
  const { username, password, email } = await request.json();
  const jwt_token = cookies.get("jwt_token");
  const response = await registerUser(username, password, email, jwt_token);
  logger.debug(`User registration response: ${JSON.stringify(response)}`);
  return json(response);
};
