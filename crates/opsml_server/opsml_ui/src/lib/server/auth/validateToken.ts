import { createOpsmlClient } from "../api/opsmlClient";
import { RoutePaths, UiPaths } from "$lib/components/api/routes";
import { redirect, type Cookies } from "@sveltejs/kit";
import type { LoginResponse } from "../../components/user/types";

/**
 * Validates JWT token from cookies and redirects to login if invalid.
 * 
 * This function performs a basic check for token presence. Token refresh
 * is handled automatically by the backend middleware when actual API requests
 * are made. The /validate endpoint doesn't trigger refresh logic, so we
 * only redirect if there's no token at all.
 *
 * Token refresh flow (happens in handleFetch + backend middleware):
 * 1. Request made to protected endpoint with expired access token
 * 2. Backend middleware checks for valid refresh token in database
 * 3. Generates new access + refresh tokens
 * 4. Returns new access token in Authorization header
 * 5. handleFetch updates jwt_token cookie
 *
 * @param cookies - SvelteKit cookies object
 * @param redirectPath - Path to redirect if validation fails (default: UiPaths.LOGIN)
 */
export async function validateTokenOrRedirect(
  cookies: Cookies,
  redirectPath: string = UiPaths.LOGIN,
): Promise<void> {
  const jwtToken = cookies.get("jwt_token");

  // If no token at all, redirect to login
  if (!jwtToken) {
    cookies.delete("username", { path: "/" });
    throw redirect(303, redirectPath);
  }

  // Token exists - let it be used for requests
  // If it's expired, backend middleware will refresh it on first protected API call
  // handleFetch will capture the new token and update the cookie
}

/**
 * Logs in a user on the server and returns the login response
 * @param username - The username
 * @param password - The password
 * @returns Promise with login response
 */
export async function loginUser(
  fetch: typeof globalThis.fetch,
  username: string,
  password: string,
): Promise<LoginResponse> {
  const opsmlClient = createOpsmlClient(fetch);
  const response = await opsmlClient.post(RoutePaths.LOGIN, {
    username,
    password,
  });

  const data = (await response.json()) as LoginResponse;
  return data;
}

/**
 * Sets the JWT token in an HttpOnly cookie with domain, expiration, and path.
 * This should be used server-side for secure authentication.
 *
 * @param cookies - SvelteKit cookies object
 * @param token - JWT token string
 * @param options - Optional overrides for domain, expiration (ms), and path
 */
export async function setTokenInCookies(
  cookies: Cookies,
  token: string,
  options?: {
    domain?: string;
    expiresMs?: number;
    path?: string;
  },
): Promise<void> {
  const expirationDate = new Date();
  expirationDate.setTime(
    expirationDate.getTime() + (options?.expiresMs ?? 60 * 60 * 1000), // default: 1 hour
  );

  cookies.set("jwt_token", token, {
    httpOnly: true,
    secure:
      process.env.APP_ENV === "production" ||
      process.env.FORCE_HTTPS === "true",
    sameSite: "lax",
    path: options?.path ?? "/",
    maxAge: 7 * 24 * 60 * 60,
  });
}

export function setUsernameInCookies(cookies: Cookies, username: string): void {
  cookies.set("username", username, {
    httpOnly: false, // Client needs to read this for UI state
    secure:
      process.env.APP_ENV === "production" ||
      process.env.FORCE_HTTPS === "true",
    sameSite: "lax",
    path: "/",
    maxAge: 7 * 24 * 60 * 60, // 7 days in seconds
  });
}
