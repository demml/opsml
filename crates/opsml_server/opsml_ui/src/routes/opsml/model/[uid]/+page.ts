export const ssr = false;
export const prerender = false;
import { redirect } from "@sveltejs/kit";
import { validateUserOrRedirect } from "$lib/components/user/user.svelte";
import type { PageLoad } from "./$types";
import type { ModelCard } from "$lib/components/card/card_interfaces/modelcard";
import { getCardMetadata } from "$lib/components/card/utils";
import { getRegistryTypeLowerCase } from "$lib/utils";

export const load: PageLoad = async ({ params, parent }) => {
  await validateUserOrRedirect();
  const { registryType } = await parent();

  let metadata = (await getCardMetadata(
    undefined,
    undefined,
    undefined,
    params.uid,
    registryType
  )) as ModelCard;

  redirect(
    301,
    `/opsml/${getRegistryTypeLowerCase(registryType)}/card/${metadata.space}/${
      metadata.name
    }/${metadata.version}`
  );
};
