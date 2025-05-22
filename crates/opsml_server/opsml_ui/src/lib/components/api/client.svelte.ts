import { goto } from "$app/navigation";
import { RoutePaths, UiPaths } from "$lib/components/api/routes";
import { browser } from "$app/environment";
import type { LoginResponse } from "../user/types";
import { userStore, UserStore } from "../user/user.svelte";

export class OpsmlClient {
  // UserStore functionality as class properties with runes
  user = $state<UserStore>(userStore);

  constructor() {
    if (browser) {
      // start active user session
      // This will load any stored token from the cookie
      this.user = userStore;
      if (this.user.jwt_token !== "") {
        this.validateAuth();
      }
    }
  }

  // UserStore methods
  resetUser() {
    this.user.resetUser();
  }

  updateUser(
    username: string,
    jwt_token: string,
    permissions: string[],
    group_permissions: string[]
  ) {
    this.user.updateUser(username, jwt_token, permissions, group_permissions);
  }
  // Auth manager methods

  /**
   * Login to the API using username and password
   *
   * @param username
   * @param password
   * @returns
   */
  async login(username: string, password: string): Promise<LoginResponse> {
    const data = (await this.post(RoutePaths.LOGIN, {
      username,
      password,
    }).then((res) => res.json())) as LoginResponse;

    if (data.authenticated)
      this.updateUser(
        data.username,
        data.jwt_token,
        data.permissions,
        data.group_permissions
      );
    return data;
  }

  async logout(): Promise<void> {
    this.resetUser();
  }

  async validateAuth(test: boolean = false): Promise<void> {
    if (test) {
      console.log("test mode");
      await this.login("guest", "guest");
      return;
    }

    const response = await this.get(RoutePaths.VALIDATE_AUTH);
    if (!response.ok) {
      console.error("Failed to validate auth");
      void goto(RoutePaths.LOGIN);
      return;
    }

    const authenticated = await response.json();
    if (!authenticated.is_authenticated) {
      void goto(RoutePaths.LOGIN);
    }
  }

  // API handler methods
  private async handleError(response: Response): Promise<Response> {
    const errorMessage = await response.text();
    void goto(`${UiPaths.ERROR}?message=${errorMessage}`);
    return new Response(null, { status: 500, statusText: "Failure" });
  }

  private addQueryParams(url: string, params?: Record<string, string>): string {
    if (!params) return url;
    const searchParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        searchParams.append(key, value);
      }
    });
    const queryString = searchParams.toString();
    return queryString ? `${url}?${queryString}` : url;
  }

  async request(
    url: string,
    method: string,
    body: any = null,
    contentType: string = "application/json",
    additionalHeaders: Record<string, string> = {}
  ): Promise<Response> {
    const userAgent = browser ? navigator.userAgent : "opsml-ui";

    const headers = {
      "Content-Type": contentType,
      "User-Agent": userAgent,
      Authorization: `Bearer ${this.user.jwt_token}`,
      ...additionalHeaders,
    };

    if (browser) {
      const response = await fetch(url, {
        method,
        headers,
        body: body ? JSON.stringify(body) : undefined,
      });

      return response.ok ? response : await this.handleError(response);
    }

    return new Response(null, { status: 500, statusText: "Failure" });
  }

  async get(url: string, params?: Record<string, any>): Promise<Response> {
    const urlWithParams = this.addQueryParams(url, params);

    return this.request(urlWithParams, "GET");
  }

  async put(
    url: string,
    body: any,
    contentType: string = "application/json"
  ): Promise<Response> {
    return this.request(url, "PUT", body, contentType);
  }

  async patch(
    url: string,
    body: any,
    contentType: string = "application/json"
  ): Promise<Response> {
    return this.request(url, "PATCH", body, contentType);
  }

  async post(
    url: string,
    body: any,
    contentType: string = "application/json",
    additionalHeaders: Record<string, string> = {}
  ): Promise<Response> {
    return this.request(url, "POST", body, contentType, additionalHeaders);
  }
}

// Create and export a singleton instance
export const opsmlClient = new OpsmlClient();
