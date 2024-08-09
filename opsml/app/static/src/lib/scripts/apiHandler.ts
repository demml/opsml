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
    contentType: string | undefined
  ): Promise<Response> {
    let response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": contentType || "application/json",
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
