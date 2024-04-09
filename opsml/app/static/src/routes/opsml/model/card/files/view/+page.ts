import { type FileView } from "$lib/scripts/types";

/** @type {import('./$types').PageLoad} */
export async function load({ fetch, params, url }) {
  let filePath = atob(url.searchParams.get("path"));

  let viewData: FileView = await fetch(
    `/opsml/files/view?path=${filePath}`
  ).then((res) => res.json());

  console.log(viewData);

  return viewData;
}
