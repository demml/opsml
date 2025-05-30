export interface CreateSpaceRequest {
  space: string;
}

export interface CreateSpaceResponse {
  created: boolean;
}

export interface DeleteSpaceResponse {
  deleted: boolean;
}

export interface SpaceRecord {
  space: string;
  description: string;
}

export interface SpaceRecordResponse {
  spaces: SpaceRecord[];
}

export interface SpaceStats {
  space: string;
  model_count: number;
  data_count: number;
  prompt_count: number;
  experiment_count: number;
}

export interface SpaceStatsResponse {
  stats: SpaceStats[];
}
