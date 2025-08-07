export const ssr = false;
export const prerender = false;

import type { PageLoad } from "./$types";
import { getFileTree } from "$lib/components/files/utils";
import { getRegistryTableName } from "$lib/utils";

export const load: PageLoad = async ({ parent, params }) => {
  let slug = params.file as string;

  // split slug with '/'
  let slugs = slug.split("/");

  const { metadata, registryPath, registryType } = await parent();

  let tableName = getRegistryTableName(registryType);
  let basePath = `${tableName}/${metadata.space}/${metadata.name}/v${metadata.version}`;

  // join all but the last element of the slugs to get the previous path without final "/"
  let previousPath = `/opsml/${registryPath}/card/${metadata.space}/${
    metadata.name
  }/${metadata.version}/files/${slugs
    .slice(0, slugs.length - 1)
    .join("/")}`.replace(/\/$/, "");

  // add the rest of the slugs to the basePath
  basePath = `${basePath}/${slugs.join("/")}`;

  let fileTree = await getFileTree(basePath);

  return { fileTree, previousPath, isRoot: false, registryPath };
};
