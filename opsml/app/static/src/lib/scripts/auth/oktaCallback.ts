// src/lib/scripts/auth/handleOktaCallback.ts
import { OktaAuth } from "@okta/okta-auth-js";
import { setAuthState, authStore } from "./newAuthStore";
import { get } from "svelte/store";

export async function handleOktaCallback() {
  const auth = get(authStore);
  const oktaConfig = auth.oktaConfig;
  if (oktaConfig) {
    const oktaAuth = new OktaAuth({
      clientId: oktaConfig.clientId,
      issuer: oktaConfig.issuer,
      redirectUri: oktaConfig.redirectUri,
      scopes: oktaConfig.scopes,
      pkce: oktaConfig.pkce,
    });

    const tokens = await oktaAuth.token.parseFromUrl();
    oktaAuth.tokenManager.setTokens(tokens.tokens);

    const user = await oktaAuth.getUser();
    setAuthState({
      requireAuth: true,
      isAuthenticated: true,
      user: user.email,
      token: tokens.tokens,
      authType: "okta",
      oktaConfig: oktaConfig,
    });
  } else {
    throw new Error("Okta configuration is missing");
  }
}
