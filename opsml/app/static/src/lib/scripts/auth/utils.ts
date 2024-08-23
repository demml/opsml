import { goTop } from "$lib/scripts/utils";
import { CommonPaths } from "$lib/scripts/types";
import { checkUser } from "$lib/scripts/auth/auth_routes";
import type { UserExistsResponse } from "$lib/scripts/types";
import {
  type securityQuestionResponse,
  CommonErrors,
  type PasswordStrength,
} from "$lib/scripts/types";
import {
  getSecurityQuestion,
  generateTempToken,
} from "$lib/scripts/auth/auth_routes";

export interface SecurityReturn {
  question?: string;
  error: string;
  warnUser: boolean;
}

export async function getSecurity(
  username: string | undefined
): Promise<SecurityReturn> {
  let warnUser = false;
  let errorMessage = "";

  if (!username) {
    // check if username is not empty
    warnUser = true;
    errorMessage = "Username cannot be empty";
    return { error: errorMessage, warnUser };
  }

  let userExists: UserExistsResponse = await checkUser(username as string);
  if (!userExists.exists) {
    errorMessage = "User does not exist";
    return { error: errorMessage, warnUser: true };
  }

  let secResponse = await getSecurityQuestion(username);

  if (!secResponse.exists) {
    errorMessage = secResponse.error;
    return { error: errorMessage, warnUser: true };
  }

  return { question: secResponse.question, error: errorMessage, warnUser };
}
