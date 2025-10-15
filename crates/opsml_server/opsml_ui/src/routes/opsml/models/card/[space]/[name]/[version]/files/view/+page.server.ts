import type { PageServerLoad } from "./$types";
import { getRawFile } from "$lib/server/card/files/utils";
import { RegistryType } from "$lib/utils";

export const load: PageServerLoad = async ({ parent, url, fetch }) => {
  const { metadata } = await parent();
  const viewPath = (url as URL).searchParams.get("path") as string;

  let rawFile = await getRawFile(
    fetch,
    viewPath,
    metadata.uid,
    RegistryType.Model
  );
  let splitPath = viewPath.split("/");

  return { rawFile, viewPath, splitPath };
};
