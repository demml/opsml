import { goto } from "$app/navigation";
import { RoutePaths } from "$lib/components/api/routes";
import { user } from "$lib/components/auth/AuthStore.svelte";

async function handleError(response: Response): Promise<Response> {
  const errorMessage = await response.text();
  void goto(`${RoutePaths.ERROR}?message=${errorMessage}`);
  return new Response(null, {
    status: 500,
    statusText: "Failure",
  });
}

class ApiHandler {
  constructor() {}

  async request(
    url: string,
    method: string,
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    body: any = null,
    contentType: string = "application/json",
    additionalHeaders: Record<string, string> = {}
  ): Promise<Response> {
    const headers = {
      "Content-Type": contentType,
      Authorization: `Bearer ${user.user.token}`,
      ...additionalHeaders,
    };

    const response = await fetch(url, {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined,
    });

    if (response.ok) {
      return response;
    } else {
      return await handleError(response);
    }
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
