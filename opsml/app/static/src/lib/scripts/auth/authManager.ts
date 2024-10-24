import { writable, get, type Writable } from "svelte/store";
import { CommonPaths, type Token } from "$lib/scripts/types";
import { browser } from "$app/environment";
import { OktaAuth } from "@okta/okta-auth-js";
import { goto } from "$app/navigation";

export interface OpsmlAuth {
  opsml_auth: boolean;
  okta_auth: boolean;
  okta_client_id: string | undefined;
  okta_issuer: string | undefined;
  okta_redirect_uri: string | undefined;
  okta_scopes: string[] | undefined;
}

export interface OpsmlAuthState {
  user: string | undefined;
  access_token: string | undefined;
  refresh_token: string | undefined;
}

export interface OktaConfig {
  clientId: string;
  issuer: string;
  redirectUri: string;
  scopes: string[];
  pkce: boolean;
}

export interface AuthState {
  authType: string;
  requireAuth: boolean;
  isAuthenticated: boolean;
  state: OpsmlAuthState;
  config: OktaConfig | undefined;
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
  config: undefined,
};

class AuthManager {
  private static instance: AuthManager;
  public authStore: Writable<AuthState>;

  private constructor() {
    this.authStore = writable<AuthState>(initialAuthState);
  }

  public static getInstance(): AuthManager {
    if (!AuthManager.instance) {
      AuthManager.instance = new AuthManager();
    }
    return AuthManager.instance;
  }

  public clearToken() {
    // keep user and clear tokens
    let auth = get(this.authStore);
    this.setAuthState({
      ...auth,
      state: {
        ...auth.state,
        access_token: undefined,
        refresh_token: undefined,
      },
    });
  }

  public logout() {
    this.authStore.update((state) => ({
      ...state,
      isAuthenticated: false,
      state: baseOpsmlAuthState,
    }));

    if (browser) {
      localStorage.removeItem("cacheAuthState");
    }
  }

  public setAuthState(authState: AuthState) {
    this.authStore.set(authState);

    if (browser) {
      localStorage.setItem("cacheAuthState", JSON.stringify(authState));
    }
  }

  public async login(username: string, password: string): Promise<boolean> {
    const auth = get(this.authStore);
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
    } else if (auth.authType === "okta") {
      const oktaAuth = new OktaAuth(auth.config!);
      await oktaAuth.signInWithRedirect();
    }
    return false;
  }

  public async getAuthReqs(): Promise<OpsmlAuth> {
    let response = (await fetch(CommonPaths.AUTH_SETTINGS, {
      method: "GET",
    })) as Response;

    if (!response.ok) {
      throw new Error(`HTTP error ${response.status}`);
    } else {
      let data = (await response.json()) as OpsmlAuth;
      return data;
    }
  }

  public async setupAuth(): Promise<AuthState> {
    if (browser) {
      let storedAuthState: string | null = null;

      storedAuthState = localStorage.getItem("cacheAuthState");

      if (storedAuthState) {
        const authState: AuthState = JSON.parse(storedAuthState);
        this.setAuthState(authState);
        return authState;
      }
      let reqs: OpsmlAuth = await this.getAuthReqs();

      if (!reqs.okta_auth) {
        this.setAuthState({
          authType: "basic",
          requireAuth: reqs.opsml_auth,
          isAuthenticated: false,
          state: baseOpsmlAuthState,
          config: undefined,
        });
      } else {
        let oktaConfig: OktaConfig = {
          clientId: reqs.okta_client_id as string,
          issuer: reqs.okta_issuer as string,
          redirectUri: reqs.okta_redirect_uri as string,
          scopes: reqs.okta_scopes as string[],
          pkce: true,
        };

        this.setAuthState({
          authType: "okta",
          requireAuth: reqs.okta_auth,
          isAuthenticated: false,
          state: baseOpsmlAuthState,
          config: oktaConfig,
        });
      }
    }
    return get(this.authStore);
  }

  public getAuthState(): AuthState {
    return get(this.authStore);
  }

  public setAccessToken(token: string) {
    let auth = get(this.authStore);
    this.setAuthState({
      ...auth,
      state: {
        ...auth.state,
        access_token: token,
      },
    });
  }

  public getAccessToken(): string | undefined {
    let auth = get(this.authStore);
    return auth.state.access_token;
  }
}

export const authManager = AuthManager.getInstance();

export const loggedIn = writable({
  isLoggedIn: false,
});

export function checkAuthstore(): void {
  authManager.setupAuth().then((authstate) => {
    if (authstate.requireAuth && !authstate.isAuthenticated) {
      // redirect to login page with previous page as query param
      void goto(CommonPaths.LOGIN, { invalidateAll: true });
      // do nothing
    }
  });
}
