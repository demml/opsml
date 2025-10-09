import { json } from "@sveltejs/kit";
import type { RequestHandler } from "./$types";
import { userStore } from "$lib/components/user/user.svelte";

/**
 * Handles login requests and sets JWT cookie.
 * Only authentication and cookie logic here; UI navigation is handled client-side.
 */
export const POST: RequestHandler = async ({ request, cookies }) => {
  const { username, password } = await request.json();

  // Validate credentials using your backend logic
  const loginResponse = await userStore.login(username, password, cookies);

  if (loginResponse.authenticated) {
    return json({ success: true });
  } else {
    // Return error response
    return json(
      {
        success: false,
        error: loginResponse.message ?? "Invalid username or password",
      },
      { status: 401 }
    );
  }
};
