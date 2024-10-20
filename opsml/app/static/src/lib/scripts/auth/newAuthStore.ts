// src/stores/authStore.ts
import { writable } from "svelte/store";

export interface OpsmlAuth {
  opsml_auth: boolean;
  okta_auth: boolean;
  okta_client_id: string | undefined;
  okta_issuer: string | undefined;
  okta_redirect_uri: string | undefined;
  okta_scopes: string | undefined;
}

export interface OktaConfig {
  OktaClientId: string;
  OktaIssuer: string;
  OktaRedirectUri: string;
  OktaScope: string;
  pkce: boolean;
}

// Define the shape of your auth state
export interface AuthState {
  authType: string;
  requireAuth: boolean;
  isAuthenticated: boolean;
  user: string | undefined;
  token: string | undefined;
  OktaConfig: OktaConfig | undefined;
}

// Initialize the store with default values
export const initialAuthState: AuthState = {
  requireAuth: false,
  isAuthenticated: false,
  authType: "basic",
  user: undefined,
  token: undefined,
  OktaConfig: undefined,
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
