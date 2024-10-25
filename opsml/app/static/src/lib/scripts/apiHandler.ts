import { goto } from "$app/navigation";
import { CommonPaths } from "$lib/scripts/types";
import { authManager } from "./auth/authManager";
import type { Token } from "$lib/scripts/types";

const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

async function handleError(response: Response): Promise<Response> {
  const errorMessage = await response.text();
  void goto(`${CommonPaths.ERROR}?message=${errorMessage}`);
  return new Response(null, {
    status: 500,
    statusText: "Failure",
  });
}

class ApiHandler {
  constructor() {}

  async refreshToken(): Promise<boolean> {
    const response = await fetch(CommonPaths.REFRESH_TOKEN, {
      method: "GET",
    });

    if (response.ok) {
      const res = (await response.json()) as Token;
      authManager.setAccessToken(res.access_token);
      return true;
    }
    return false;
  }

  async request(
    url: string,
    method: string,
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    body: any = null,
    contentType: string = "application/json",
    additionalHeaders: Record<string, string> = {}
  ): Promise<Response> {
    let retries = 3;

    while (retries > 0) {
      const headers = {
        "Content-Type": contentType,
        Authorization: `Bearer ${authManager.getAccessToken()}`,
        ...additionalHeaders,
      };

      const response = await fetch(url, {
        method,
        headers,
        body: body ? JSON.stringify(body) : undefined,
      });

      if (response.ok) {
        return response;
      } else if (response.status === 401) {
        const refreshed = await this.refreshToken();

        if (!refreshed) {
          retries -= 1;
        } else {
          await sleep(500);
        }
      } else {
        return await handleError(response);
      }
    }

    authManager.logout();
    void goto(CommonPaths.LOGIN);
    return new Response("Unauthorized", { status: 401 });
  }

  async get(url: string): Promise<Response> {
    return this.request(url, "GET");
  }

  async put(
    url: string,
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    body: any,
    contentType: string = "application/json"
  ): Promise<Response> {
    return this.request(url, "PUT", body, contentType);
  }

  async patch(
    url: string,
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    body: any,
    contentType: string = "application/json"
  ): Promise<Response> {
    return this.request(url, "PATCH", body, contentType);
  }

  async post(
    url: string,
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    body: any,
    contentType: string = "application/json",
    additionalHeaders: Record<string, string> = {}
  ): Promise<Response> {
    return this.request(url, "POST", body, contentType, additionalHeaders);
  }
}

export const apiHandler = new ApiHandler();
