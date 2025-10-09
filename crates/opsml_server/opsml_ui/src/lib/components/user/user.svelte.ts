import { browser } from "$app/environment";
import { RoutePaths, UiPaths } from "../api/routes";
import { opsmlClient } from "../api/client.svelte";
import type { AuthenticatedResponse, JwtToken, LoginResponse } from "./types";
import { redirect, type Cookies } from "@sveltejs/kit";

export class UserStore {
  username = $state("");
  jwt_token = $state("");
  logged_in = $state(false);
  sso_state = $state("");
  permissions = $state<string[]>([]);
  group_permissions = $state<string[]>([]);
  repositories = $state<string[]>([]);
  recovery_codes = $state<string[]>([]);
  favorite_spaces = $state<string[]>([]);

  constructor() {}

  public async validateSession(cookies: Cookies): Promise<boolean> {
    try {
      // Step 1: Check if user is already logged in with valid token
      if (this.logged_in && this.jwt_token) {
        const isValid = await this.validateAuth(cookies);
        if (isValid) {
          return true;
        }
      }

      // Step 2: Attempt to restore session from cookie
      const cookieToken = this.getTokenFromCookie(cookies);
      if (!cookieToken) {
        console.warn("No JWT token found in cookies");
        this.resetUser(cookies);
        return false;
      }

      // Check if cookie token is expired
      if (this.isTokenExpired(cookieToken)) {
        console.warn("Cookie token is expired, attempting refresh");

        const refreshed = await this.refreshToken(cookieToken, cookies);
        if (!refreshed) {
          this.resetUser(cookies);
          return false;
        }
      } else {
        // Valid cookie token found, set it
        this.jwt_token = cookieToken;
      }

      // Step 3: Validate authentication with current token
      return await this.validateAuth(cookies);
    } catch (error) {
      console.error("Session validation failed:", error);
      this.resetUser(cookies);
      return false;
    }
  }

  private async refreshToken(
    token: string,
    cookies: Cookies
  ): Promise<boolean> {
    try {
      const response = await opsmlClient.get(
        RoutePaths.REFRESH_TOKEN,
        undefined,
        token
      );

      if (!response.ok) return false;

      const jwtToken = (await response.json()) as JwtToken;
      this.jwt_token = jwtToken.token;
      this.setTokenCookie(jwtToken.token, cookies);
      return true;
    } catch {
      return false;
    }
  }

  // Attempts to validate the current jwt token
  // If the token is valid, updates the user information
  public async validateAuth(cookies: Cookies): Promise<boolean> {
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
        this.resetUser(cookies);
        return false;
      }
      // Update user information if authenticated
      this.updateUser(
        authenticated.user_response.username,
        this.jwt_token,
        authenticated.user_response.permissions,
        authenticated.user_response.group_permissions,
        authenticated.user_response.favorite_spaces,
        cookies
      );

      return true;
    } catch (error) {
      this.resetUser(cookies);
      return false;
    }
  }

  public getTokenFromCookie(cookies: Cookies): string | null {
    const tokenCookie = cookies.get("jwt_token");

    if (tokenCookie) {
      return tokenCookie;
    }

    return null;
  }

  private removeTokenCookies(cookies: Cookies) {
    // Remove JWT token
    cookies.delete("jwt_token", { path: "/" });
  }

  public resetUser(cookies: Cookies) {
    this.username = "";
    this.jwt_token = "";
    this.logged_in = false;
    this.repositories = [];
    this.recovery_codes = [];
    this.permissions = [];
    this.group_permissions = [];
    this.favorite_spaces = [];

    this.removeTokenCookies(cookies);
  }

  private setTokenCookie(token: string, cookies: Cookies) {
    const expirationDate = new Date();
    expirationDate.setTime(expirationDate.getTime() + 1 * 60 * 60 * 1000); // 1 hour
    cookies.set("jwt_token", token, {
      sameSite: "strict",
      secure: true,
      domain: browser ? window.location.hostname : "localhost",
      expires: expirationDate,
      path: "/",
    });
  }

  public updateUser(
    username: string,
    jwt_token: string,
    permissions: string[],
    group_permissions: string[],
    favorite_spaces: string[] = [],
    cookies: Cookies
  ) {
    this.username = username;
    this.jwt_token = jwt_token;
    this.logged_in = true;
    this.permissions = permissions;
    this.group_permissions = group_permissions;
    this.favorite_spaces = favorite_spaces;

    this.setTokenCookie(jwt_token, cookies);
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

  public setFavoriteSpaces(favorite_spaces: string[]) {
    this.favorite_spaces = favorite_spaces;
  }

  public setSsoState(state: string) {
    this.sso_state = state;
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

  public getSsoState(): string {
    return this.sso_state;
  }

  public async login(
    username: string,
    password: string,
    cookies: Cookies
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
        data.favorite_spaces,
        cookies
      );

      return data;
    }

    return data;
  }
}

export const userStore = new UserStore();

export async function validateUserOrRedirect(cookies: Cookies): Promise<void> {
  const redirectPath = UiPaths.LOGIN;

  try {
    const isValid = await userStore.validateSession(cookies);

    if (!isValid) {
      throw redirect(303, redirectPath);
    }
  } catch (error) {
    if (error instanceof Response) throw error; // Re-throw redirect
    console.error("Authentication error:", error);
    throw redirect(303, redirectPath);
  }
}
