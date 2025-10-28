import type { Actions } from "./$types";
import { fail } from "@sveltejs/kit";
import {
  loginUser,
  setTokenInCookies,
  setUsernameInCookies,
} from "$lib/server/auth/validateToken";
import { validateLoginSchema } from "$lib/components/user/schema";

export const actions = {
  default: async ({ cookies, request, fetch }) => {
    let data = await request.formData();

    const username = data.get("username") as string;
    const password = data.get("password") as string;
    const argsValid = validateLoginSchema(username, password);

    if (!argsValid.success) {
      return fail(400, {
        success: false,
        validationErrors: argsValid.errors ?? {},
      });
    }

    const loginResponse = await loginUser(fetch, username, password);

    if (loginResponse.authenticated) {
      // Return success response with JWT token
      setTokenInCookies(cookies, loginResponse.jwt_token);
      setUsernameInCookies(cookies, username);

      // mask the token in the response after setting the cookie
      loginResponse.jwt_token = "*****";
      return {
        success: true,
        data: loginResponse,
      };
    } else {
      // Return error response
      return fail(400, {
        success: false,
        error: loginResponse.message ?? "Invalid username or password",
      });
    }
  },
} satisfies Actions;
