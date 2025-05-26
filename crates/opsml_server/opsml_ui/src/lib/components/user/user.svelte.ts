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
    }
  }

  public async validateSession(): Promise<boolean> {
    try {
      // Step 1: Check if user is already logged in with valid token
      if (this.logged_in && this.jwt_token) {
        const isValid = await this.validateAuth();
        if (isValid) {
          return true;
        }
      }

      // Step 2: Attempt to restore session from cookie
      const cookieToken = this.getTokenFromCookie();
      if (!cookieToken) {
        console.warn("No JWT token found in cookies");
        this.resetUser();
        return false;
      }

      // Check if cookie token is expired
      if (this.isTokenExpired(cookieToken)) {
        console.warn("Cookie token is expired, attempting refresh");
        const refreshed = await this.refreshToken(cookieToken);
        if (!refreshed) {
          this.resetUser();
          return false;
        }
      } else {
        // Valid cookie token found, set it
        this.jwt_token = cookieToken;
      }

      // Step 3: Validate authentication with current token
      return await this.validateAuth();
    } catch (error) {
      console.error("Session validation failed:", error);
      this.resetUser();
      return false;
    }
  }

  private async refreshToken(token: string): Promise<boolean> {
    try {
      const response = await opsmlClient.get(
        RoutePaths.REFRESH_TOKEN,
        undefined,
        token
      );

      if (!response.ok) return false;

      const jwtToken = (await response.json()) as JwtToken;
      this.jwt_token = jwtToken.token;
      this.setTokenCookie(jwtToken.token);
      return true;
    } catch {
      return false;
    }
  }

  // Attempts to validate the current jwt token
  // If the token is valid, updates the user information
  public async validateAuth(): Promise<boolean> {
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

      console.log("User is authenticated:", JSON.stringify(authenticated));

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

  public getTokenFromCookie(): string | null {
    if (!browser) return null;

    const cookies = document.cookie.split(";");
    const tokenCookie = cookies.find((cookie) =>
      cookie.trim().startsWith("jwt_token=")
    );

    console.log("Token cookie found:", tokenCookie);

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
    console.log("Setting JWT token cookie");
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
    const isValid = await userStore.validateSession();

    if (!isValid) {
      throw redirect(303, redirectPath);
    }
  } catch (error) {
    if (error instanceof Response) throw error; // Re-throw redirect
    console.error("Authentication error:", error);
    throw redirect(303, redirectPath);
  }
}
