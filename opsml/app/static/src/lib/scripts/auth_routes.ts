import {
  CommonPaths,
  type RegisterUser,
  type UserExistsResponse,
  type securityQuestionResponse,
} from "$lib/scripts/types";
import { apiHandler } from "./apiHandler";

export interface RegisterResponse {
  message: string;
  success: boolean;
}

export async function registerUser(
  request: RegisterUser
): Promise<RegisterResponse> {
  let response = await apiHandler.post(
    CommonPaths.REGISTER,
    request,
    "application/json"
  );

  if (response.ok) {
    return { success: true, message: "User registered successfully" };
  } else {
    let error = await response.json();
    return { success: false, message: error["detail"] };
  }
}

export async function checkUser(username: string): Promise<UserExistsResponse> {
  let url: string = CommonPaths.EXISTS + "?username=" + username;
  let response = await apiHandler.get(url);
  if (response.ok) {
    let res = await response.json();
    return {
      exists: res["exists"],
      username: res["username"],
    };
  } else {
    return {
      exists: false,
      username: username,
    };
  }
}

export async function getSecurityQuestion(
  username: string
): Promise<securityQuestionResponse> {
  let url: string = CommonPaths.SECURITY_QUESTION + "?username=" + username;
  let response = await apiHandler.get(url);
  if (response.ok) {
    let res = await response.json();
    return {
      question: res["question"],
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
  } else {
    return {
      question: "NA",
      exists: false,
      error: "Error fetching security question",
    };
  }
}

export async function generateTempToken(
  username: string,
  answer: string
): Promise<string> {
  let body = { username: username, answer: answer };
  let response = await apiHandler.post(CommonPaths.TEMP_TOKEN, body);
  if (response.ok) {
    return await response.json();
  }

  if (response.status === 404) {
    return "User not found";
  } else if (response.status === 401) {
    return "Incorrect answer";
  } else {
    return "Error generating token";
  }
}
