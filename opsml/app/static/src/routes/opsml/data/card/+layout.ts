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
export async function load({ url }) {
  const name = (url as URL).searchParams.get("name") as string | undefined;
  const repository = (url as URL).searchParams.get("repository") as
    | string
    | undefined;
  const version = (url as URL).searchParams.get("version") as
    | string
    | undefined;
  const uid = (url as URL).searchParams.get("uid") as string | undefined;
  const registry = "data";

  /** get last path from url */
  const tab = (url as URL).pathname.split("/").pop();

  const cardReq: CardRequest = {
    name,
    repository,
    registry_type: registry,
  };

  if (uid) {
    cardReq.uid = uid;
  }

  if (version) {
    cardReq.version = version;
  }

  // get card info
  const cards: CardResponse = await listCards(cardReq);
  const selectedCard = cards.cards[0];

  // check if markdown exists
  const markdownPath = `${opsmlRoot}/${selectedCard.repository}/${selectedCard.name}/README.md`;

  const readme: Readme = await getReadme(markdownPath);

  // get datacard
  //const dataCard: DataCardMetadata = await getDataCard(cardReq);

  const fakeData: DataCardMetadata = {
    name: "Fake Data",
    repository: "fake",
    version: "1.0.0",
    uid: "fake",
    contact: "hello",
    interface_type: "PandasData",
    data_splits: undefined,
    feature_map: undefined,
    has_profile: false,
    sql_logic: undefined,
  };

  return {
    registry,
    repository: selectedCard.repository,
    name: selectedCard.name,
    hasReadme: readme.exists,
    card: cards.cards[0],
    readme: readme.readme,
    metadata: fakeData,
    tabSet: tab,
  };
}
