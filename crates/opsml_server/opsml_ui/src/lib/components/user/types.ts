export interface LoginResponse {
  authenticated: boolean;
  message: string;
  username: string;
  jwt_token: string;
}
