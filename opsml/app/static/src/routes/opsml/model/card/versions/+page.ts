import { getRegistryPage } from "$lib/scripts/registry_page";
import { type CardRequest, type CardResponse } from "$lib/scripts/types";
import { listCards } from "$lib/scripts/utils";

/** @type {import('./$types').PageLoad} */
export async function load({ fetch, params, url }) {
  const name: string = (url as URL).searchParams.get("name");
  const repository: string = (url as URL).searchParams.get("repository");
  const registry: string = (url as URL).searchParams.get("registry");

  const registryPage = await getRegistryPage(
    registry,
    undefined,
    repository,
    name,
    0
  );

  const cardReq: CardRequest = {
    name,
    repository,
    registry_type: registry,
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
