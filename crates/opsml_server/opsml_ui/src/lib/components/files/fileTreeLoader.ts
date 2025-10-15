import { getFileTree } from "$lib/server/card/files/utils";
import { getRegistryPath, getRegistryTableName } from "$lib/utils";

/**
 * Loads file tree and navigation metadata for a card file route.
 * Encapsulates slug parsing, registry path construction, and file tree retrieval.
 * @param parent - SvelteKit parent loader function
 * @param params - Route parameters
 * @param fetch - SvelteKit fetch function
 * @returns File tree, previous path, and root indicator
 */
export async function loadFileTree({
  parent,
  params,
  fetch,
}: {
  parent: () => Promise<{ metadata: any; registryType: string }>;
  params: { file: string };
  fetch: typeof globalThis.fetch;
}) {
  const slug = params.file as string;
  const slugs = slug.split("/");

  const { metadata, registryType } = await parent();

  // @ts-ignore
  const tableName = getRegistryTableName(registryType);
  let basePath = `${tableName}/${metadata.space}/${metadata.name}/v${metadata.version}`;

  // @ts-ignore
  const previousPath = `/opsml/${getRegistryPath(registryType)}/card/${
    metadata.space
  }/${metadata.name}/${metadata.version}/files/${slugs
    .slice(0, slugs.length - 1)
    .join("/")}`.replace(/\/$/, "");

  basePath = `${basePath}/${slugs.join("/")}`;

  const fileTree = await getFileTree(fetch, basePath);

  return { fileTree, previousPath, isRoot: false };
}
