import { json } from "@sveltejs/kit";
import type { RequestHandler } from "./$types";
import { getSsoAuthURL } from "$lib/server/user/utils";
import { logger } from "$lib/server/logger";

/**
 * Server route to fetch SSO authentication URL and related state.
 * Client should store state/code_verifier and perform redirect.
 */
export const GET: RequestHandler = async ({ fetch, url }) => {
  // Fetch SSO auth URL and related info from backend
  const ssoAuthUrl = await getSsoAuthURL(fetch);

  // Log the SSO URL fetch action
  logger.debug(`Fetched SSO authentication URL. ${JSON.stringify(ssoAuthUrl)}`);

  // Return SSO info to client for further handling
  return json(ssoAuthUrl);
};
