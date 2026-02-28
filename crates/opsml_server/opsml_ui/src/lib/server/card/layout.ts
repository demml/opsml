import { getCardMetadata } from "./utils";
import { getCardReadMe } from "./readme/utils";
import type { RegistryType } from "$lib/utils";
import type { ReadMe } from "$lib/components/readme/util";
import type { DataCard } from "$lib/components/card/card_interfaces/datacard";
import type { ModelCard } from "$lib/components/card/card_interfaces/modelcard";
import type { ExperimentCard } from "$lib/components/card/card_interfaces/experimentcard";
import type { PromptCard } from "$lib/components/card/card_interfaces/promptcard";
import type { ServiceCard } from "$lib/components/card/card_interfaces/servicecard";

export type CardMetadata =
  | DataCard
  | ModelCard
  | ExperimentCard
  | PromptCard
  | ServiceCard;

export type CardLayoutData = {
  metadata: CardMetadata;
  registryType: RegistryType;
  readme: ReadMe;
  activeTab: string;
};

/**
 * Loads card layout data
 */
export async function loadCardLayout(
  registryType: RegistryType,
  space: string,
  name: string,
  version: string,
  fetch: typeof globalThis.fetch,
): Promise<CardLayoutData> {
  const [metadata, readme] = await Promise.all([
    getCardMetadata(space, name, version, undefined, registryType, fetch),
    getCardReadMe(name, space, registryType, fetch),
  ]);

  return {
    metadata: metadata as CardMetadata,
    registryType,
    readme,
    activeTab: "card",
  };
}

/**
 * Loads card data for the main page (not layout) - currently only used for agent cards to get associated prompt cards with eval profiles.
 *
 */
export async function loadCard(
  registryType: RegistryType,
  space: string,
  name: string,
  version: string,
  fetch: typeof globalThis.fetch,
): Promise<CardMetadata> {
  const metadata = await getCardMetadata(
    space,
    name,
    version,
    undefined,
    registryType,
    fetch,
  );

  return metadata as CardMetadata;
}
