import { createOpsmlClient } from "$lib/server/api/opsmlClient";
import { RoutePaths } from "$lib/components/api/routes";
import type {
  FileTreeResponse,
  RawFile,
  RawFileRequest,
} from "$lib/components/files/types";
import type { RegistryType } from "$lib/utils";

export async function getFileTree(
  fetch: typeof globalThis.fetch,
  path: string
): Promise<FileTreeResponse> {
  const params = {
    path: path,
  };

  const response = await createOpsmlClient(fetch).get(
    RoutePaths.FILE_TREE,
    params
  );
  return (await response.json()) as FileTreeResponse;
}
export async function getRawFile(
  fetch: typeof globalThis.fetch,
  path: string,
  uid: string,
  registry_type: RegistryType
): Promise<RawFile> {
  const body: RawFileRequest = {
    path: path,
    uid: uid,
    registry_type: registry_type,
  };

  const response = await createOpsmlClient(fetch).post(
    RoutePaths.FILE_CONTENT,
    body
  );
  return (await response.json()) as RawFile;
}
