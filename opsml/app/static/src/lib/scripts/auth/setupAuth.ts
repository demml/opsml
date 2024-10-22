import { CommonPaths } from "$lib/scripts/types";
import {
  setAuthState,
  initialAuthState,
  type AuthState,
  type OpsmlAuth,
  type OktaConfig,
} from "$lib/scripts/auth/newAuthStore";
import OktaAuth from "@okta/okta-auth-js";

export async function setupAuth() {
  console.log("setupAuth");
  // check if authState is stored in localStorage (for page refresh)
  const storedAuthState = localStorage.getItem("authState");
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

      // define auth type. If okta_auth is true, then we need to set up the OktaConfig
      // if not, then we don't need to set up the OktaConfig and default to basic auth
      let authType: string = data.okta_auth ? "okta" : "basic";
      let oktaAuth: OktaAuth | undefined = undefined;
      let oktaConfig: OktaConfig | undefined = undefined;

      if (data.okta_auth) {
        oktaConfig = {
          clientId: data.okta_client_id!,
          issuer: data.okta_issuer!,
          redirectUri: data.okta_redirect_uri!,
          scopes: data.okta_scopes!,
          pkce: true,
        };

        oktaAuth = new OktaAuth({
          clientId: oktaConfig.clientId,
          issuer: oktaConfig.issuer,
          redirectUri: oktaConfig.redirectUri,
          scopes: oktaConfig.scopes,
          pkce: oktaConfig.pkce,
        });
      }

      setAuthState({
        authType: authType,
        requireAuth: data.opsml_auth,
        isAuthenticated: false,
        user: undefined,
        token: undefined,
        oktaAuth: oktaAuth,
        oktaConfig: oktaConfig,
      });
    }
  }
}
