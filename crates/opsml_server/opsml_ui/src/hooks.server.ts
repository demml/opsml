import { validateTokenOrRedirect } from "$lib/components/auth/validateToken";
import type { Handle } from "@sveltejs/kit";

// These routes do not require authentication
const PUBLIC_ROUTES = [
  "/opsml/user/login",
  "/api/login",
  "/opsml/user/register",
  "/opsml/user/reset",
  "/", // Add root route
  "/opsml/home", // Add home route temporarily for testing
];

export const handle: Handle = async ({ event, resolve }) => {
  console.log("Handling request for:", event.url.pathname);
  if (!PUBLIC_ROUTES.includes(event.url.pathname)) {
    try {
      await validateTokenOrRedirect(event.cookies);
    } catch (err) {
      if (err instanceof Response) return err;
      throw err;
    }
  }
  return await resolve(event);
};
