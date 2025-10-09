export const ssr = false;
export const prerender = false;

import type { PageLoad } from "./$types";
import { getFileTree } from "$lib/components/files/utils";
import { getRegistryPath, getRegistryTableName } from "$lib/utils";
import { validateUserOrRedirect } from "$lib/components/user/user.svelte";

export const load: PageLoad = async ({ parent, params }) => {
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

  let fileTree = await getFileTree(basePath);

  return { fileTree, previousPath, isRoot: false, registryType };
};
