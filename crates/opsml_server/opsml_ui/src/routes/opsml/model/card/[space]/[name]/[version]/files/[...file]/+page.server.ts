import type { PageServerLoad } from "./$types";
import { getFileTree } from "$lib/server/card/files/utils";
import { getRegistryPath, getRegistryTableName } from "$lib/utils";

export const load: PageServerLoad = async ({ parent, params, fetch }) => {
  let slug = params.file as string;

  // split slug with '/'
  let slugs = slug.split("/");

  const { metadata, registryType } = await parent();

  let tableName = getRegistryTableName(registryType);
  let basePath = `${tableName}/${metadata.space}/${metadata.name}/v${metadata.version}`;

  // join all but the last element of the slugs to get the previous path without final "/"
  let previousPath = `/opsml/${getRegistryPath(registryType)}/card/${
    metadata.space
  }/${metadata.name}/${metadata.version}/files/${slugs
    .slice(0, slugs.length - 1)
    .join("/")}`.replace(/\/$/, "");

  // add the rest of the slugs to the basePath
  basePath = `${basePath}/${slugs.join("/")}`;

  let fileTree = await getFileTree(basePath, fetch);

  return { fileTree, previousPath, isRoot: false };
};
