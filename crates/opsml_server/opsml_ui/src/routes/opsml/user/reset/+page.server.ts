import type { Actions } from "./$types";
import { fail } from "@sveltejs/kit";
import {
  loginUser,
  setTokenInCookies,
  setUsernameInCookies,
} from "$lib/server/auth/validateToken";
import { validateLoginSchema } from "$lib/components/user/schema";
import { resetUserPassword } from "$lib/server/user/utils";
import { type ResetPasswordResponse } from "$lib/components/user/types";
import {
  validatePasswordResetSchema,
  type PasswordResetSchema,
} from "$lib/components/user/schema";

export const actions = {
  default: async ({ request, fetch }) => {
    let data = await request.formData();

    const username = data.get("username") as string;
    const newPassword = data.get("newPassword") as string;
    const recoveryCode = data.get("recoveryCode") as string;
    const confirmPassword = data.get("confirmPassword") as string;
    const argsValid = validatePasswordResetSchema(
      username,
      recoveryCode,
      newPassword,
      confirmPassword
    );

    if (!argsValid.success) {
      return fail(400, {
        success: false,
        validationErrors: argsValid.errors ?? {},
      });
    }

    await resetUserPassword(username, recoveryCode, newPassword, fetch);

    return {
      success: true,
    };
  },
} satisfies Actions;
