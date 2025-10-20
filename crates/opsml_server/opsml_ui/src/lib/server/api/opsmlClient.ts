import { goto } from "$app/navigation";
import { browser } from "$app/environment";
import { redirect } from "@sveltejs/kit";

/**
 * OpsmlClient is a wrapper around the Fetch API to interact with the OpsML axum backend.
 * It provides methods for GET, POST, PUT, DELETE, and PATCH requests with built-in
 * error handling and token management.
 */
export class OpsmlClient {
  private fetchFn: typeof globalThis.fetch;

  constructor(fetchFn: typeof globalThis.fetch = fetch) {
    this.fetchFn = fetchFn;
  }

  private getBaseUrl(): string {
    // Use OPSML_SERVER_PORT from process.env or fallback to 8080
    const port = process.env.OPSML_SERVER_PORT ?? "8080";
    return `http://localhost:${port}`;
  }

  /**
   * Handles API errors and redirects on 401.
   * @param error - Error object or message
   * @param status - Optional HTTP status code
   */
  private handleError(error: any, status?: number) {
    console.error("API Error:", error);

    // Only use goto() on the client side
    if (browser && status === 401) {
      goto("/opsml/user/login");
    } else if (!browser && status === 401) {
      // Use redirect for server-side
      throw redirect(303, "/opsml/user/login");
    }
  }

  /**
   * Adds query parameters to a URL. This is a special param handler to ensure
   * compatibility with how the axum backend expects arrays and objects.
   * @param url - URL object
   * @param params - Query params as key-value pairs
   */
  private addQueryParams(url: URL, params?: Record<string, any>): URL {
    if (!params) return url;
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        if (
          Array.isArray(value) ||
          (typeof value === "object" && typeof value.length === "number")
        ) {
          for (let i = 0; i < value.length; i++) {
            url.searchParams.append(`${key}[${i}]`, String(value[i]));
          }
        } else if (typeof value === "object") {
          url.searchParams.append(key, JSON.stringify(value));
        } else {
          url.searchParams.append(key, String(value));
        }
      }
    });
    return url;
  }

  /**
   * Generic request handler for all HTTP methods.
   * @param path - API path (relative)
   * @param options - Fetch options
   */
  async request(path: string, options: RequestInit = {}): Promise<Response> {
    const baseUrl = this.getBaseUrl();
    const url = new URL(path, baseUrl);

    try {
      const response = await this.fetchFn(url.toString(), {
        ...options,
        headers: options.headers,
      });

      if (!response.ok) {
        this.handleError(`HTTP ${response.status}`, response.status);
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return response;
    } catch (error) {
      this.handleError(error);
      throw error;
    }
  }

  /**
   * GET request with optional query params and bearer token.
   */
  async get(path: string, params?: Record<string, any>): Promise<Response> {
    const url = this.addQueryParams(new URL(path, this.getBaseUrl()), params);
    const headers: Record<string, string> = {};
    return this.request(url.pathname + url.search, { method: "GET", headers });
  }

  async validateToken(path: string, token: string): Promise<Response> {
    const headers: Record<string, string> = {
      Authorization: `Bearer ${token}`,
    };
    return this.request(path, { method: "GET", headers });
  }

  async refreshToken(path: string, token: string): Promise<Response> {
    const headers: Record<string, string> = {
      Authorization: `Bearer ${token}`,
    };
    return this.request(path, { method: "POST", headers });
  }

  /**
   * DELETE request with optional body and bearer token.
   */
  async delete(path: string, body?: any): Promise<Response> {
    const headers: Record<string, string> = {};
    return this.request(path, {
      method: "DELETE",
      headers: { "Content-Type": "application/json", ...headers },
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  /**
   * PUT request with body and optional bearer token.
   */
  async put(path: string, body: any): Promise<Response> {
    const headers: Record<string, string> = {};
    return this.request(path, {
      method: "PUT",
      headers: { "Content-Type": "application/json", ...headers },
      body: JSON.stringify(body),
    });
  }

  /**
   * PATCH request with body and optional bearer token.
   */
  async patch(path: string, body: any): Promise<Response> {
    const headers: Record<string, string> = {};
    return this.request(path, {
      method: "PATCH",
      headers: { "Content-Type": "application/json", ...headers },
      body: JSON.stringify(body),
    });
  }

  async post(
    path: string,
    body: any,
    additionalHeaders: Record<string, string> = {}
  ): Promise<Response> {
    return this.request(path, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...additionalHeaders,
      },
      body: JSON.stringify(body),
    });
  }
}

export function createOpsmlClient(fetch: typeof globalThis.fetch) {
  const client = new OpsmlClient(fetch);
  return client;
}
