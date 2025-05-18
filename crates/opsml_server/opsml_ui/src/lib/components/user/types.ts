export interface LoginResponse {
  authenticated: boolean;
  message: string;
  username: string;
  jwt_token: string;
}

export interface UserResponse {
  username: string;
  active: boolean;
  permissions: string[];
  group_permissions: string[];
}

export interface CreateUserResponse {
  user: UserResponse;
  recovery_codes: string[];
  message: string;
}

export interface CreateUserRequest {
  username: string;
  password: string;
  email: string;
}

export interface CreateUserUiResponse {
  registered: boolean;
  response?: CreateUserResponse;
  error?: string;
}
