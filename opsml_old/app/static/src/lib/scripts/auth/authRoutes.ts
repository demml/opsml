import {
  CommonPaths,
  type RegisterUser,
  type UserExistsResponse,
  type securityQuestionResponse,
} from "$lib/scripts/types";
import { apiHandler } from "../apiHandler";

export interface RegisterResponse {
  message: string;
  success: boolean;
}

export async function registerUser(
  request: RegisterUser
): Promise<RegisterResponse> {
  const response = await apiHandler.post(
    CommonPaths.REGISTER,
    request,
    "application/json"
  );

  if (response.ok) {
    return { success: true, message: "User registered successfully" };
  }
  // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
  const error = await response.json();

  // eslint-disable-next-line @typescript-eslint/no-unsafe-member-access
  return { success: false, message: error.detail as string };
}

export async function checkUser(username: string): Promise<UserExistsResponse> {
  const url: string = `${CommonPaths.EXISTS}?username=${username}`;
  const response = await apiHandler.get(url);
  if (response.ok) {
    const res = (await response.json()) as UserExistsResponse;
    return {
      exists: res.exists,
      username: res.username,
    };
  }
  return {
    exists: false,
    username,
  };
}

export async function getSecurityQuestion(
  username: string
): Promise<securityQuestionResponse> {
  const url: string = `${CommonPaths.SECURITY_QUESTION}?username=${username}`;
  const response = await apiHandler.get(url);
  if (response.ok) {
    const res = (await response.json()) as securityQuestionResponse;
    return {
      question: res.question,
      exists: true,
      error: "NA",
    };
  }

  if (response.status === 404) {
    return {
      question: "NA",
      exists: false,
      error: "User not found",
    };
  }
  return {
    question: "NA",
    exists: false,
    error: "Error fetching security question",
  };
}

export async function generateTempToken(
  username: string,
  answer: string
): Promise<string> {
  const body = { username, answer };
  const response = await apiHandler.post(CommonPaths.TEMP_TOKEN, body);
  if (response.ok) {
    return (await response.json()) as string;
  }
  return "Error generating token";
}
