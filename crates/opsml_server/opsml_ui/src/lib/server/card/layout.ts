import { getCardMetadata } from "./utils";
import { getCardReadMe } from "./readme/utils";
import { getRegistryFromString, type RegistryType } from "$lib/utils";
import type { ReadMe } from "$lib/components/readme/util";
import type { ServiceCard } from "$lib/components/card/card_interfaces/servicecard";
import { logger } from "../logger";

/**
 * Loads card layout data
 */
export async function loadCardLayout(
  registryType: RegistryType,
  space: string,
  name: string,
  version: string,
  fetch: typeof globalThis.fetch,
): Promise<{
  metadata: any;
  registryType: RegistryType;
  readme: ReadMe;
  activeTab: string;
  has_drift_profile: boolean;
}> {
  const [metadata, readme] = await Promise.all([
    getCardMetadata(space, name, version, undefined, registryType, fetch),
    getCardReadMe(name, space, registryType, fetch),
  ]);

  let has_drift_profile = false;
  if (metadata.metadata && metadata.metadata.drift_profile_uri_map) {
    has_drift_profile =
      Object.keys(metadata.metadata.drift_profile_uri_map).length > 0;
  }

  return {
    metadata,
    registryType,
    readme,
    activeTab: "card",
    has_drift_profile,
  };
}

/**  executes the same logic as loadCardLayout but
 * also load the metadata for all cards in a service
 */
export async function loadServiceCardLayout(
  registryType: RegistryType,
  space: string,
  name: string,
  fetch: typeof globalThis.fetch,
): Promise<{
  metadata: any;
  registryType: RegistryType;
  readme: ReadMe;
  activeTab: string;
  cards: Record<string, any>;
  has_drift_profile: boolean;
}> {
  const [metadata, readme] = await Promise.all([
    getCardMetadata(space, name, undefined, undefined, registryType, fetch),
    getCardReadMe(name, space, registryType, fetch),
  ]);

  const metdata: ServiceCard = metadata;

  const cardPromises = metdata.cards.cards
    .map((card) => {
      const cardRegistryType = getRegistryFromString(card.type);
      if (!cardRegistryType) return null;

      return getCardMetadata(
        card.space,
        card.name,
        card.version,
        undefined,
        cardRegistryType,
        fetch,
      ).then((cardMetadata) => ({ alias: card.alias, metadata: cardMetadata }));
    })
    .filter(Boolean);

  const cardResults = await Promise.all(cardPromises);

  const cards = Object.fromEntries(
    cardResults
      .filter(
        (result): result is { alias: string; metadata: any } => result !== null,
      )
      .map((result) => [result.alias, result.metadata]),
  );

  // check if any cards have drift profile
  let has_drift_profile = false;
  for (const card of Object.values(cards)) {
    if (card.metadata && card.metadata.drift_profile_uri_map) {
      has_drift_profile =
        Object.keys(card.metadata.drift_profile_uri_map).length > 0;
      if (has_drift_profile) break;
    }
  }

  return {
    metadata,
    registryType,
    readme,
    activeTab: "card",
    cards,
    has_drift_profile,
  };
}
