export const ssr = false;
export const prerender = false;

import type { PageLoad } from "./$types";
import { getRawFile } from "$lib/components/files/utils";
import { validateUserOrRedirect } from "$lib/components/user/user.svelte";
import { RegistryType } from "$lib/utils";

export const load: PageLoad = async ({ parent, url }) => {
  await validateUserOrRedirect();
  const { metadata } = await parent();
  const viewPath = (url as URL).searchParams.get("path") as string;

  let rawFile = await getRawFile(viewPath, metadata.uid, RegistryType.Model);
  let splitPath = viewPath.split("/");

  return { rawFile, viewPath, splitPath };
};
