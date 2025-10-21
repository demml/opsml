// we are accessing localStorage, so this page cannot be server-side rendered
export const ssr = false;

import type { PageLoad } from "./$types";
import { userStore } from "$lib/components/user/user.svelte";
import { createInternalApiClient } from "$lib/api/internalClient";
import type { LoginResponse } from "$lib/components/user/types";
import { ServerPaths } from "$lib/components/api/routes";

export const load: PageLoad = async ({ url, fetch }) => {
  const code = (url as URL).searchParams.get("code") as string;
  const state = (url as URL).searchParams.get("state") as string;

  const storedState = localStorage.getItem("ssoState") || "";

  // validate state and code
  if (!code || !state || state !== storedState) {
    throw new Error("Invalid state or missing authorization code");
  }

  let codeVerifier = localStorage.getItem("ssoCodeVerifier") || "";

  // send to server to exchange code for tokens
  let resp = await createInternalApiClient(fetch).post(
    ServerPaths.SSO_CALLBACK,
    {
      code,
      code_verifier: codeVerifier,
    }
  );

  const loginResponse = (await resp.json()) as LoginResponse;

  if (loginResponse.authenticated) {
    // Clear the stored vars after successful login
    localStorage.removeItem("ssoState");
    localStorage.removeItem("ssoCodeVerifier");
    userStore.fromLoginResponse(loginResponse);
  }

  return { response: loginResponse };
};
