import {
  type FileExists,
  type CardRequest,
  type CardResponse,
  type DataCardMetadata,
  RegistryName,
} from "$lib/scripts/types";

import { listCards, getDataCard } from "$lib/scripts/utils";

export const ssr = false;
const opsmlRoot: string = `opsml-root:/${RegistryName.Data}`;

/** @type {import('./$types').PageLoad} */
export async function load({ fetch, params, url }) {
  const name: string = url.searchParams.get("name")!;
  const repository: string = url.searchParams.get("repository")!;
  const version: string | null = url.searchParams.get("version");
  const uid: string | null = url.searchParams.get("uid");
  const registry = "data";

  /** get last path from url */
  const tab = url.pathname.split("/").pop();

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
  const markdown: FileExists = await fetch(
    `/opsml/files/exists?path=${markdownPath}`,
  ).then((res) => res.json());

  let readme: string = "";
  if (markdown.exists) {
    // fetch markdown
    const viewData = await fetch(`/opsml/files/view?path=${markdownPath}`).then(
      (res) => res.json(),
    );

    readme = viewData.content.content;
  }

  // get datacard
  const dataCard: DataCardMetadata = await getDataCard(cardReq);

  return {
    registry,
    repository: selectedCard.repository,
    name: selectedCard.name,
    hasReadme: markdown.exists,
    card: cards.cards[0],
    readme,
    metadata: dataCard,
    tabSet: tab,
  };
}
