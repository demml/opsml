import { browser } from '$app/environment';

export type ThemeMode = 'light' | 'dark' | 'system';

const STORAGE_KEY = 'opsml-theme';

class ThemeStore {
    mode = $state<ThemeMode>('system');
    private _username: string = '';
    private _mediaListener: (() => void) | null = null;

    get resolved(): 'light' | 'dark' {
        if (this.mode === 'system') {
            if (!browser) return 'light';
            return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
        }
        return this.mode;
    }

    initialize(serverPreference?: string, username?: string) {
        if (username) this._username = username;
        // Priority: localStorage (fast) > server preference > system
        if (browser) {
            const stored = localStorage.getItem(STORAGE_KEY) as ThemeMode | null;
            if (stored && ['light', 'dark', 'system'].includes(stored)) {
                this.mode = stored;
            } else if (serverPreference && ['light', 'dark', 'system'].includes(serverPreference)) {
                this.mode = serverPreference as ThemeMode;
            }
            this.apply();

            // Listen for system theme changes when in "system" mode (register once only)
                this._mediaListener = () => { if (this.mode === 'system') { this.mode = 'system'; this.apply(); } };
                window.matchMedia('(prefers-color-scheme: dark)')
                    .addEventListener('change', this._mediaListener);
            }
        }
    }

    toggle() {
        if (this.mode === 'light') {
            this.mode = 'dark';
        } else if (this.mode === 'dark') {
            this.mode = 'system';
        } else {
            this.mode = 'light';
        }
        this.apply();
        this.persist();
    }

    setMode(mode: ThemeMode) {
        this.mode = mode;
        this.apply();
        this.persist();
    }

    apply() {
        if (!browser) return;
        const resolved = this.resolved;
        const html = document.documentElement;
        html.classList.remove('theme-light', 'theme-dark');
        html.classList.add(`theme-${resolved}`);
    }

    private persist() {
        if (!browser) return;
        localStorage.setItem(STORAGE_KEY, this.mode);

        // Fire async PUT to server (non-blocking)
        this.persistToServer().catch(() => {
            // Silent fail — localStorage is the primary cache
        });
    }

    private async persistToServer() {
        if (!browser || !this._username) return;
        try {
            await fetch(`/opsml/api/user/${this._username}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ theme_preference: this.mode }),
            });
        } catch {
            // Best-effort — localStorage handles persistence
        }
    }
}

export const themeStore = new ThemeStore();
