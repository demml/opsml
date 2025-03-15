export interface FileTreeNode {
  name: string;
  created_at: string;
  object_type: string;
  size: number;
  path: string;
}
export interface FileTreeResponse {
  files: FileTreeNode[];
}
