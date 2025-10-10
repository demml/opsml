import { redirect } from "@sveltejs/kit";

/**
 * HTTP client for SvelteKit server endpoints.
 * Uses relative paths and idiomatic error handling.
 */
export class ServerClient {
  private fetchFn: typeof fetch;

  constructor(fetchFn: typeof fetch = fetch) {
    this.fetchFn = fetchFn;
  }

  /**
   * Handles API errors and redirects on 401.
   * @param error - Error object or message
   * @param status - Optional HTTP status code
   */
  private handleError(error: unknown, status?: number): void {
    console.error("Server API Error:", error);
    if (status === 401) {
      throw redirect(303, "/opsml/user/login");
    }
  }

  /**
   * Adds query parameters to a URL object.
   * Supports arrays and objects for compatibility.
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
   * @param path - Relative API path
   * @param options - Fetch options
   */
  async request(path: string, options: RequestInit = {}): Promise<Response> {
    const url = new URL(path, "http://localhost"); // base is ignored for relative paths
    try {
      const response = await this.fetchFn(url.pathname + url.search, {
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
   * GET request with optional query params.
   */
  async get(path: string, params?: Record<string, any>): Promise<Response> {
    const url = this.addQueryParams(new URL(path, "http://localhost"), params);
    const headers: Record<string, string> = {};
    return this.request(url.pathname + url.search, { method: "GET", headers });
  }

  /**
   * DELETE request with optional body and bearer token.
   */
  async delete(path: string, body?: any, token?: string): Promise<Response> {
    const headers: Record<string, string> = {};
    return this.request(path, {
      method: "DELETE",
      headers: { "Content-Type": "application/json", ...headers },
      body: body ? JSON.stringify(body) : undefined,
    });
  }

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

  /**
   * POST request with body and optional bearer token.
   */
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

/** Singleton instance for usage in SvelteKit server code */
export const serverClient = new ServerClient();

export function createServerClient(fetchFn: typeof fetch) {
  return new ServerClient(fetchFn);
}
