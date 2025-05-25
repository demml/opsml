export interface LoginResponse {
  authenticated: boolean;
  message: string;
  username: string;
  jwt_token: string;
  permissions: string[];
  group_permissions: string[];
  favorite_spaces: string[];
}

export interface UserResponse {
  username: string;
  active: boolean;
  permissions: string[];
  group_permissions: string[];
  email: string;
  role: string;
  favorite_spaces: string[];
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

export interface RecoveryResetRequest {
  username: string;
  recovery_code: string;
  new_password: string;
}

export interface CreateUserUiResponse {
  registered: boolean;
  response?: CreateUserResponse;
  error?: string;
}

export interface ResetPasswordResponse {
  message: string;
  remaining_recovery_codes: number;
}

export interface AuthenticatedResponse {
  is_authenticated: boolean;
  user_response: UserResponse;
}

export interface JwtToken {
  token: string;
}
