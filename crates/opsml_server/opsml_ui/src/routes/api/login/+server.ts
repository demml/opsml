import { json } from "@sveltejs/kit";
import type { RequestHandler } from "./$types";
import {
  loginUser,
  setTokenInCookies,
} from "$lib/components/auth/validateToken";
/**
 * Handles login requests and sets JWT cookie.
 * Only authentication and cookie logic here; UI navigation is handled client-side.
 */
export const POST: RequestHandler = async ({ request, cookies }) => {
  const { username, password } = await request.json();
  const loginResponse = await loginUser(username, password);

  if (loginResponse.authenticated) {
    // Return success response with JWT token
    setTokenInCookies(cookies, loginResponse.jwt_token);
    return json({ success: true, response: loginResponse });
  } else {
    return json(
      {
        success: false,
        error: loginResponse.message ?? "Invalid username or password",
      },
      { status: 401 }
    );
  }
};
