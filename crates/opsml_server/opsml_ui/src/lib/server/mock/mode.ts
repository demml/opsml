import { dev } from "$app/environment";
import { DEV_MOCK_COOKIE, parseDevMockValue } from "$lib/components/settings/devMock";

export function isDevMockEnabled(
  cookies: Pick<{ get(name: string): string | undefined }, "get">,
): boolean {
  return dev && parseDevMockValue(cookies.get(DEV_MOCK_COOKIE));
}
