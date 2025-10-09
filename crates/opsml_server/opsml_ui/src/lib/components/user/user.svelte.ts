import type { LoginResponse } from "./types";

export class UserStore {
  username = $state("");
  logged_in = $state(false);
  sso_state = $state("");
  permissions = $state<string[]>([]);
  group_permissions = $state<string[]>([]);
  repositories = $state<string[]>([]);
  recovery_codes = $state<string[]>([]);
  favorite_spaces = $state<string[]>([]);

  constructor() {}

  public fromLoginResponse(response: LoginResponse) {
    this.updateUser(
      response.username,
      response.permissions,
      response.group_permissions,
      response.favorite_spaces
    );
  }

  public resetUser() {
    this.username = "";
    this.logged_in = false;
    this.repositories = [];
    this.recovery_codes = [];
    this.permissions = [];
    this.group_permissions = [];
    this.favorite_spaces = [];
  }

  public updateUser(
    username: string,
    permissions: string[],
    group_permissions: string[],
    favorite_spaces: string[] = []
  ) {
    this.username = username;
    this.logged_in = true;
    this.permissions = permissions;
    this.group_permissions = group_permissions;
    this.favorite_spaces = favorite_spaces;
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

  public setFavoriteSpaces(favorite_spaces: string[]) {
    this.favorite_spaces = favorite_spaces;
  }

  public setSsoState(state: string) {
    this.sso_state = state;
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

  public getSsoState(): string {
    return this.sso_state;
  }
}

export const userStore = new UserStore();
