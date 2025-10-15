import type { PageServerLoad } from "./$types";
import { getFileTree } from "$lib/server/card/files/utils";
import { getRegistryTableName } from "$lib/utils";

export const load: PageServerLoad = async ({ parent, fetch }) => {
  const { metadata, registryType } = await parent();

  let tableName = getRegistryTableName(registryType);
  let basePath = `${tableName}/${metadata.space}/${metadata.name}/v${metadata.version}`;

  let fileTree = await getFileTree(fetch, basePath);

  return { fileTree, previousPath: basePath, isRoot: true };
};
