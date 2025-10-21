import { redirect } from "@sveltejs/kit";

/**
 * Redirects root URL "/" to the main application page "/opsml/home".
 * Ensures users always land on the main dashboard.
 */
export function load() {
  throw redirect(302, "/opsml/home");
}
