import { getCardMetadata } from "./utils";
import { getCardReadMe } from "./readme/utils";
import type { RegistryType } from "$lib/utils";
import type { ReadMe } from "$lib/components/readme/util";

/**
 * Loads card layout data
 */
export async function loadCardLayout(
  registryType: RegistryType,
  space: string,
  name: string,
  version: string,
  fetch: typeof globalThis.fetch
): Promise<{
  metadata: any;
  registryType: RegistryType;
  readme: ReadMe;
  activeTab: string;
}> {
  const [metadata, readme] = await Promise.all([
    getCardMetadata(space, name, version, undefined, registryType, fetch),
    getCardReadMe(name, space, registryType, fetch),
  ]);

  return {
    metadata,
    registryType,
    readme,
    activeTab: "card",
  };
}
