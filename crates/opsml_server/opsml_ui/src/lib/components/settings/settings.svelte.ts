import type { UiSettings } from "./types";

export class UiSettingsStore {
  scouterEnabled = $state(false);
  ssoEnabled = $state(false);

  public initialize(settings: UiSettings) {
    this.scouterEnabled = settings.scouter_enabled;
    this.ssoEnabled = settings.sso_enabled;
  }
}

export const uiSettingsStore = new UiSettingsStore();
