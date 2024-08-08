import {
  type metadataRequest,
  type ModelMetadata,
  type FileExists,
  type CardRequest,
  type CardResponse,
  type Card,
  RegistryName,
} from "$lib/scripts/types";

import { listCards } from "$lib/scripts/utils";

export const ssr = false;
const opsmlRoot: string = `opsml-root:/${RegistryName.Model}`;

/** @type {import('./$types').LayoutLoad} */
export async function load({ fetch, params, url }) {
  const name: string = url.searchParams.get("name")!;
  const repository: string = url.searchParams.get("repository")!;
  const version = url.searchParams.get("version");
  const uid: string | null = url.searchParams.get("uid");
  const registry = "model";
  let metaAttr: metadataRequest;

  console.log("hover");

  /** get last path from url */
  const tab = url.pathname.split("/").pop();

  if (uid !== null) {
    metaAttr = {
      uid,
    };
  } else {
    metaAttr = {
      name,
      repository,
    };

    if (version) {
      metaAttr.version = version;
    }
  }

  const res: ModelMetadata = await fetch("/opsml/models/metadata", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(metaAttr),
  }).then((res) => res.json());

  // check if markdown exists
  const markdownPath = `${opsmlRoot}/${res.model_repository}/${res.model_name}/README.md`;
  const markdown: FileExists = await fetch(
    `/opsml/files/exists?path=${markdownPath}`
  ).then((res) => res.json());

  let readme: string = "";
  if (markdown.exists) {
    // fetch markdown
    const viewData = await fetch(`/opsml/files/view?path=${markdownPath}`).then(
      (res) => res.json()
    );

    readme = viewData.content.content;
  }

  const cardReq: CardRequest = {
    name,
    repository,
    version: res.model_version,
    registry_type: registry,
  };

  // get card info
  const cards: CardResponse = await listCards(cardReq);
  let selectedCard = cards.cards[0];

  return {
    registry,
    repository: repository,
    name: name,
    metadata: res,
    hasReadme: markdown.exists,
    card: selectedCard,
    readme,
    tabSet: tab,
    version: res.model_version,
  };
}
