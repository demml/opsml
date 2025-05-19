import { browser } from "$app/environment";

export class UserStore {
  username = $state("");
  jwt_token = $state("");
  logged_in = $state(false);
  repositories = $state<string[]>([]);
  recovery_codes = $state<string[]>([]);

  constructor() {
    if (browser) {
      const storedToken = this.getTokenFromCookie();
      if (storedToken) {
        this.jwt_token = storedToken;
        this.logged_in = true;
      }
    }
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

  private removeTokenCookie() {
    document.cookie =
      "jwt_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
  }

  public resetUser() {
    this.username = "";
    this.jwt_token = "";
    this.logged_in = false;
    this.repositories = [];
    this.recovery_codes = [];

    if (browser) {
      this.removeTokenCookie();
    }
  }

  private setTokenCookie(token: string) {
    // Set cookie to expire in 24 hours (or match your token expiration)
    const expirationDate = new Date();
    expirationDate.setTime(expirationDate.getTime() + 1 * 60 * 60 * 1000);

    document.cookie = `jwt_token=${token}; expires=${expirationDate.toUTCString()}; path=/; SameSite=Strict`;
  }

  public updateUser(username: string, jwt_token: string) {
    this.username = username;
    this.jwt_token = jwt_token;
    this.logged_in = true;

    if (browser) {
      this.setTokenCookie(jwt_token);
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
}

export const userStore = new UserStore();
