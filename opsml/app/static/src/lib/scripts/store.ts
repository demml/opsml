import { writable } from "svelte/store";
import { authStore } from "$lib/authStore";

export const loginStore = writable(authStore.loggedIn());

export function updateLoginStore() {
  loginStore.update((loggedIn) => authStore.loggedIn());
}
