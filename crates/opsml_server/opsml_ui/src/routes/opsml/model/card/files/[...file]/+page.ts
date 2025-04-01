export const ssr = false;
export const prerender = false;

import { opsmlClient } from "$lib/components/api/client.svelte";
import type { PageLoad } from "./$types";
import { getFileTree } from "$lib/components/files/utils";
import { getRegistryTableName } from "$lib/utils";

export const load: PageLoad = async ({ parent, params }) => {
  await opsmlClient.validateAuth(true);

  let slug = params.file as string;

  // split slug with '/'
  let slugs = slug.split("/");

  const { metadata, registry, registryPath } = await parent();

  let tableName = getRegistryTableName(registry);
  let basePath = `${tableName}/${metadata.repository}/${metadata.name}/v${metadata.version}`;

  // join all but the last element of the slugs to get the previous path without final "/"
  let previousPath = `/opsml/${registryPath}/card/files/${slugs
    .slice(0, slugs.length - 1)
    .join("/")}`.replace(/\/$/, "");

  // add params to previousPath
  previousPath = `${previousPath}?repository=${metadata.repository}&name=${metadata.name}&version=${metadata.version}`;

  // add the rest of the slugs to the basePath
  basePath = `${basePath}/${slugs.join("/")}`;

  let fileTree = await getFileTree(basePath);

  return { fileTree, previousPath, isRoot: false, registryPath };
};
