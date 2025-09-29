export const ssr = false;
export const prerender = false;
import { redirect } from "@sveltejs/kit";
import { validateUserOrRedirect } from "$lib/components/user/user.svelte";
import type { PageLoad } from "./$types";
import type { DataCard } from "$lib/components/card/card_interfaces/datacard";
import { getCardMetadata } from "$lib/components/card/utils";
import { getRegistryPath } from "$lib/utils";

export const load: PageLoad = async ({ params, parent }) => {
  await validateUserOrRedirect();
  const { registryType } = await parent();

  let metadata = (await getCardMetadata(
    undefined,
    undefined,
    undefined,
    params.uid,
    registryType
  )) as DataCard;

  redirect(
    301,
    `/opsml/${getRegistryPath(registryType)}/card/${metadata.space}/${
      metadata.name
    }/${metadata.version}/card`
  );
};
