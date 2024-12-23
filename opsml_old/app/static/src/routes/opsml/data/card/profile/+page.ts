import { getDataProfile } from "$lib/scripts/data/utils";
import { type DataProfile } from "$lib/scripts/data/types";

export async function load({ url }) {
  const name = (url as URL).searchParams.get("name") as string | undefined;
  const repository = (url as URL).searchParams.get("repository") as
    | string
    | undefined;
  const version = (url as URL).searchParams.get("version") as
    | string
    | undefined;

  const profile = await getDataProfile(repository!, name!, version!);

  function getFeatureNames(profile: DataProfile): string[] {
    // get keys of profile object
    return Object.keys(profile.features);
  }

  return {
    profile: profile,
    featureNames: getFeatureNames(profile),
  };
}
