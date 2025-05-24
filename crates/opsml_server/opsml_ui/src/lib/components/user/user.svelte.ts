import { browser } from "$app/environment";

export class UserStore {
  username = $state("");
  jwt_token = $state("");
  refresh_token = $state("");
  logged_in = $state(false);
  permissions = $state<string[]>([]);
  group_permissions = $state<string[]>([]);
  repositories = $state<string[]>([]);
  recovery_codes = $state<string[]>([]);
  favorite_spaces = $state<string[]>([]);

  constructor() {
    if (browser) {
      const storedToken = this.getTokenFromCookie();
      const storedRefreshToken = this.getRefreshTokenFromCookie();
      if (storedToken) {
        this.jwt_token = storedToken;
        this.logged_in = true;
      }
      if (storedRefreshToken) {
        this.refresh_token = storedRefreshToken;
      }
    }
  }

  public async validateAndRefreshTokens(): Promise<boolean> {
    const token = this.getTokenFromCookie();
    if (!token) return false;

    if (this.isTokenExpired(token)) {
      const refreshToken = this.getRefreshTokenFromCookie();
      if (!refreshToken) {
        this.resetUser();
        return false;
      }

      try {
        // Call your refresh token API endpoint
        const response = await fetch("/opsml/api/auth/refresh", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ refresh_token: refreshToken }),
        });

        if (!response.ok) throw new Error("Refresh failed");

        const { new_token, new_refresh_token } = await response.json();
        this.setTokenCookies(new_token, new_refresh_token);
        return true;
      } catch {
        this.resetUser();
        return false;
      }
    }

    return true;
  }

  public getTokenFromCookie(): string | null {
    if (!browser) return null;

    const cookies = document.cookie.split(";");
    const tokenCookie = cookies.find((cookie) =>
      cookie.trim().startsWith("jwt_token=")
    );

    if (tokenCookie) {
      return tokenCookie.split("=")[1].trim();
    }

    return null;
  }

  public getRefreshTokenFromCookie(): string | null {
    if (!browser) return null;
    const cookies = document.cookie.split(";");
    const tokenCookie = cookies.find((cookie) =>
      cookie.trim().startsWith("refresh_token=")
    );
    if (tokenCookie) {
      return tokenCookie.split("=")[1].trim();
    }
    return null;
  }

  private removeTokenCookies() {
    // Remove JWT token
    document.cookie =
      "jwt_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/; SameSite=Strict; Secure";

    // Remove refresh token
    document.cookie =
      "refresh_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/; SameSite=Strict; Secure";
  }

  public resetUser() {
    this.username = "";
    this.jwt_token = "";
    this.logged_in = false;
    this.repositories = [];
    this.recovery_codes = [];
    this.permissions = [];
    this.group_permissions = [];
    this.favorite_spaces = [];

    if (browser) {
      this.removeTokenCookies();
    }
  }

  private setTokenCookies(token: string, refreshToken: string) {
    const expirationDate = new Date();
    expirationDate.setTime(expirationDate.getTime() + 1 * 60 * 60 * 1000); // 1 hour
    document.cookie = `jwt_token=${token}; expires=${expirationDate.toUTCString()}; domain=${
      window.location.hostname
    }; path=/; SameSite=Strict; Secure`;

    // Refresh token with longer expiration
    const refreshExpiration = new Date();
    refreshExpiration.setTime(
      refreshExpiration.getTime() + 24 * 60 * 60 * 1000
    ); // 24 hours

    document.cookie = `refresh_token=${refreshToken}; expires=${refreshExpiration.toUTCString()}; domain=${
      window.location.hostname
    }; path=/; SameSite=Strict; Secure`;
  }

  public updateUser(
    username: string,
    jwt_token: string,
    refresh_token: string,
    permissions: string[],
    group_permissions: string[],
    favorite_spaces: string[] = []
  ) {
    this.username = username;
    this.jwt_token = jwt_token;
    this.refresh_token = refresh_token;
    this.logged_in = true;
    this.permissions = permissions;
    this.group_permissions = group_permissions;
    this.favorite_spaces = favorite_spaces;

    if (browser) {
      this.setTokenCookies(jwt_token, refresh_token);
    }
  }

  private isTokenExpired(token: string): boolean {
    try {
      const payload = JSON.parse(atob(token.split(".")[1]));
      return payload.exp * 1000 < Date.now();
    } catch {
      return true;
    }
  }

  public setRepositories(repositories: string[]) {
    this.repositories = repositories;
  }

  public setRecoveryCodes(codes: string[]) {
    this.recovery_codes = codes;
  }

  public setUsername(username: string) {
    this.username = username;
  }

  // all perms are stored as <operation>:<resource>
  // split permissions by : and get resource
  // if index at 1 is empty set it to "all"
  public getPermissions(): string[][] {
    return this.permissions.map((perm) => {
      const parts = perm.split(":");
      if (parts[1] === "") parts[1] = "all";
      return parts;
    });
  }

  // same as permissions
  public getGroupPermissions(): string[][] {
    return this.group_permissions.map((perm) => {
      const parts = perm.split(":");
      if (parts[1] === "") parts[1] = "all";
      return parts;
    });
  }
}

export const userStore = new UserStore();
