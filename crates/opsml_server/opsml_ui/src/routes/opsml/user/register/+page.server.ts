import type { Actions } from "./$types";
import { fail } from "@sveltejs/kit";
import { registerUser } from "$lib/server/user/utils";
import { validateUserRegisterSchema } from "$lib/components/user/schema";
import { logger } from "$lib/server/logger";

export const actions = {
  default: async ({ request, fetch }) => {
    let data = await request.formData();

    const username = data.get("username") as string;
    const password = data.get("password") as string;
    const reEnterPassword = data.get("reEnterPassword") as string;
    const email = data.get("email") as string;

    const argsValid = validateUserRegisterSchema(
      username,
      password,
      reEnterPassword,
      email
    );

    if (!argsValid.success) {
      logger.error(`Validation errors: ${JSON.stringify(argsValid.errors)}`);
      return fail(400, {
        success: false,
        validationErrors: argsValid.errors ?? {},
      });
    }

    const registerResponse = await registerUser(
      username,
      password,
      email,
      fetch
    );

    if (registerResponse.registered) {
      return {
        success: true,
        response: registerResponse.response,
      };
    } else {
      // Return error response
      let errorMessage = "Error encountered during registration";
      if (
        registerResponse.error?.includes(
          "Failed to create user: error returned from database"
        )
      ) {
        errorMessage =
          "Registration failed. Username or email may already be in use. Please try again with different credentials or contact the administrator.";
      }

      return fail(400, {
        success: false,
        error: errorMessage,
      });
    }
  },
} satisfies Actions;
