// src/lib/stores/authStore.js
import { browser } from "$app/environment";

class AuthStore {
  constructor() {}

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
      return localStorage.getItem("needAuth");
    } else {
      return false;
    }
  }

  setupAuth() {
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

export const authStore = new AuthStore();
