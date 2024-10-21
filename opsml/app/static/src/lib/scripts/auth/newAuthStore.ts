// src/stores/authStore.ts
import { writable } from "svelte/store";
import { OktaAuth, type Tokens } from "@okta/okta-auth-js";
import { get } from "svelte/store";

export interface OpsmlAuth {
  opsml_auth: boolean;
  okta_auth: boolean;
  okta_client_id: string | undefined;
  okta_issuer: string | undefined;
  okta_redirect_uri: string | undefined;
  okta_scopes: string[] | undefined;
}

export interface OktaConfig {
  clientId: string;
  issuer: string;
  redirectUri: string;
  scopes: string[];
  pkce: boolean;
}

// Define the shape of your auth state
export interface AuthState {
  authType: string;
  requireAuth: boolean;
  isAuthenticated: boolean;
  user: string | undefined;
  token: string | Tokens | undefined;
  oktaAuth: OktaAuth | undefined;
}

// Initialize the store with default values
export const initialAuthState: AuthState = {
  requireAuth: false,
  isAuthenticated: false,
  authType: "basic",
  user: undefined,
  token: undefined,
  oktaAuth: undefined,
};

export const authStore = writable<AuthState>(initialAuthState);

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
        user: data.user,
        token: data.token,
      });
    } else {
      throw new Error("Login failed");
    }
  } else if (auth.authType === "okta") {
    // Use Okta Auth JS library for Okta login
    if (auth.oktaAuth) {
      auth.oktaAuth.signInWithRedirect();
    } else {
      throw new Error("Okta configuration is missing");
    }
  }
}
