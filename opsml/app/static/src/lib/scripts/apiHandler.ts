import { goto } from "$app/navigation";
import { CommonPaths } from "$lib/scripts/types";
import { authStore } from "$lib/scripts/authStore";
import type { Token } from "$lib/scripts/types";

const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

class ApiHandler {
  constructor() {}

  async refreshToken(): Promise<boolean> {
    const response = await fetch(CommonPaths.REFRESH_TOKEN, {
      method: "GET",
    });

    if (response.ok) {
      const res = (await response.json()) as Token;
      authStore.setToken(res.access_token);
      return true;
    }
    return false;
  }

  async get(url: string): Promise<Response> {
    let retries = 3;

    while (retries > 0) {
      const response = await fetch(url, {
        method: "GET",
        headers: {
          Authorization: `Bearer ${authStore.getToken()}`,
        },
      });

      if (!response.ok) {
        // Try refreshing the jwt token if the response is unauthorized
        const refreshed = await this.refreshToken();

        if (refreshed) {
          retries -= 1;
          await sleep(500);
        }
      } else {
        return response;
      }
    }
    // only get here if retries are exhausted
    authStore.clearToken();
    authStore.clearUsername();
    void goto(CommonPaths.LOGIN);
    return new Response("Unauthorized", { status: 401 });
  }

  async put(
    url: string,

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    body: any,
    contentType: string = "application/json"
  ): Promise<Response> {
    let retries = 3;

    while (retries > 0) {
      const response = await fetch(url, {
        method: "PUT",
        headers: {
          "Content-Type": contentType,
          Authorization: `Bearer ${authStore.getToken()}`,
        },
        body: JSON.stringify(body),
      });

      if (!response.ok) {
        // Try refreshing the jwt token if the response is unauthorized
        const refreshed = await this.refreshToken();

        if (refreshed) {
          retries -= 1;
          await sleep(500);
        }
      } else {
        return response;
      }
    }
    // only get here if retries are exhausted
    authStore.clearToken();
    authStore.clearUsername();
    void goto(CommonPaths.LOGIN);
    return new Response("Unauthorized", { status: 401 });
  }

  async patch(
    url: string,

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    body: any,
    contentType: string = "application/json"
  ): Promise<Response> {
    let retries = 3;

    while (retries > 0) {
      const response = await fetch(url, {
        method: "PATCH",
        headers: {
          "Content-Type": contentType,
          Authorization: `Bearer ${authStore.getToken()}`,
        },
        body: JSON.stringify(body),
      });
      if (!response.ok) {
        // Try refreshing the jwt token if the response is unauthorized
        const refreshed = await this.refreshToken();

        if (refreshed) {
          retries -= 1;
          await sleep(500);
        }
      } else {
        return response;
      }
    }
    // only get here if retries are exhausted
    authStore.clearToken();
    authStore.clearUsername();
    void goto(CommonPaths.LOGIN);

    return new Response("Unauthorized", { status: 401 });
  }

  async post(
    url: string,

    //eslint-disable-next-line @typescript-eslint/no-explicit-any
    body: any,
    contentType: string = "application/json",
    additionalHeaders: Record<string, string> = {}
  ): Promise<Response> {
    let retries = 3;

    while (retries > 0) {
      const headers = {
        "Content-Type": contentType,
        Authorization: `Bearer ${authStore.getToken()}`,
        ...additionalHeaders,
      };

      const response = await fetch(url, {
        method: "POST",
        headers,
        body: JSON.stringify(body),
      });
      if (!response.ok) {
        // Try refreshing the jwt token if the response is unauthorized
        const refreshed = await this.refreshToken();

        if (refreshed) {
          retries -= 1;
          await sleep(500);
        }
      } else {
        return response;
      }
    }
    // only get here if retries are exhausted
    authStore.clearToken();
    authStore.clearUsername();
    void goto(CommonPaths.LOGIN);

    return new Response("Unauthorized", { status: 401 });
  }
}

export const apiHandler = new ApiHandler();