export interface FileNode {
  name: string;
  type: "file" | "directory";
  path: string;
  children?: FileNode[];
  isOpen?: boolean;
}

export interface FileInfo {
  name: string;
  size: number;
  object_type: string;
  created: string;
  suffix: string;
}
export interface ListFileInfoResponse {
  files: FileInfo[];
}

export interface DirectoryInfo {
  name: string;
  created: string;
}
