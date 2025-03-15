import { RegistryType } from "$lib/utils";

// Enums first
export enum DataType {
  Base = "Base",
  Arrow = "Arrow",
  Numpy = "Numpy",
  Pandas = "Pandas",
  Polars = "Polars",
  Sql = "Sql",
  Torch = "Torch",
}

export enum DataInterfaceType {
  Base = "Base",
  Arrow = "Arrow",
  Numpy = "Numpy",
  Pandas = "Pandas",
  Polars = "Polars",
  Sql = "Sql",
  Torch = "Torch",
}

// Enums
export enum Inequality {
  Equal = "Equal",
  GreaterThan = "GreaterThan",
  GreaterThanEqual = "GreaterThanEqual",
  LesserThan = "LesserThan",
  LesserThanEqual = "LesserThanEqual",
}

export enum ColType {
  Builtin = "Builtin",
  Timestamp = "Timestamp",
}

// Column value types
export type ColValType =
  | { String: string }
  | { Float: number }
  | { Int: number }
  | { Timestamp: number };

// Split types
export interface ColumnSplit {
  column_name: string;
  column_value: ColValType;
  column_type: ColType;
  inequality: Inequality;
}

export interface StartStopSplit {
  start: number;
  stop: number;
}

export interface IndiceSplit {
  indices: number[];
}

export interface DataSplit {
  label: string;
  column_split?: ColumnSplit;
  start_stop_split?: StartStopSplit;
  indice_split?: IndiceSplit;
}

export interface DataSplits {
  splits: DataSplit[];
}

// Example usage of these types:

// Feature schema interfaces
export interface Feature {
  feature_type: string;
  shape: number[];
  extra_args: Record<string, string>;
}

export interface FeatureSchema {
  items: Record<string, Feature>;
}

// Interface metadata types
export interface DataInterfaceSaveMetadata {
  data_uri: string;
  sql_uri?: string;
  data_profile_uri?: string;
  extra?: Record<string, any>;
  save_kwargs?: Record<string, any>;
}

export interface SqlLogic {
  queries: Record<string, string>;
}

export interface DataSplit {
  label: string;
  column_split?: ColumnSplit;
  start_stop_split?: StartStopSplit;
  indice_split?: IndiceSplit;
}

export interface DataSplits {
  splits: DataSplit[];
}

export interface DependentVars {
  column_names: string[];
  column_indices: number[];
  is_idx: boolean;
}

export interface DataInterfaceMetadata {
  save_metadata: DataInterfaceSaveMetadata;
  schema: FeatureSchema;
  extra_metadata: Record<string, string>;
  sql_logic: SqlLogic;
  interface_type: DataInterfaceType;
  data_splits: DataSplits;
  dependent_vars: DependentVars;
  data_type: DataType;
  data_specific_metadata: any;
}

// Main DataCard interfaces
export interface DataCardMetadata {
  schema: FeatureSchema;
  experimentcard_uid?: string;
  auditcard_uid?: string;
  interface_metadata: DataInterfaceMetadata;
}

export interface DataCard {
  name: string;
  repository: string;
  version: string;
  uid: string;
  tags: string[];
  metadata: DataCardMetadata;
  registry_type: RegistryType.Data;
  app_env: string;
  created_at: string; // ISO datetime string
  is_card: boolean;
}
