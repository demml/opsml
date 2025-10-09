import { validateTokenOrRedirect } from "$lib/server/auth/validateToken";
import type { Handle } from "@sveltejs/kit";
import { logger } from "$lib/server/logger";

// These routes do not require authentication
const PUBLIC_ROUTES = [
  "/opsml/user/login",
  "/api/login",
  "/opsml/user/register",
  "/opsml/user/reset",
  "/",
];

export const handle: Handle = async ({ event, resolve }) => {
  logger.debug(`Handling request for: ${event.url.pathname}`);
  if (!PUBLIC_ROUTES.includes(event.url.pathname)) {
    try {
      await validateTokenOrRedirect(event.cookies);
    } catch (err) {
      if (err instanceof Response) return err;
      throw err;
    }
  }
  logger.debug(
    `Request for ${event.url.pathname} passed authentication check.`
  );
  return await resolve(event);
};
