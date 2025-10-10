import { redirect } from "@sveltejs/kit";
import type { PageServerLoad } from "./$types";
import type { ModelCard } from "$lib/components/card/card_interfaces/modelcard";
import { getCardMetadata } from "$lib/server/card/utils";
import { getRegistryPath } from "$lib/utils";

export const load: PageServerLoad = async ({
  params,
  parent,
  cookies,
  fetch,
}) => {
  const { registryType } = await parent();

  let metadata = (await getCardMetadata(
    undefined,
    undefined,
    undefined,
    params.uid,
    registryType,
    fetch,
    cookies.get("jwt_token")
  )) as ModelCard;

  redirect(
    301,
    `/opsml/${getRegistryPath(registryType)}/card/${metadata.space}/${
      metadata.name
    }/${metadata.version}/card`
  );
};
