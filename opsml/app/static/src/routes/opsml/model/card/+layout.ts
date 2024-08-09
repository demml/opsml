import {
  type ModelMetadata,
  type CardRequest,
  type CardResponse,
  type Readme,
  RegistryName,
} from "$lib/scripts/types";

import { listCards, getReadme, getModelMetadata } from "$lib/scripts/utils";

export const ssr = false;
const opsmlRoot: string = `opsml-root:/${RegistryName.Model}`;

/** @type {import('./$types').LayoutLoad} */
export async function load({ fetch, params, url }) {
  const name: string = url.searchParams.get("name")!;
  const repository: string = url.searchParams.get("repository")!;
  const version = url.searchParams.get("version");
  const uid: string | null = url.searchParams.get("uid");
  const registry = "model";

  /** get last path from url */
  const tab = url.pathname.split("/").pop();

  let metadata: ModelMetadata = await getModelMetadata(
    uid,
    name,
    repository,
    version
  );

  // check if markdown exists
  const markdownPath = `${opsmlRoot}/${metadata.model_repository}/${metadata.model_name}/README.md`;

  let readme: Readme = await getReadme(markdownPath);

  const cardReq: CardRequest = {
    name,
    repository,
    version: metadata.model_version,
    registry_type: registry,
  };

  // get card info
  const cards: CardResponse = await listCards(cardReq);
  let selectedCard = cards.cards[0];

  return {
    registry,
    repository: metadata.model_repository,
    name: metadata.model_name,
    metadata: metadata,
    hasReadme: readme.exists,
    card: selectedCard,
    readme: readme.readme,
    tabSet: tab,
    version: metadata.model_version,
  };
}
