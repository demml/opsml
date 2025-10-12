import { redirect } from "@sveltejs/kit";
import type { PageLoad } from "./$types";
import { getRegistryTypeLowerCase, RegistryType } from "$lib/utils";
import type { ServiceCard } from "$lib/components/card/card_interfaces/servicecard";
import { getCardMetadata } from "$lib/server/card/utils";

export const load: PageLoad = async ({ params, fetch }) => {
  let registryType = RegistryType.Data;

  let resp = await getCardMetadata(
    undefined,
    undefined,
    undefined,
    params.uid,
    registryType,
    fetch
  );

  let metadata = (await resp.json()) as ServiceCard;

  redirect(
    301,
    `/opsml/${getRegistryTypeLowerCase(registryType)}/card/${metadata.space}/${
      metadata.name
    }/${metadata.version}/card`
  );
};
