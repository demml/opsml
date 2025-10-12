import { createOpsmlClient } from "$lib/server/api/opsmlClient";
import { RoutePaths } from "$lib/components/api/routes";
import { RegistryType } from "$lib/utils";
import { type ReadMe, type UploadResponse } from "$lib/components/readme/util";
import type { CardQueryArgs, ReadMeArgs } from "$lib/components/api/schema";

/**
 * Get the README content for a card.
 * @param name The name of the card.
 * @param space The space the card is in.
 * @param registry_type The type of registry the card is in.
 * @param fetch The fetch function to use.
 * @returns The README content for the card.
 */
export async function getCardReadMe(
  name: string,
  space: string,
  registry_type: RegistryType,
  fetch: typeof globalThis.fetch
): Promise<ReadMe> {
  const params: CardQueryArgs = {
    name: name,
    space: space,
    registry_type: registry_type,
  };

  const response = await createOpsmlClient(fetch).get(
    RoutePaths.README,
    params
  );
  return await response.json();
}

/**
 * Get the README content for a card.
 * @param name The name of the card.
 * @param space The space the card is in.
 * @param registry_type The type of registry the card is in.
 * @param fetch The fetch function to use.
 * @returns The README content for the card.
 */
export async function createReadMe(
  space: string,
  name: string,
  registry_type: RegistryType,
  content: string,
  fetch: typeof globalThis.fetch
): Promise<UploadResponse> {
  let args: ReadMeArgs = {
    space: space,
    name: name,
    registry_type: registry_type,
    readme: content,
  };

  return (await createOpsmlClient(fetch).post(RoutePaths.README, args)).json();
}
