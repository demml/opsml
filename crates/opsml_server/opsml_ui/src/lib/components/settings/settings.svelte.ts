import { browser } from "$app/environment";
import { RoutePaths } from "../api/routes";
import { opsmlClient } from "../api/client.svelte";
import type { UiSettings } from "./types";
import { redirect } from "@sveltejs/kit";
import { userStore } from "../user/user.svelte";

export class UiSettingsStore {
  scouterEnabled = $state(false);
  ssoEnabled = $state(false);

  constructor() {}

  public async getSettings() {
    if (browser) {
      const response = await opsmlClient.get(
        RoutePaths.SETTINGS,
        undefined,
        userStore.jwt_token
      );
      const data = (await response.json()) as UiSettings;
      this.scouterEnabled = data.scouter_enabled;
      this.ssoEnabled = data.sso_enabled;
    }
  }
}

export const uiSettingsStore = new UiSettingsStore();
