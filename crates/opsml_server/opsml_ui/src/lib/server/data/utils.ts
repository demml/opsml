import { type DataCard } from "$lib/components/card/card_interfaces/datacard";
import { type DataProfile } from "$lib/components/card/data/types";
import { getRegistryTableName, RegistryType } from "$lib/utils";
import { getRawFile } from "../card/files/utils";
import { loadDataProfile } from "$lib/components/card/data/utils";

/** Helper function to get the data profile for a card
 * @param card The DataCard to get the profile for
 * @returns The DataProfile object
 */
export async function getDataProfile(
  fetch: typeof globalThis.fetch,
  card: DataCard
): Promise<DataProfile> {
  let dataProfileUri = card.metadata.interface_metadata.save_metadata
    .data_profile_uri as string;

  let profilePath = `${getRegistryTableName(RegistryType.Data)}/${card.space}/${
    card.name
  }/v${card.version}/${dataProfileUri}`;

  let rawFile = await getRawFile(
    fetch,
    profilePath,
    card.uid,
    RegistryType.Data
  );

  return loadDataProfile(rawFile.content);
}
