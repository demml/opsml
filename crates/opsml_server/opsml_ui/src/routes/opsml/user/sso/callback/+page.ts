export const ssr = false;

import { RoutePaths, UiPaths } from "$lib/utils/api/routes";
import type { PageLoad } from "./$types";
import { userStore } from "$lib/components/user/user.svelte";
import { exchangeSsoCallbackCode } from "$lib/components/user/utils";

export const load: PageLoad = async ({ url }) => {
  const code = (url as URL).searchParams.get("code") as string;
  const state = (url as URL).searchParams.get("state") as string;
  //const storedState = userStore.getSsoState();
  // get local storage state
  const storedState = localStorage.getItem("ssoState") || "";

  if (!code || !state || state !== storedState) {
    throw new Error("Invalid state or missing authorization code");
  }

  let codeVerifier = localStorage.getItem("ssoCodeVerifier") || "";
  let loginResponse = await exchangeSsoCallbackCode(code, codeVerifier);

  if (loginResponse.authenticated) {
    localStorage.removeItem("ssoState"); // Clear the stored state after successful login
    localStorage.removeItem("ssoCodeVerifier"); // Clear the code verifier after successful login

    userStore.updateUser(
      loginResponse.username,
      loginResponse.jwt_token,
      loginResponse.permissions,
      loginResponse.group_permissions,
      loginResponse.favorite_spaces
    );
  }

  return { response: loginResponse };
};
