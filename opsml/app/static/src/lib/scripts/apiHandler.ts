import { goto } from "$app/navigation";
import { CommonPaths } from "$lib/scripts/types";
import { authStore } from "$lib/scripts/authStore";

class ApiHandler {
  constructor() {}

  async get(url: string): Promise<Response> {
    let response = await fetch(url, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${authStore.getToken()}`,
      },
    });

    if (response.status === 401) {
      authStore.clearToken();
      authStore.clearUsername();
      goto(CommonPaths.LOGIN);
    }

    return response;
  }

  async post(
    url: string,
    body: any,
    contentType: string = "application/json",
    additionalHeaders: Record<string, string> = {}
  ): Promise<Response> {
    let headers = {
      "Content-Type": contentType,
      Authorization: `Bearer ${authStore.getToken()}`,
      ...additionalHeaders,
    };
    let response = await fetch(url, {
      method: "POST",
      headers: headers,
      body: JSON.stringify(body),
    });

    if (response.status === 401) {
      authStore.clearToken();
      authStore.clearUsername();
      goto(CommonPaths.LOGIN);
    }

    return response;
  }

  async put(
    url: string,
    body: any,
    contentType: string = "application/json"
  ): Promise<Response> {
    let response = await fetch(url, {
      method: "PUT",
      headers: {
        "Content-Type": contentType,
        Authorization: `Bearer ${authStore.getToken()}`,
      },
      body: JSON.stringify(body),
    });

    if (response.status === 401) {
      authStore.clearToken();
      authStore.clearUsername();
      goto(CommonPaths.LOGIN);
    }

    return response;
  }

  async patch(
    url: string,
    body: any,
    contentType: string = "application/json"
  ): Promise<Response> {
    let response = await fetch(url, {
      method: "PATCH",
      headers: {
        "Content-Type": contentType,
        Authorization: `Bearer ${authStore.getToken()}`,
      },
      body: JSON.stringify(body),
    });

    if (response.status === 401) {
      authStore.clearToken();
      authStore.clearUsername();
      goto(CommonPaths.LOGIN);
    }

    return response;
  }
}

export const apiHandler = new ApiHandler();
