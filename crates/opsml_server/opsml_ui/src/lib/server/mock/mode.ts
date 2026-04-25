import { dev } from "$app/environment";
import { parseDevMockValue } from "$lib/components/settings/devMock";

export function isDevMockEnabled(
  cookies: Pick<{ get(name: string): string | undefined }, "get">,
): boolean {
  return dev && parseDevMockValue(cookies.get("opsml_ui_dev_mock"));
}
