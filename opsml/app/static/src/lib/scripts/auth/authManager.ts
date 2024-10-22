// src/stores/authStore.ts
import { writable, get } from "svelte/store";
import { CommonPaths } from "$lib/scripts/types";
import { browser } from "$app/environment";

export interface OpsmlAuth {
  opsml_auth: boolean;
}

export interface OpsmlAuthState {
  user: string | undefined;
  access_token: string | undefined;
  refresh_token: string | undefined;
}

// Define the shape of your auth state
export interface AuthState {
  authType: string;
  requireAuth: boolean;
  isAuthenticated: boolean;
  state: OpsmlAuthState;
}

// Initialize the store with default values
export const initialAuthState: AuthState = {
  requireAuth: false,
  isAuthenticated: false,
  authType: "basic",
  state: {
    user: undefined,
    access_token: undefined,
    refresh_token: undefined,
  },
};

export const authStore = writable<AuthState>(initialAuthState);

export function clearToken() {
  authStore.update((state) => ({ ...state, token: undefined }));
}

// Function to update the auth state
export function setAuthState(authState: AuthState) {
  authStore.set(authState);

  if (browser) {
    localStorage.setItem("authState", JSON.stringify(authState));
  }
}

// Function to clear the auth state
export function clearAuthState() {
  authStore.set(initialAuthState);
  if (browser) {
    localStorage.removeItem("authState");
  }
}

export async function login(username: string, password: string) {
  const auth = get(authStore);

  if (auth.authType === "basic") {
    // Call your login endpoint here
    const response = await fetch("/api/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ username, password }),
    });

    if (response.ok) {
      const data = await response.json();
      setAuthState({
        ...auth,
        isAuthenticated: true,
        state: {
          user: data.user,
          access_token: data.access_token,
          refresh_token: data.refresh_token,
        },
      });
    } else {
      throw new Error("Login failed");
    }
  }
}

export async function setupAuth() {
  // check if authState is stored in localStorage (for page refresh)
  let storedAuthState: string | null = null;

  if (browser) {
    storedAuthState = localStorage.getItem("authState");
  }

  if (storedAuthState) {
    const authState: AuthState = JSON.parse(storedAuthState);
    setAuthState(authState);
    return;
  }

  // check if we are in test mode
  if (import.meta.env.VITE_TEST) {
    setAuthState({
      ...initialAuthState,
      isAuthenticated: false,
    });
    return;

    // all other cases
  } else {
    // await opsm/verify
    let response = (await fetch(CommonPaths.VERIFY, {
      method: "GET", // default, so we can ignore
    })) as Response;

    if (!response.ok) {
      throw new Error(`HTTP error ${response.status}`);
    } else {
      let data = (await response.json()) as OpsmlAuth;

      console.log("data", data);

      // define auth type. If okta_auth is true, then we need to set up the OktaConfig
      // if not, then we don't need to set up the OktaConfig and default to basic auth
      let authType: string = "basic";

      setAuthState({
        authType: authType,
        requireAuth: data.opsml_auth,
        isAuthenticated: false,
        state: {
          user: undefined,
          access_token: undefined,
          refresh_token: undefined,
        },
      });
    }
  }
}
