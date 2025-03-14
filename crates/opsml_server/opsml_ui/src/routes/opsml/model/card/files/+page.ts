export const ssr = false;

import { opsmlClient } from "$lib/components/api/client.svelte";
import type { PageLoad } from "./$types";
import { getFileInfo, separateFiles } from "$lib/components/files/utils";
import { getRegistryTableName } from "$lib/utils";

export const load: PageLoad = async ({ parent, url }) => {
  await opsmlClient.validateAuth(true);

  const { metadata, registry, readme, registryPath } = await parent();
  let tableName = getRegistryTableName(registry);
  let rPath = `${tableName}/${metadata.repository}/${metadata.name}/v${metadata.version}`;

  let fileInfo = await getFileInfo(rPath);

  const { currentPathFiles, directories } = separateFiles(fileInfo.files);

  return { currentPathFiles, directories };
};
