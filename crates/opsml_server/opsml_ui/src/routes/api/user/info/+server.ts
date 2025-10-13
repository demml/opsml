import type { RequestHandler } from "./$types";
import { json } from "@sveltejs/kit";
import { getUser } from "$lib/server/user/util";
import { logger } from "$lib/server/logger";

/**
 * Top-level GET to get user info if jwt and username cookies are set.
 * Only calls getUser if both are present; otherwise returns success: false.
 */
export const GET: RequestHandler = async ({ cookies, fetch }) => {
  const jwt_token = cookies.get("jwt_token");
  const username = cookies.get("username");
  let response = { success: false, user: null };

  if (jwt_token && username) {
    try {
      const user = await getUser(username, fetch);
      return json({ success: true, user });
    } catch (error) {
      logger.error(`Error fetching user info: ${error}`);
      return json(
        { success: false, user: null, error: "User not found" },
        { status: 404 }
      );
    }
  }

  return json(response);
};
