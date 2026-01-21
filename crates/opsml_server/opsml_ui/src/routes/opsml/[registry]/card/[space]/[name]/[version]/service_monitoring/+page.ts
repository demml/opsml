export const ssr = false;

import type { PageLoad } from "./$types";
import {
  getProfilesFromMetadata,
  getSortedDriftTypes,
} from "$lib/components/scouter/dashboard/utils";
import { getRegistryFromString } from "$lib/utils";
import { DriftType } from "$lib/components/scouter/types";

export const load: PageLoad = async ({ parent, fetch }) => {
  const { metadata, cards } = await parent();

  // Aggregate all drift profiles from all cards
  const cardMonitoringData = await Promise.all(
    metadata.cards.cards.map(async (cardRef) => {
      const card = cards[cardRef.alias];
      const registryType = getRegistryFromString(cardRef.type);

      try {
        const profiles = await getProfilesFromMetadata(
          fetch,
          card,
          registryType,
        );
        const driftTypes = getSortedDriftTypes(profiles);

        return {
          alias: cardRef.alias,
          name: cardRef.name,
          space: cardRef.space,
          version: cardRef.version,
          registryType,
          profiles,
          driftTypes,
          hasMonitoring: driftTypes.length > 0,
        };
      } catch (error) {
        console.warn(`Failed to load monitoring for ${cardRef.name}:`, error);
        return {
          alias: cardRef.alias,
          name: cardRef.name,
          space: cardRef.space,
          version: cardRef.version,
          registryType,
          profiles: [],
          driftTypes: [],
          hasMonitoring: false,
        };
      }
    }),
  );

  // Get union of all drift types available across all cards
  const allDriftTypes = [
    ...new Set(
      cardMonitoringData
        .filter((cm) => cm.hasMonitoring)
        .flatMap((cm) => cm.driftTypes),
    ),
  ];

  return {
    metadata,
    cardMonitoringData: cardMonitoringData.filter((cm) => cm.hasMonitoring),
    allDriftTypes,
  };
};
