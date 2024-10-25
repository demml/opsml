import { authManager } from "$lib/scripts/auth/authManager";

export const ssr = false;

/** @type {import('./$types').PageLoad} */
export function load() {
  const auth = authManager.getAuthState();

  return {
    username: auth.state.user,
    loggedIn: auth.isAuthenticated,
  };
}
