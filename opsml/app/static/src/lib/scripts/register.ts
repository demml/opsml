import { type RegisterUser } from "$lib/scripts/types";

export interface RegisterResponse {
  message: string;
  success: boolean;
}

export async function registerUser(
  request: RegisterUser
): Promise<RegisterResponse> {
  const response = await fetch("/opsml/auth/register", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
  });

  if (response.ok) {
    return { success: true, message: "User registered successfully" };
  } else {
    let error = await response.json();
    return { success: false, message: error["detail"] };
  }
}
