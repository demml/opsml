import { CommonPaths, type RegisterUser } from "$lib/scripts/types";
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

export async function checkUser(request: RegisterUser): Promise<Boolean> {
  let url: string = CommonPaths.EXISTS + "?username=" + request.username;
  let response = await apiHandler.get(url);
  if (response.ok) {
    return true;
  } else {
    return false;
  }
}
