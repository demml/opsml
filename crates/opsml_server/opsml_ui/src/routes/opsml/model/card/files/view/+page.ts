export const ssr = false;
export const prerender = false;

import { opsmlClient } from "$lib/components/api/client.svelte";
import type { PageLoad } from "./$types";
import { getRawFile } from "$lib/components/files/utils";

export const load: PageLoad = async ({ parent, url }) => {
  await opsmlClient.validateAuth(true);
  const { metadata, registry, registryPath } = await parent();
  const viewPath = (url as URL).searchParams.get("path") as string;

  let rawFile = await getRawFile(viewPath, metadata.uid, registry);
  let splitPath = viewPath.split("/");

  return { rawFile, viewPath, splitPath };
};
