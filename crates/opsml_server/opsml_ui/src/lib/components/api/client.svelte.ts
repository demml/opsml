import { goto } from "$app/navigation";
import { RoutePaths } from "$lib/components/api/routes";
import { browser } from "$app/environment";
import type { LoginResponse } from "../user/types";

export class OpsmlClient {
  // UserStore functionality as class properties with runes
  username = $state("");
  jwt_token = $state("");
  logged_in = $state(false);

  constructor() {
    if (browser) {
      const storedToken = this.getTokenFromCookie();
      if (storedToken) {
        this.jwt_token = storedToken;
        this.logged_in = true;
        // Optionally validate the token here
        this.validateAuth();
      }
    }
  }

  private setTokenCookie(token: string) {
    // Set cookie to expire in 24 hours (or match your token expiration)
    const expirationDate = new Date();
    expirationDate.setTime(expirationDate.getTime() + 1 * 60 * 60 * 1000);

    document.cookie = `jwt_token=${token}; expires=${expirationDate.toUTCString()}; path=/; SameSite=Strict`;
  }

  private getTokenFromCookie(): string | null {
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

  private removeTokenCookie() {
    document.cookie =
      "jwt_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
  }

  // UserStore methods
  resetUser() {
    this.username = "";
    this.jwt_token = "";
    this.logged_in = false;

    if (browser) {
      this.removeTokenCookie();
    }
  }

  updateUser(username: string, jwt_token: string) {
    this.username = username;
    this.jwt_token = jwt_token;
    this.logged_in = true;

    if (browser) {
      this.setTokenCookie(jwt_token);
    }
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

    if (data.authenticated) this.updateUser(data.username, data.jwt_token);
    return data;
  }

  async logout(): Promise<void> {
    this.resetUser();
  }

  async validateAuth(test: boolean = false): Promise<void> {
    if (test) {
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
    void goto(`${RoutePaths.ERROR}?message=${errorMessage}`);
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
      Authorization: `Bearer ${this.jwt_token}`,
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
