// src/lib/stores/authStore.js
import { browser } from "$app/environment";
import { writable } from "svelte/store";

const createAuthStore = () => {
  const storedToken = browser ? localStorage.getItem("jwtToken") : null;
  const { subscribe, set, update } = writable(storedToken);

  return {
    subscribe,
    setToken: (token) => {
      if (browser) {
        localStorage.setItem("jwtToken", token);
      }
      set(token);
    },
    clearToken: () => {
      if (browser) {
        localStorage.removeItem("jwtToken");
      }
      set(null);
    },
    GetToken: () => {
      return storedToken;
    },
  };
};

export const authStore = createAuthStore();
