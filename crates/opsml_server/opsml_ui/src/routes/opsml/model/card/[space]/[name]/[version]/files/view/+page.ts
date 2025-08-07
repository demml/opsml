export const ssr = false;
export const prerender = false;

import type { PageLoad } from "./$types";
import { getRawFile } from "$lib/components/files/utils";

export const load: PageLoad = async ({ parent, url }) => {
  const { metadata, registryType, registryPath } = await parent();
  const viewPath = (url as URL).searchParams.get("path") as string;

  let rawFile = await getRawFile(viewPath, metadata.uid, registryPath);
  let splitPath = viewPath.split("/");

  return { rawFile, viewPath, splitPath };
};
