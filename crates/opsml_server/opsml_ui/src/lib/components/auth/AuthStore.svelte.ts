import { RoutePaths } from "$lib/components/api/routes";
import { apiHandler } from "$lib/components/api/apiHandler";

/**
 * AuthStore
 *
 * This file contains the AuthStore class and the User interface.
 **/
export interface User {
  username: string;
  jwt_token: string;
  logged_in: boolean;
}

export interface LoginResponse {
  username: string;
  jwt_token: string;
}

export interface Authenticated {
  is_authenticated: boolean;
}

// Set User Rune
function UserStore() {
  let baseUser: User = {
    username: "",
    jwt_token: "",
    logged_in: false,
  };

  //@ts-ignore
  let user = $state(baseUser);

  return {
    get user(): User {
      return user;
    },
    set user(data: User) {
      user = data;
    },
  };
}

export const user = UserStore();

class AuthManager {
  constructor() {}

  public async login(username: string, password: string): Promise<boolean> {
    const response = await apiHandler.post(RoutePaths.LOGIN, {
      username,
      password,
    });

    if (response.ok) {
      const data = (await response.json()) as LoginResponse;
      user.user = {
        username: data.username,
        jwt_token: data.jwt_token,
        logged_in: true,
      };

      return true;
    } else {
      return false;
    }
  }

  public async logout(): Promise<void> {
    // remove token from user
    user.user = { username: "", jwt_token: "", logged_in: false };
  }
}

export const authManager = new AuthManager();
