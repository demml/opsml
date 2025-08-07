export const ssr = false;

import type { PageLoad } from "./$types";
import { getFileTree } from "$lib/components/files/utils";
import { getRegistryTableName } from "$lib/utils";

export const load: PageLoad = async ({ parent }) => {
  const { metadata, registry, registryPath } = await parent();
  console.log("Loading files for metadata:", metadata);

  let tableName = getRegistryTableName(registry);
  let basePath = `${tableName}/${metadata.space}/${metadata.name}/v${metadata.version}`;

  let fileTree = await getFileTree(basePath);

  return { fileTree, previousPath: basePath, isRoot: true, registryPath };
};
