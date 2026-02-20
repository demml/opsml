import { validateTokenOrRedirect } from "$lib/server/auth/validateToken";
import type { Handle } from "@sveltejs/kit";
import { logger } from "$lib/server/logger";
import { ServerPaths, UiPaths } from "$lib/components/api/routes";
import type { HandleFetch } from "@sveltejs/kit";

// These routes do not require authentication
const PUBLIC_ROUTES = [
  UiPaths.LOGIN,
  UiPaths.REGISTER,
  UiPaths.RESET,
  UiPaths.FORGOT,
  UiPaths.SSO_AUTH,
  UiPaths.SSO_CALLBACK,
  ServerPaths.LOGIN,
  ServerPaths.REGISTER_USER,
  ServerPaths.RESET_PASSWORD,
  ServerPaths.SSO_AUTH,
  ServerPaths.SSO_CALLBACK,
  ServerPaths.USER,
  ServerPaths.HEALTHCHECK,
  "/",
];

// The handle function runs on every request to the server. We use it to check for a valid JWT token in cookies and redirect to login if not authenticated.
export const handle: Handle = async ({ event, resolve }) => {
  logger.debug(`Handling request for: ${event.url.pathname}`);

  if (!PUBLIC_ROUTES.includes(event.url.pathname)) {
    try {
      await validateTokenOrRedirect(event.cookies);
      logger.debug(`User authenticated successfully.`);
    } catch (err) {
      if (err instanceof Response) return err;
      throw err;
    }
  }
  logger.debug(
    `Request for ${event.url.pathname} passed authentication check.`,
  );

  return await resolve(event);
};

// For outgoing requests from the server (e.g. API calls), we need to add the JWT token to the Authorization header
export const handleFetch: HandleFetch = async ({ request, event, fetch }) => {
  const token = event.cookies.get("jwt_token");

  if (token) {
    // add the auth token to all outgoing requests:
    // - Requests are either being routed to the server endpoints or backend api
    request.headers.set("Authorization", `Bearer ${token}`);
  }

  let response: Response;
  try {
    response = await fetch(request);
  } catch (error) {
    logger.error(`API Error: ${error}`);
    // Return a 503 so load functions receive a Response object rather than
    // an unhandled throw, keeping non-backend-dependent routes functional.
    return new Response(JSON.stringify({ error: "Backend unavailable" }), {
      status: 503,
      headers: { "Content-Type": "application/json" },
    });
  }

  // If backend middleware refreshed the token, it will be in the Authorization header
  const newToken = response.headers.get("Authorization");
  if (newToken?.startsWith("Bearer ")) {
    const refreshedToken = newToken.replace("Bearer ", "");
    // Update the cookie with the new token
    event.cookies.set("jwt_token", refreshedToken, {
      httpOnly: true,
      secure:
        process.env.APP_ENV === "production" ||
        process.env.FORCE_HTTPS === "true",
      sameSite: "lax",
      path: "/",
      maxAge: 7 * 24 * 60 * 60,
    });
    logger.debug("Token refreshed automatically by backend middleware");
  }

  return response;
};
