import type { RegistryType } from "$lib/utils";

export interface FileTreeNode {
  name: string;
  created_at: string;
  object_type: string;
  size: number;
  path: string;
  suffix: string;
}
export interface FileTreeResponse {
  files: FileTreeNode[];
}

export enum AcceptableSuffix {
  MD = "md",
  TIFF = "tiff",
  JSON = "json",
  JSONL = "jsonl",
  YAML = "yaml",
  YML = "yml",
  SQL = "sql",
  TXT = "txt",
  JPEG = "jpeg",
  JPG = "jpg",
  PNG = "png",
  GIFF = "giff",
  PYTHON = "py",
}

export interface RawFile {
  content: string;
  suffix: string;
  mime_type: string;
}

export interface RawFileRequest {
  uid: string;
  path: string;
  registry_type: RegistryType;
}
