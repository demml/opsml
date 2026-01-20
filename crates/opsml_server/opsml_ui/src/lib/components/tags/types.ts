export interface Tag {
  key: string;
  value: string;
}

export interface ScouterEntityIdTagsRequest {
  entity_type: string;
  tags: Tag[];
  match_all: boolean;
}

export interface ScouterEntityIdResponse {
  entity_id: string[];
}
