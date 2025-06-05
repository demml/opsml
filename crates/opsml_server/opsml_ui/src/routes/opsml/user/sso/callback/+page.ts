export const ssr = false;

import { RoutePaths, UiPaths } from "$lib/components/api/routes";
import type { PageLoad } from "./$types";
import { userStore } from "$lib/components/user/user.svelte";
import { exchangeSsoCallbackCode } from "$lib/components/user/utils";

export const load: PageLoad = async ({ url }) => {
  const code = (url as URL).searchParams.get("code") as string;
  const state = (url as URL).searchParams.get("state") as string;
  //const storedState = userStore.getSsoState();
  // get local storage state
  const storedState = localStorage.getItem("ssoState") || "";

  // log code and state
  console.log("SSO Callback Code:", code);
  console.log("SSO Callback State:", state);
  console.log("Stored SSO State:", storedState);

  if (!code || !state || state !== storedState) {
    throw new Error("Invalid state or missing authorization code");
  }

  let loginResponse = await exchangeSsoCallbackCode(code);

  if (loginResponse.authenticated) {
    userStore.setSsoState("");
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
