export const ssr = false;
export const prerender = false;
import { redirect } from "@sveltejs/kit";
import { validateUserOrRedirect } from "$lib/components/user/user.svelte";
import type { PageLoad } from "./$types";
import type { ExperimentCard } from "$lib/components/card/card_interfaces/experimentcard";
import { getCardMetadata } from "$lib/components/card/utils";
import { getRegistryPath } from "$lib/utils";

export const load: PageLoad = async ({ params, parent }) => {
  const { registryType } = await parent();

  let metadata = (await getCardMetadata(
    undefined,
    undefined,
    undefined,
    params.uid,
    registryType
  )) as ExperimentCard;

  redirect(
    301,
    `/opsml/${getRegistryPath(registryType)}/card/${metadata.space}/${
      metadata.name
    }/${metadata.version}/card`
  );
};
