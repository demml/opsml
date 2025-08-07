export const ssr = false;

import type { PageLoad } from "./$types";
import { getFileTree } from "$lib/components/files/utils";
import { getRegistryTableName } from "$lib/utils";

export const load: PageLoad = async ({ parent }) => {
  const { metadata, registryPath, registryType } = await parent();

  let tableName = getRegistryTableName(registryType);
  let basePath = `${tableName}/${metadata.space}/${metadata.name}/v${metadata.version}`;

  let fileTree = await getFileTree(basePath);

  return { fileTree, previousPath: basePath, isRoot: true, registryPath };
};
