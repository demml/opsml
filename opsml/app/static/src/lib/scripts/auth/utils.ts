import { CommonPaths, type User, type UserUpdated } from "$lib/scripts/types";
import { checkUser } from "$lib/scripts/auth/authRoutes";
import type { UserExistsResponse } from "$lib/scripts/types";
import { CommonErrors } from "$lib/scripts/types";
import {
  getSecurityQuestion,
  generateTempToken,
} from "$lib/scripts/auth/authRoutes";
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

  const userExists: UserExistsResponse = await checkUser(username);
  if (!userExists.exists) {
    errorMessage = "User does not exist";
    return { error: errorMessage, warnUser: true };
  }

  const secResponse = await getSecurityQuestion(username);

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
  const tokenResult = await generateTempToken(username, answer);

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

  const response = await apiHandler.get(
    `${CommonPaths.USER_AUTH}?username=${username}`
  );
  const user = (await response.json()) as User;

  // update password
  user.password = newPassword;
  const updateResponse = await apiHandler.put(CommonPaths.USER_AUTH, user);
  const updateResult = (await updateResponse.json()) as UserUpdated;

  if (updateResult.updated) {
    return { error: "", warnUser: false };
  } else {
    return { error: "Failed to update user", warnUser: true };
  }
}
