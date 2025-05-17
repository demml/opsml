import { opsmlClient } from "$lib/components/api/client.svelte";
import { RoutePaths } from "$lib/components/api/routes";
import type {
  CreateUserRequest,
  CreateUserResponse,
} from "$lib/components/user/types";

// Helper function for registering a user via the api client
// It is assumed that all arguments have been validated prior to calling this function
export async function registerUser(
  username: string,
  password: string,
  email: string
): Promise<CreateUserResponse> {
  const request: CreateUserRequest = {
    username: username,
    password: password,
    email: email,
  };
  const response = await opsmlClient.post(RoutePaths.USER, request);
  return (await response.json()) as CreateUserResponse;
}
