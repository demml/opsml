import { browser } from "$app/environment";
import { RoutePaths, UiPaths } from "../api/routes";
import { opsmlClient } from "../api/client.svelte";
import type { AuthenticatedResponse, JwtToken, LoginResponse } from "./types";
import { redirect } from "@sveltejs/kit";

export class UserStore {
  username = $state("");
  jwt_token = $state("");
  logged_in = $state(false);
  permissions = $state<string[]>([]);
  group_permissions = $state<string[]>([]);
  repositories = $state<string[]>([]);
  recovery_codes = $state<string[]>([]);
  favorite_spaces = $state<string[]>([]);

  constructor() {
    if (browser) {
      // checks if a refresh token exists in the cookie
      // If it does, will refresh the token and populate user
      this.validateAndRefreshToken();
    }
  }

  // Attempts to validate the current jwt token
  // If the token is valid, updates the user information
  public async validateAuth(test: boolean = false): Promise<boolean> {
    try {
      const response = await opsmlClient.get(
        RoutePaths.VALIDATE_AUTH,
        undefined,
        this.jwt_token
      );

      if (!response.ok) {
        console.error("Failed to validate auth. Redirecting to login.");
        return false;
      }

      const authenticated = (await response.json()) as AuthenticatedResponse;
      if (!authenticated.is_authenticated) {
        this.resetUser();
        return false;
      }

      // Update user information if authenticated
      this.updateUser(
        authenticated.user_response.username,
        this.jwt_token,
        authenticated.user_response.permissions,
        authenticated.user_response.group_permissions,
        authenticated.user_response.favorite_spaces
      );

      return true;
    } catch (error) {
      this.resetUser();
      return false;
    }
  }

  // Checks and validates any existing JWT token in the cookie
  public async validateAndRefreshToken(): Promise<boolean> {
    // check if refresh token exists
    const cookieToken = this.getTokenFromCookie();
    if (!cookieToken) {
      this.resetUser();
      return false;
    }

    // if exists, check if it is expired
    if (this.isTokenExpired(cookieToken)) {
      // If the JWT token is expired, reset the user state, attempt to refresh the token
      this.resetUser();
    }

    try {
      const response = await opsmlClient.get(
        RoutePaths.REFRESH_TOKEN,
        undefined,
        cookieToken
      );

      if (!response.ok) throw new Error("Refresh failed");

      const jwtToken = (await response.json()) as JwtToken;
      this.setTokenCookie(jwtToken.token);
      this.jwt_token = jwtToken.token;

      // Use new jwt to get user information
      this.validateAuth();

      return true;
    } catch {
      this.resetUser();
      return false;
    }
  }

  public getTokenFromCookie(): string | null {
    if (!browser) return null;

    const cookies = document.cookie.split(";");
    const tokenCookie = cookies.find((cookie) =>
      cookie.trim().startsWith("jwt_token=")
    );

    if (tokenCookie) {
      return tokenCookie.split("=")[1].trim();
    }

    return null;
  }

  private removeTokenCookies() {
    // Remove JWT token
    document.cookie =
      "jwt_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/; SameSite=Strict; Secure";
  }

  public resetUser() {
    this.username = "";
    this.jwt_token = "";
    this.logged_in = false;
    this.repositories = [];
    this.recovery_codes = [];
    this.permissions = [];
    this.group_permissions = [];
    this.favorite_spaces = [];

    if (browser) {
      this.removeTokenCookies();
    }
  }

  private setTokenCookie(token: string) {
    const expirationDate = new Date();
    expirationDate.setTime(expirationDate.getTime() + 1 * 60 * 60 * 1000); // 1 hour
    document.cookie = `jwt_token=${token}; expires=${expirationDate.toUTCString()}; domain=${
      window.location.hostname
    }; path=/; SameSite=Strict; Secure`;
  }

  public updateUser(
    username: string,
    jwt_token: string,
    permissions: string[],
    group_permissions: string[],
    favorite_spaces: string[] = []
  ) {
    this.username = username;
    this.jwt_token = jwt_token;
    this.logged_in = true;
    this.permissions = permissions;
    this.group_permissions = group_permissions;
    this.favorite_spaces = favorite_spaces;

    if (browser) {
      this.setTokenCookie(jwt_token);
    }
  }

  private isTokenExpired(token: string): boolean {
    try {
      const payload = JSON.parse(atob(token.split(".")[1]));
      return payload.exp * 1000 < Date.now();
    } catch {
      return true;
    }
  }

  public setRepositories(repositories: string[]) {
    this.repositories = repositories;
  }

  public setRecoveryCodes(codes: string[]) {
    this.recovery_codes = codes;
  }

  public setUsername(username: string) {
    this.username = username;
  }

  // all perms are stored as <operation>:<resource>
  // split permissions by : and get resource
  // if index at 1 is empty set it to "all"
  public getPermissions(): string[][] {
    return this.permissions.map((perm) => {
      const parts = perm.split(":");
      if (parts[1] === "") parts[1] = "all";
      return parts;
    });
  }

  // same as permissions
  public getGroupPermissions(): string[][] {
    return this.group_permissions.map((perm) => {
      const parts = perm.split(":");
      if (parts[1] === "") parts[1] = "all";
      return parts;
    });
  }

  public async login(
    username: string,
    password: string
  ): Promise<LoginResponse> {
    const response = await opsmlClient.post(
      RoutePaths.LOGIN,
      {
        username,
        password,
      },
      userStore.jwt_token
    );

    const data = (await response.json()) as LoginResponse;

    if (data.authenticated) {
      this.updateUser(
        data.username,
        data.jwt_token,
        data.permissions,
        data.group_permissions,
        data.favorite_spaces
      );

      return data;
    }

    return data;
  }
}

export const userStore = new UserStore();

export async function validateUserOrRedirect(): Promise<void> {
  const redirectPath = UiPaths.LOGIN;

  try {
    console.log("Validating user authentication...");
    const isAuthenticated = await userStore.validateAuth();

    console.log("User authentication status:", isAuthenticated);

    if (!isAuthenticated) {
      // Clear any stale user data
      throw redirect(303, redirectPath);
    }
  } catch (error) {
    if (error instanceof Response) throw error; // Re-throw redirect

    console.error("Authentication error:", error);
    throw redirect(303, redirectPath);
  }
}
