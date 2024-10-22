// src/lib/scripts/auth/handleOktaCallback.ts
import { setAuthState, authStore } from "./newAuthStore";
import { get } from "svelte/store";

export async function handleOktaCallback() {
  const auth = get(authStore);

  if (auth.authType === "okta") {
    const tokens = await auth.oktaAuth!.token.parseFromUrl();
    auth.oktaAuth!.tokenManager.setTokens(tokens.tokens);

    const user = await auth.oktaAuth!.getUser();
    setAuthState({
      requireAuth: true,
      isAuthenticated: true,
      user: user.email,
      token: tokens.tokens,
      authType: "okta",
      oktaAuth: auth.oktaAuth,
      oktaConfig: auth.oktaConfig,
    });
  } else {
    throw new Error("Okta configuration is missing");
  }
}
