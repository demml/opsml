import type { PageServerLoad } from "./$types";
import { getFileTree, getRawFile } from "$lib/server/card/files/utils";
import { getRegistryTableName } from "$lib/utils";

export const load: PageServerLoad = async ({ parent, fetch, url }) => {
  const { metadata, registryType } = await parent();

  const tableName = getRegistryTableName(registryType);
  const basePath = `${tableName}/${metadata.space}/${metadata.name}/v${metadata.version}`;

  const fileTree = await getFileTree(fetch, basePath);

  const viewPath = url.searchParams.get("view");
  let rawFile = null;
  if (viewPath) {
    rawFile = await getRawFile(fetch, viewPath, metadata.uid, registryType);
  }

  return { fileTree, basePath, viewPath, rawFile };
};
