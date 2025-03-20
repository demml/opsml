import { opsmlClient } from "$lib/components/api/client.svelte";
import { RoutePaths } from "$lib/components/api/routes";
import type { ModelCard } from "../card/card_interfaces/modelcard";

export async function getDriftProfiles(
  metadata: ModelCard
): Promise<FileTreeResponse> {
  const params = {
    path: path,
  };

  const response = await opsmlClient.get(RoutePaths.FILE_TREE, params);
  return (await response.json()) as FileTreeResponse;
}
