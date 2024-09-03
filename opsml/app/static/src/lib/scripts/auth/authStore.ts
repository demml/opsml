// src/lib/stores/authStore.js
import { browser } from "$app/environment";
import { goto } from "$app/navigation";
import { CommonPaths, type Token } from "$lib/scripts/types";

class AuthStore {
  constructor() {
    this.setupAuth();
  }

  setUsername(username: string) {
    if (browser) {
      localStorage.setItem("username", username);
    }
  }

  getUsername(): string | undefined {
    const username: string | null = localStorage.getItem("username");
    if (username === null) {
      return undefined;
    }
    return username;
  }

  clearUsername() {
    if (browser) {
      localStorage.removeItem("username");
    }
  }

  loggedIn() {
    if (this.getToken()) {
      return "true";
    }
    return "false";
  }

  setToken(token: string) {
    if (browser) {
      localStorage.setItem("jwtToken", token);
    }
  }

  clearToken() {
    if (browser) {
      localStorage.removeItem("jwtToken");
    }
  }

  getToken() {
    if (browser) {
      const token: string | null = localStorage.getItem("jwtToken");
      if (token === null) {
        return undefined;
      }
      return token;
    }
  }

  needAuth() {
    if (browser) {
      if (localStorage.getItem("needAuth") === "true") {
        return true;
      }
      return false;
    }
  }

  setupAuth() {
    if (browser) {
      // for testing purposes (don't have another way currently)
      if (import.meta.env.VITE_TEST) {
        localStorage.setItem("needAuth", "false");
        return;
      }
      const response = fetch(CommonPaths.VERIFY, {
        method: "GET", // default, so we can ignore
      })
        .then((response) => {
          if (!response.ok) {
            throw new Error(`HTTP error ${response.status}`);
          } else {
            return response.json();
          }
        })
        .catch((error) => {
          throw new Error(`Fetch error: ${error}`);
        });

      response
        .then((data: string) => {
          if (browser) {
            localStorage.setItem("needAuth", data);
          }
        })
        .catch((error) => {
          console.error("Fetch error: ", error);
        });
    }
  }

  async loginWithCredentials(
    username: string,
    password: string
  ): Promise<boolean> {
    if (browser) {
      const formData = new FormData();
      formData.append("username", username);
      formData.append("password", password);

      const response = await fetch(CommonPaths.TOKEN, {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        const data = (await response.json()) as Token;
        const accessToken = data.access_token;

        // need to set token and username
        this.setToken(accessToken);
        this.setUsername(username);

        return true;
      }
      return false;
    }
    return false;
  }

  logout() {
    if (browser) {
      this.clearToken();
      this.clearUsername();
    }
  }
}

export const authStore = new AuthStore();

export function checkAuthstore(
  store: AuthStore,
  previousPath: string | undefined
): void {
  if (store.needAuth() && !store.getToken()) {
    // redirect to login page with previous page as query param
    if (previousPath) {
      void goto(`${CommonPaths.LOGIN}?redirect=${previousPath}`);
    } else {
      void goto(CommonPaths.LOGIN);
    }
    // do nothing
  }
}
