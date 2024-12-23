import { writable, get } from "svelte/store";
import { CommonPaths, type Token } from "$lib/scripts/types";
import { browser } from "$app/environment";
import { goto } from "$app/navigation";
import { persisted } from "svelte-persisted-store";

export interface OpsmlAuth {
  opsml_auth: boolean;
}

export interface OpsmlAuthState {
  user: string | undefined;
  access_token: string | undefined;
  refresh_token: string | undefined;
}

export interface AuthState {
  authType: string;
  requireAuth: boolean;
  isAuthenticated: boolean;
  state: OpsmlAuthState;
  setup: boolean;
}

const baseOpsmlAuthState: OpsmlAuthState = {
  user: undefined,
  access_token: undefined,
  refresh_token: undefined,
};

export const initialAuthState: AuthState = {
  requireAuth: false,
  isAuthenticated: false,
  authType: "basic",
  state: baseOpsmlAuthState,
  setup: false,
};

class AuthManager {
  private static instance: AuthManager;

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  public authStore: any;

  private constructor() {
    this.authStore = persisted("cacheAuthState", initialAuthState);
  }

  public static getInstance(): AuthManager {
    if (!AuthManager.instance) {
      AuthManager.instance = new AuthManager();
    }
    return AuthManager.instance;
  }

  public clearToken() {
    // keep user and clear tokens
    // eslint-disable-next-line @typescript-eslint/no-unsafe-argument
    const auth: AuthState = get(this.authStore);
    this.setAuthState({
      ...auth,
      state: {
        ...auth.state,
        access_token: undefined,
        refresh_token: undefined,
      },
    });
  }

  public async logout() {
    // eslint-disable-next-line  @typescript-eslint/no-unsafe-call, @typescript-eslint/no-unsafe-member-access
    this.authStore.reset();

    const auth = await this.setupAuth();
    auth.isAuthenticated = false;
    this.setAuthState(auth);
    loggedIn.set({ isLoggedIn: false });
  }

  public setAuthState(authState: AuthState) {
    // eslint-disable-next-line  @typescript-eslint/no-unsafe-call, @typescript-eslint/no-unsafe-member-access
    this.authStore.set(authState);
  }

  public async login(username: string, password: string): Promise<boolean> {
    const auth = await this.setupAuth();

    const formData = new FormData();
    formData.append("username", username);
    formData.append("password", password);

    if (auth.authType === "basic") {
      const response = await fetch(CommonPaths.TOKEN, {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        const data = (await response.json()) as Token;
        this.setAuthState({
          ...auth,
          isAuthenticated: true,
          state: {
            user: username,
            access_token: data.access_token,
            refresh_token: undefined,
          },
        });

        return true;
      } else {
        return false;
      }
    }
    return false;
  }

  public async getAuthReqs(): Promise<OpsmlAuth> {
    const response = await fetch(CommonPaths.AUTH_SETTINGS, {
      method: "GET",
    });

    if (!response.ok) {
      throw new Error(`HTTP error ${response.status}`);
    } else {
      const data = (await response.json()) as OpsmlAuth;
      return data;
    }
  }

  public async setupAuth(): Promise<AuthState> {
    if (browser) {
      // check if auth state is already set
      // eslint-disable-next-line  @typescript-eslint/no-unsafe-argument
      const auth: AuthState = get(this.authStore);
      if (auth.setup) {
        return auth;
      }

      const reqs: OpsmlAuth = await this.getAuthReqs();

      if (!reqs.opsml_auth) {
        this.setAuthState({
          authType: "basic",
          requireAuth: reqs.opsml_auth,
          isAuthenticated: false,
          state: baseOpsmlAuthState,
          setup: true,
        });
      }
    }
    // eslint-disable-next-line  @typescript-eslint/no-unsafe-argument
    return get(this.authStore);
  }

  public getAuthState(): AuthState {
    // eslint-disable-next-line  @typescript-eslint/no-unsafe-argument
    return get(this.authStore);
  }

  public setAccessToken(token: string) {
    // eslint-disable-next-line  @typescript-eslint/no-unsafe-argument
    const auth: AuthState = get(this.authStore);
    this.setAuthState({
      ...auth,
      state: {
        ...auth.state,
        access_token: token,
      },
    });
  }

  public getAccessToken(): string | undefined {
    // eslint-disable-next-line  @typescript-eslint/no-unsafe-argument
    const auth: AuthState = get(this.authStore);
    return auth.state.access_token;
  }
}

export const authManager = AuthManager.getInstance();

export const loggedIn = writable({
  isLoggedIn: false,
});

export async function checkAuthstore(): Promise<void> {
  const auth = await authManager.setupAuth();

  if (auth.requireAuth && !auth.isAuthenticated) {
    // redirect to login page with previous page as query param
    void goto(CommonPaths.LOGIN, { invalidateAll: true });
    // do nothing
  }
}
