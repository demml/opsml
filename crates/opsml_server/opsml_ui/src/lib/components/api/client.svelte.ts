import { goto } from "$app/navigation";
import { UiPaths } from "$lib/components/api/routes";
import { browser } from "$app/environment";
import Console from "../card/monitoring/update/dispatch/Console.svelte";

export class OpsmlClient {
  // UserStore functionality as class properties with runes
  // user = $state<UserStore>(userStore);

  constructor() {
    if (browser) {
      // start active user session
      // This will load any stored token from the cookie
      //this.user = userStore;
      //if (this.user.jwt_token !== "") {
      //  this.validateAuth();
      //}
    }
  }

  //// API handler methods
  private async handleError(response: Response): Promise<Response> {
    const errorMessage = await response.text();
    void goto(`${UiPaths.ERROR}?message=${errorMessage}`);
    return new Response(null, { status: 500, statusText: "Failure" });
  }

  private addQueryParams(url: string, params?: Record<string, any>): string {
    if (!params) return url;
    const searchParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        if (
          Array.isArray(value) ||
          (typeof value === "object" && typeof value.length === "number")
        ) {
          for (let i = 0; i < value.length; i++) {
            searchParams.append(`${key}[${i}]`, String(value[i]));
          }
        } else if (typeof value === "object") {
          searchParams.append(key, JSON.stringify(value));
        } else {
          searchParams.append(key, String(value));
        }
      }
    });
    const queryString = searchParams.toString();
    return queryString ? `${url}?${queryString}` : url;
  }

  async request(
    url: string,
    method: string,
    body: any = null,
    bearerToken: string,
    contentType: string = "application/json",
    additionalHeaders: Record<string, string> = {}
  ): Promise<Response> {
    const userAgent = browser ? navigator.userAgent : "opsml-ui";

    const headers = {
      "Content-Type": contentType,
      "User-Agent": userAgent,
      Authorization: `Bearer ${bearerToken}`,
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

  async get(
    url: string,
    params?: Record<string, any>,
    bearerToken: string = ""
  ): Promise<Response> {
    const urlWithParams = this.addQueryParams(url, params);

    return this.request(urlWithParams, "GET", null, bearerToken);
  }

  async delete(
    url: string,
    body: any = null,
    bearerToken: string = "",
    contentType: string = "application/json"
  ): Promise<Response> {
    return this.request(url, "DELETE", body, bearerToken, contentType);
  }

  async put(
    url: string,
    body: any,
    bearerToken: string = "",
    contentType: string = "application/json"
  ): Promise<Response> {
    return this.request(url, "PUT", body, bearerToken, contentType);
  }

  async patch(
    url: string,
    body: any,
    bearerToken: string = "",
    contentType: string = "application/json"
  ): Promise<Response> {
    return this.request(url, "PATCH", body, bearerToken, contentType);
  }

  async post(
    url: string,
    body: any,
    bearerToken: string = "",
    contentType: string = "application/json",
    additionalHeaders: Record<string, string> = {}
  ): Promise<Response> {
    return this.request(
      url,
      "POST",
      body,
      bearerToken,
      contentType,
      additionalHeaders
    );
  }
}

// Create and export a singleton instance
export const opsmlClient = new OpsmlClient();
