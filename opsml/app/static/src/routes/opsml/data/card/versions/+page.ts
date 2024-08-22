import { getRegistryPage } from "$lib/scripts/utils.js";
import { type CardRequest, type CardResponse } from "$lib/scripts/types";
import { listCards } from "$lib/scripts/utils";

/** @type {import('./$types').PageLoad} */
export async function load({ fetch, params, url }) {
  const name = (url as URL).searchParams.get("name") as string | undefined;
  const repository = (url as URL).searchParams.get("repository") as
    | string
    | undefined;
  const registry = (url as URL).searchParams.get("registry") as
    | string
    | undefined;

  const registryPage = await getRegistryPage(
    registry!,
    undefined,
    repository,
    name,
    0
  );

  const cardReq: CardRequest = {
    repository: repository,
    name: name,
    registry_type: registry!,
    page: 0,
  };

  // get card info
  const cards: CardResponse = await listCards(cardReq);

  return {
    nbr_cards: registryPage.page[0][2],
    name,
    repository,
    registry,
    cards,
  };
}
