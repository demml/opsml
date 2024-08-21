import {
  type CardRequest,
  type CardResponse,
  type DataCardMetadata,
  type Readme,
  RegistryName,
} from "$lib/scripts/types";

import { listCards, getDataCard, getReadme } from "$lib/scripts/utils";

export const ssr = false;
const opsmlRoot: string = `opsml-root:/${RegistryName.Data}`;

/** @type {import('./$types').PageLoad} */
export async function load({ fetch, params, url }) {
  const name: string = (url as URL).searchParams.get("name");
  const repository: string = (url as URL).searchParams.get("repository");
  const version: string | null = (url as URL).searchParams.get("version");
  const uid: string | null = (url as URL).searchParams.get("uid");
  const registry = "data";

  /** get last path from url */
  const tab = (url as URL).pathname.split("/").pop();

  const cardReq: CardRequest = {
    name,
    repository,
    registry_type: registry,
  };

  if (uid !== null) {
    cardReq.uid = uid;
  }

  if (version !== null) {
    cardReq.version = version;
  }

  // get card info
  const cards: CardResponse = await listCards(cardReq);
  const selectedCard = cards.cards[0];

  // check if markdown exists
  const markdownPath = `${opsmlRoot}/${selectedCard.repository}/${selectedCard.name}/README.md`;

  const readme: Readme = await getReadme(markdownPath);

  // get datacard
  const dataCard: DataCardMetadata = await getDataCard(cardReq);

  return {
    registry,
    repository: selectedCard.repository,
    name: selectedCard.name,
    hasReadme: readme.exists,
    card: cards.cards[0],
    readme: readme.readme,
    metadata: dataCard,
    tabSet: tab,
  };
}
