type record = [string, string, number, number, number, number];

export interface registryPage {
  page: record[];
}

export interface registryStats {
  nbr_names: number;
  nbr_versions: number;
  nbr_repos: number;
}

export interface repositories {
  repositories: string[];
}

export interface metadataRequest {
  repository: string;
  name: string;
  version?: string;
}

export interface DataSchema {
  data_type: string;
  input_features: any;
  ouput_features: any;
  onnx_input_features: any;
  onnx_output_features: any;
  onnx_data_type: string | undefined;
  onnx_version: string | undefined;
}

export interface ModelMetadata {
  model_name: string;
  model_class: string;
  model_type: string;
  model_interface: string;
  onnx_uri: string;
  onnx_version: string;
  model_uri: string;
  model_version: string;
  model_repository: string;
  opsml_version: string;
  data_schema: DataSchema;
  preprocessor_uri?: string;
  preprocessor_name?: string;
  quantized_model_uri?: string;
  tokenizer_uri?: string;
  tokenizer_name?: string;
  feature_extractor_uri?: string;
  feature_extractor_name?: string;
}

export enum RegistryName {
  Model = "OPSML_MODEL_REGISTRY",
  Data = "OPSML_DATA_REGISTRY",
}

export interface FileExists {
  exists: boolean;
}

export interface FileInfo {
  name: string;
  size: number;
  type: string;
  created: number;
  islink: boolean;
  mode: number;
  uid: number;
  gid: number;
  mtime: number;
  ino: number;
  nlink: number;
}

export interface Files {
  files: FileInfo[];
  mtime: number;
}
