// src/stores/authStore.ts
import { writable, get } from "svelte/store";

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
  localStorage.setItem("authState", JSON.stringify(authState));
}

// Function to clear the auth state
export function clearAuthState() {
  authStore.set(initialAuthState);
  localStorage.removeItem("authState");
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
