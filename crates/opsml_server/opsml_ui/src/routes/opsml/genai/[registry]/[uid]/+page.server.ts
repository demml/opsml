import { redirect } from "@sveltejs/kit";
import type { PageServerLoad } from "./$types";
import { getRegistryTypeLowerCase } from "$lib/utils";
import type { ServiceCard } from "$lib/components/card/card_interfaces/servicecard";
import { getCardMetadata } from "$lib/server/card/utils";
import type { BaseCard } from "$lib/components/home/types";

export const load: PageServerLoad = async ({ parent, params, fetch }) => {
  let { registryType } = await parent();

  console.log("uid param:", params.uid);

  if (!registryType) {
    throw redirect(307, "/opsml/home");
  }

  let metadata = (await getCardMetadata(
    undefined,
    undefined,
    undefined,
    params.uid,
    registryType,
    fetch
  )) as BaseCard;

  redirect(
    301,
    `/opsml/${getRegistryTypeLowerCase(registryType)}/card/${metadata.space}/${
      metadata.name
    }/${metadata.version}/card`
  );
};
