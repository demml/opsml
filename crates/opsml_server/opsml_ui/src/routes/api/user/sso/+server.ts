import { json } from "@sveltejs/kit";
import type { RequestHandler } from "./$types";
import { getSsoAuthURL } from "$lib/server/user/util";
import { logger } from "$lib/server/logger";

/**
 * Server route to fetch SSO authentication URL and related state.
 * Client should store state/code_verifier and perform redirect.
 */
export const GET: RequestHandler = async ({ fetch, cookies }) => {
  // Optionally, extract JWT from cookies if needed for SSO
  const jwt_token = cookies.get("jwt_token");

  // Fetch SSO auth URL and related info from backend
  const ssoAuthUrl = await getSsoAuthURL(fetch, jwt_token);

  // Log the SSO URL fetch action
  logger.debug(`Fetched SSO authentication URL. ${JSON.stringify(ssoAuthUrl)}`);

  // Return SSO info to client for further handling
  return json(ssoAuthUrl);
};
