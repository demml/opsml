import { goTop } from "$lib/scripts/utils";
import { CommonPaths, type User, type UserUpdated } from "$lib/scripts/types";
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
import { authStore } from "$lib/scripts/auth/authStore";
import { apiHandler } from "$lib/scripts/apiHandler";

export interface SecurityReturn {
  question?: string;
  error: string;
  warnUser: boolean;
}

export interface TokenReturn {
  token: string;
  error: string;
  warnUser: boolean;
}

export interface PasswordReturn {
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

export async function getToken(
  username: string,
  answer: string
): Promise<TokenReturn> {
  let tokenResult = await generateTempToken(username, answer);

  if (
    [
      CommonErrors.USER_NOT_FOUND.toString(),
      CommonErrors.INCORRECT_ANSWER.toString(),
      CommonErrors.TOKEN_ERROR.toString(),
    ].includes(tokenResult)
  ) {
    return { token: "", error: tokenResult, warnUser: true };
  } else {
    return { token: tokenResult, error: "", warnUser: false };
  }
}

export async function resetPassword(
  passStrength: number,
  username: string,
  newPassword: string
): Promise<PasswordReturn> {
  if (passStrength < 100) {
    return { error: "Password is not strong enough", warnUser: true };
  }

  let response = await apiHandler.get(
    `${CommonPaths.USER_AUTH}?username=${username}`
  );
  let user: User = await response.json();

  // update password
  user.password = newPassword;
  let updateResponse = await apiHandler.put(CommonPaths.USER_AUTH, user);
  let updateResult = (await updateResponse.json()) as UserUpdated;

  if (updateResult.updated) {
    return { error: "", warnUser: false };
  } else {
    return { error: "Failed to update user", warnUser: true };
  }
}
