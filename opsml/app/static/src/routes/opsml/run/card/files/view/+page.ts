import { type FileView } from "$lib/scripts/types";
import { CommonPaths } from "$lib/scripts/types";
import { apiHandler } from "$lib/scripts/apiHandler";

/** @type {import('./$types').PageLoad} */
export async function load({ fetch, params, url }) {
  const path = (url as URL).searchParams.get("path");
  const filePath = atob(path!);

  const viewData = (await apiHandler
    .get(
      `${CommonPaths.FILES_VIEW}?${new URLSearchParams({
        path: filePath,
      }).toString()}`
    )
    .then((res) => res.json())) as FileView;

  return viewData;
}
