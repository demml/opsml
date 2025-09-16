export interface Card {
  name: string;
  space: string;
  version: string;
  uid: string;
  registry_type: string;
  alias: string;
}

export interface CardList {
  cards: Card[];
}

export interface ServiceCard {
  name: string;
  space: string;
  version: string;
  uid: string;
  created_at: string; // ISO datetime string
  cards: CardList;
  opsml_version: string;
  app_env: string;
  is_card: boolean;
  registry_type: string;
  experimentcard_uid?: string;
}
