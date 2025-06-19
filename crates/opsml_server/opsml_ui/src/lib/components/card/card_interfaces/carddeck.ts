import type { RegistryType } from "$lib/utils";

export interface Card {
  name: string;
  space: string;
  version: string;
  uid: string;
  registry_type: RegistryType;
  alias: string;
}

export interface CardList {
  cards: Card[];
}

export interface CardDeck {
  name: string;
  space: string;
  version: string;
  uid: string;
  created_at: string; // ISO datetime string
  cards: CardList;
  opsml_version: string;
  app_env: string;
  is_card: boolean;
  registry_type: RegistryType.Deck;
  experimentcard_uid?: string;
}
