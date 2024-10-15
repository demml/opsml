import { getDataProfile } from "$lib/scripts/data/utils";

export async function load({ url }) {
  const name = (url as URL).searchParams.get("name") as string | undefined;
  const repository = (url as URL).searchParams.get("repository") as
    | string
    | undefined;
  const version = (url as URL).searchParams.get("version") as
    | string
    | undefined;

  const profile = await getDataProfile(repository!, name!, version!);

  console.log(profile);
}
