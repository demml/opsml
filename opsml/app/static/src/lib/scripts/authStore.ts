// src/lib/stores/authStore.js
import { browser } from "$app/environment";
import { goto } from "$app/navigation";
import { CommonPaths } from "$lib/scripts/types";

class AuthStore {
  constructor() {
    this.setupAuth();
  }

  setUsername(username: string) {
    if (browser) {
      localStorage.setItem("username", username);
    }
  }

  getUsername() {
    return localStorage.getItem("username");
  }

  clearUsername() {
    if (browser) {
      localStorage.removeItem("username");
    }
  }

  loggedIn() {
    if (this.getToken()) {
      return "true";
    } else {
      return "false";
    }
  }

  setToken(token) {
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
      return localStorage.getItem("jwtToken");
    }
  }

  needAuth() {
    if (browser) {
      if (localStorage.getItem("needAuth") === "true") {
        return true;
      } else {
        return false;
      }
    }
  }

  async setupAuth() {
    if (browser) {
      let response = fetch(CommonPaths.VERIFY, {
        method: "GET", // default, so we can ignore
      })
        .then((response) => {
          if (!response.ok) {
            throw new Error("HTTP error " + response.status);
          } else {
            return response.json();
          }
        })
        .catch((error) => {
          console.error("Fetch error: ", error);
        });

      response.then((data) => {
        if (browser) {
          localStorage.setItem("needAuth", data);
        }
      });
    }
  }

  async loginWithCredentials(
    username: string,
    password: string
  ): Promise<boolean> {
    if (browser) {
      let formData = new FormData();
      formData.append("username", username);
      formData.append("password", password);

      let response = await fetch(CommonPaths.TOKEN, {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        let data = await response.json();
        let accessToken = data["access_token"];

        // need to set token and username
        this.setToken(accessToken);
        this.setUsername(username);

        return true;
      } else {
        return false;
      }
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
) {
  if (store.needAuth() && !store.getToken()) {
    // redirect to login page with previous page as query param
    if (previousPath) {
      goto(CommonPaths.LOGIN + "?redirect=" + previousPath);
    } else {
      goto(CommonPaths.LOGIN);
    }
    // do nothing
  } else {
    return;
  }
}
