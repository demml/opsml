export const ssr = false;

import { opsmlClient } from "$lib/components/api/client.svelte";
import type { PageLoad } from "./$types";
import { getFileTree } from "$lib/components/files/utils";
import { getRegistryTableName } from "$lib/utils";

export const load: PageLoad = async ({ parent }) => {
  await opsmlClient.validateAuth(true);

  const { metadata, registry } = await parent();

  let tableName = getRegistryTableName(registry);
  let basePath = `${tableName}/${metadata.repository}/${metadata.name}/v${metadata.version}`;

  let fileTree = await getFileTree(basePath);

  return { fileTree, previousPath: basePath, isRoot: true };
};
