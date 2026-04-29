import { browser, dev } from "$app/environment";
import {
  DEV_MOCK_COOKIE,
  DEV_MOCK_STORAGE_KEY,
} from "./devMock";

export class DevMockStore {
  enabled = $state(false);

  public initialize(initial: boolean) {
    if (!dev) {
      this.enabled = false;
      return;
    }

    this.enabled = initial;

    if (!browser) {
      return;
    }

    localStorage.setItem(DEV_MOCK_STORAGE_KEY, String(initial));
    this.syncCookie(initial);
  }

  public toggle() {
    this.setEnabled(!this.enabled);
  }

  public setEnabled(enabled: boolean) {
    this.enabled = enabled;

    if (!browser) {
      return;
    }

    localStorage.setItem(DEV_MOCK_STORAGE_KEY, String(enabled));
    this.syncCookie(enabled);
    window.location.reload();
  }

  private syncCookie(enabled: boolean) {
    document.cookie = `${DEV_MOCK_COOKIE}=${enabled ? "true" : "false"}; Path=/; Max-Age=31536000; SameSite=Lax`;
  }
}

export const devMockStore = new DevMockStore();
