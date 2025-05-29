import { opsmlClient } from "$lib/components/api/client.svelte";
import { RoutePaths } from "$lib/components/api/routes";
import type {
  CreateUserRequest,
  CreateUserUiResponse,
  RecoveryResetRequest,
  ResetPasswordResponse,
  UserResponse,
  LogOutResponse,
} from "$lib/components/user/types";
import { format } from "date-fns";
import { userStore } from "./user.svelte";

// Helper function for registering a user via the api client
// It is assumed that all arguments have been validated prior to calling this function
export async function registerUser(
  username: string,
  password: string,
  email: string
): Promise<CreateUserUiResponse> {
  const request: CreateUserRequest = {
    username: username,
    password: password,
    email: email,
  };
  const response = await opsmlClient.post(
    RoutePaths.REGISTER,
    request,
    userStore.jwt_token
  );
  return (await response.json()) as CreateUserUiResponse;
}

// Helper for getting user information for user section
export async function getUser(username: string): Promise<UserResponse> {
  let path = `${RoutePaths.USER}/${username}`;

  const response = await opsmlClient.get(path, undefined, userStore.jwt_token);

  return (await response.json()) as UserResponse;
}

export async function resetUserPassword(
  username: string,
  recovery_code: string,
  newPassword: string
): Promise<ResetPasswordResponse> {
  const request: RecoveryResetRequest = {
    username: username,
    recovery_code: recovery_code,
    new_password: newPassword,
  };

  const response = await opsmlClient.post(
    RoutePaths.RESET_PASSWORD,
    request,
    userStore.jwt_token
  );

  return (await response.json()) as ResetPasswordResponse;
}

export async function logout(): Promise<LogOutResponse> {
  let path = `${RoutePaths.LOGOUT}`;

  const response = await opsmlClient.get(path, undefined, userStore.jwt_token);

  return (await response.json()) as LogOutResponse;
}
