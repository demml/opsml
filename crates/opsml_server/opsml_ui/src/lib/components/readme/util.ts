import { opsmlClient } from "$lib/components/api/client.svelte";
import { RoutePaths } from "$lib/components/api/routes";
import { RegistryType } from "$lib/utils";
import type { CardQueryArgs } from "../api/schema";

export type ReadMe = {
  readme: string;
  exists: boolean;
};

export async function getCardReadMe(
  name: string,
  repository: string,
  version: string,
  registry_type: RegistryType
): Promise<ReadMe> {
  const params: CardQueryArgs = {
    name: name,
    repository: repository,
    version: version,
    registry_type: registry_type,
  };

  const response = await opsmlClient.get(RoutePaths.README, params);
  return await response.json();
}
