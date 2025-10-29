import { createOpsmlClient, OpsmlClient } from "../api/opsmlClient";
import { RoutePaths, UiPaths } from "$lib/components/api/routes";
import { redirect, type Cookies } from "@sveltejs/kit";
import type {
  AuthenticatedResponse,
  JwtToken,
  LoginResponse,
} from "../../components/user/types";

/**
 * Validates JWT token from cookies, attempts refresh if expired,
 * and redirects to login if invalid or refresh fails.
 * Flow:
 * 1. Check for JWT token in cookies
 * 2. Validate token with server
 * 3. If expired, attempt to refresh token
 * 4. If refresh successful, set new token in cookies and re-validate
 * 5. If all fails, clear cookie and redirect to login
 *
 * @param cookies - SvelteKit cookies object
 * @param redirectPath - Path to redirect if validation fails (default: UiPaths.LOGIN)
 */
export async function validateTokenOrRedirect(
  cookies: Cookies,
  redirectPath: string = UiPaths.LOGIN
): Promise<void> {
  const jwtToken = cookies.get("jwt_token");
  const opsmlClient = createOpsmlClient(fetch);

  // Validate the JWT token
  const validationResult = await validateJWTToken(opsmlClient, jwtToken ?? "");

  if (validationResult.isValid) return; // Authenticated

  // If token is present and expired, attempt to refresh
  if (jwtToken && isTokenExpired(jwtToken)) {
    const refreshedToken = await attemptRefreshToken(opsmlClient, jwtToken);
    if (refreshedToken) {
      // Set new token in cookies and validate again
      await setTokenInCookies(cookies, refreshedToken);
      const refreshedValidation = await validateJWTToken(
        opsmlClient,
        refreshedToken
      );
      if (refreshedValidation.isValid) return;
    }
  }
  // If all else fails, clear cookie and redirect
  cookies.delete("jwt_token", { path: "/" });
  throw redirect(303, redirectPath);
}

/**
 * Attempts to refresh the JWT token via backend.
 */
async function attemptRefreshToken(
  opsmlClient: OpsmlClient,
  jwt_Token: string
): Promise<string | null> {
  try {
    const response = await opsmlClient.refreshToken(
      RoutePaths.REFRESH_TOKEN,
      jwt_Token
    );
    if (!response.ok) return null;
    const jwtToken = (await response.json()) as JwtToken;
    return jwtToken.token ?? null;
  } catch {
    return null;
  }
}

interface AuthValidationResult {
  isValid: boolean;
  shouldRedirect: boolean;
  error?: string;
}

/**
 * Validates JWT token against the server
 * @param jwtToken - The JWT token to validate
 * @returns Promise with validation result
 */
async function validateJWTToken(
  opsmlClient: OpsmlClient,
  jwt_token: string
): Promise<AuthValidationResult> {
  try {
    const response = await opsmlClient.validateToken(
      RoutePaths.VALIDATE_AUTH,
      jwt_token
    );

    if (!response.ok) {
      const error = `Authentication failed: ${response.status} ${response.statusText}`;
      console.error(error);
      return {
        isValid: false,
        shouldRedirect: response.status === 401 || response.status === 403,
        error,
      };
    }

    const authenticated = (await response.json()) as AuthenticatedResponse;

    return {
      isValid: authenticated.is_authenticated,
      shouldRedirect: !authenticated.is_authenticated,
      error: authenticated.is_authenticated
        ? undefined
        : "User not authenticated",
    };
  } catch (error) {
    const errorMessage =
      error instanceof Error ? error.message : "Unknown validation error";
    console.error("JWT validation error:", errorMessage);

    return {
      isValid: false,
      shouldRedirect: true,
      error: errorMessage,
    };
  }
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
  password: string
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
  }
): Promise<void> {
  const expirationDate = new Date();
  expirationDate.setTime(
    expirationDate.getTime() + (options?.expiresMs ?? 60 * 60 * 1000) // default: 1 hour
  );

  cookies.set("jwt_token", token, {
    httpOnly: false,
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

interface JwtPayload {
  exp: number;
  [key: string]: unknown;
}

export function isTokenExpired(token: string): boolean {
  try {
    const payload = JSON.parse(atob(token.split(".")[1])) as JwtPayload;
    return payload.exp * 1000 < Date.now();
  } catch {
    return true;
  }
}
