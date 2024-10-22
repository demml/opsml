import { goto } from "$app/navigation";
import { CommonPaths } from "$lib/scripts/types";
import type { Token } from "$lib/scripts/types";
import { authStore, clearToken } from "$lib/scripts/auth/newAuthStore";
import { get } from "svelte/store";

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

  async refreshkOktaAuth(): Promise<boolean> {
    // try refreshing the okta token if the token has expired
    const auth = get(authStore);

    // if okta, check if the session exists
    if (auth.authType === "okta") {
      const sessionExists = await auth.oktaAuth!.session.exists();

      // if the session exists, refresh the token
      if (sessionExists) {
        // refresh the token
        let tokens = await auth.oktaAuth!.token.renewTokens();
        auth.oktaAuth!.tokenManager.setTokens(tokens);
        authStore.update((state) => ({
          ...state,
          token: tokens,
        }));

        return true;
      } else {
        // if the session does not exist, redirect to login
        // add redirect param
        void goto(CommonPaths.LOGIN + "?redirect=" + window.location.pathname);
        return false;
      }
    }
    return false;
  }

  async refreshToken(): Promise<boolean> {
    const auth = get(authStore);
    if (auth.authType === "basic") {
      const response = await fetch(CommonPaths.REFRESH_TOKEN, {
        method: "GET",
      });

      if (response.ok) {
        const res = (await response.json()) as Token;
        authStore.update((state) => ({ ...state, token: res.access_token }));
        return true;
      }
    }
    return false;
  }

  async get(url: string): Promise<Response> {
    let retries = 3;
    const auth = get(authStore);

    await this.refreshkOktaAuth();

    while (retries > 0) {
      const response = await fetch(url, {
        method: "GET",
        headers: {
          Authorization: `Bearer ${auth.token}`,
        },
      });

      if (!response.ok) {
        // Try refreshing the jwt token if the response is unauthorized
        if (response.status === 401) {
          const refreshed = await this.refreshToken();

          if (refreshed) {
            retries -= 1;
            await sleep(500);
          }
        } else {
          return await handleError(response);
        }
      } else {
        return response;
      }
    }
    // only get here if retries are exhausted
    clearToken();
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
    const auth = get(authStore);

    await this.refreshkOktaAuth();
    while (retries > 0) {
      const response = await fetch(url, {
        method: "PUT",
        headers: {
          "Content-Type": contentType,
          Authorization: `Bearer ${auth.token}`,
        },
        body: JSON.stringify(body),
      });

      if (!response.ok) {
        // Try refreshing the jwt token if the response is unauthorized
        if (response.status === 401) {
          const refreshed = await this.refreshToken();

          if (refreshed) {
            retries -= 1;
            await sleep(500);
          }
        } else {
          return await handleError(response);
        }
      } else {
        return response;
      }
    }
    // only get here if retries are exhausted
    clearToken();
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
    const auth = get(authStore);

    await this.refreshkOktaAuth();
    while (retries > 0) {
      const response = await fetch(url, {
        method: "PATCH",
        headers: {
          "Content-Type": contentType,
          Authorization: `Bearer ${auth.token}`,
        },
        body: JSON.stringify(body),
      });
      if (!response.ok) {
        if (response.status === 401) {
          const refreshed = await this.refreshToken();

          if (refreshed) {
            retries -= 1;
            await sleep(500);
          }
        } else {
          return await handleError(response);
        }
      } else {
        return response;
      }
    }
    // only get here if retries are exhausted
    clearToken();
    // check if authentication is eve
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
    const auth = get(authStore);

    await this.refreshkOktaAuth();
    while (retries > 0) {
      const headers = {
        "Content-Type": contentType,
        Authorization: `Bearer ${auth.token}`,
        ...additionalHeaders,
      };

      const response = await fetch(url, {
        method: "POST",
        headers,
        body: JSON.stringify(body),
      });
      if (!response.ok) {
        // Try refreshing the jwt token if the response is unauthorized
        if (response.status === 401) {
          const refreshed = await this.refreshToken();

          if (refreshed) {
            retries -= 1;
            await sleep(500);
          }
        } else {
          return await handleError(response);
        }
      } else {
        return response;
      }
    }
    // only get here if retries are exhausted
    clearToken();
    void goto(CommonPaths.LOGIN);

    return new Response("Unauthorized", { status: 401 });
  }
}

export const apiHandler = new ApiHandler();
