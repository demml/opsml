// src/lib/stores/authStore.js
import { browser } from "$app/environment";
import { goto } from "$app/navigation";

class AuthStore {
  constructor() {
    this.setupAuth();
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
    return localStorage.getItem("jwtToken");
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

  setupAuth() {
    if (browser) {
      let response = fetch("/opsml/auth/verify", {
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
}

export const authStore = new AuthStore();

export function checkAuthstore(
  store: AuthStore,
  previousPage: string | undefined
) {
  if (store.needAuth() && !store.getToken()) {
    // redirect to login page with previous page as query param
    if (previousPage) {
      goto("/opsml/auth/login?url=" + previousPage);
    } else {
      goto("/opsml/auth/login");
    }
    // do nothing
  } else {
    return;
  }
}
