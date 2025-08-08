export const ssr = false;
export const prerender = false;

import type { PageLoad } from "./$types";
import { getRawFile } from "$lib/components/files/utils";
import { validateUserOrRedirect } from "$lib/components/user/user.svelte";

export const load: PageLoad = async ({ parent, url }) => {
  const { metadata, registry } = await parent();
  await validateUserOrRedirect();
  const viewPath = (url as URL).searchParams.get("path") as string;

  let rawFile = await getRawFile(viewPath, metadata.uid, registry);
  let splitPath = viewPath.split("/");

  return { rawFile, viewPath, splitPath };
};
