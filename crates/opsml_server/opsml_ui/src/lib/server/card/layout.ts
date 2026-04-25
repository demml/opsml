import { getCardMetadata } from "./utils";
import { getCardReadMe } from "./readme/utils";
import {
  buildMockCardLayout,
  buildMockCardMetadata,
} from "$lib/components/mock/opsmlMockData";
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
  mockMode?: boolean;
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
  useMockFallback = false,
): Promise<CardLayoutData> {
  try {
    const metadata = (await getCardMetadata(
      space,
      name,
      version,
      undefined,
      registryType,
      fetch,
    )) as CardMetadata;
    const readme = await getCardReadMe(name, space, registryType, fetch).catch(
      () => ({
        readme: "",
        exists: false,
      }),
    );

    return {
      metadata,
      registryType,
      readme,
      activeTab: "card",
      mockMode: false,
    };
  } catch (error) {
    if (!useMockFallback) {
      throw error;
    }

    return {
      ...buildMockCardLayout(registryType, space, name, version),
      mockMode: true,
    };
  }
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
  useMockFallback = false,
): Promise<CardMetadata> {
  try {
    const metadata = await getCardMetadata(
      space,
      name,
      version,
      undefined,
      registryType,
      fetch,
    );

    return metadata as CardMetadata;
  } catch (error) {
    if (!useMockFallback) {
      throw error;
    }

    return buildMockCardMetadata(registryType, space, name, version);
  }
}
