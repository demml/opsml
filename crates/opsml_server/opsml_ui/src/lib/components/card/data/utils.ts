import { getRawFile } from "$lib/components/files/utils";
import type { DataCard } from "../card_interfaces/datacard";
import type { DataProfile } from "$lib/components/card/data/types";
import { RegistryType, getRegistryTableName } from "$lib/utils";

function loadDataProfile(jsonString: string): DataProfile {
  try {
    // Parse the JSON string
    const parsedData = JSON.parse(jsonString);

    // Cast the parsed data to the DataProfile type
    return parsedData as DataProfile;
  } catch (error) {
    throw new Error("Invalid JSON string");
  }
}

export async function getDataProfile(card: DataCard): Promise<DataProfile> {
  let dataProfileUri = card.metadata.interface_metadata.save_metadata
    .data_profile_uri as string;

  let profilePath = `${getRegistryTableName(RegistryType.Data)}/${
    card.repository
  }/${card.name}/v${card.version}/${dataProfileUri}`;

  console.log("dataProfileUri", profilePath);

  let rawFile = await getRawFile(profilePath, card.uid, RegistryType.Data);

  return loadDataProfile(rawFile.content);
}
