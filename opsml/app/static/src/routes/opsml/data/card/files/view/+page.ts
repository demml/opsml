import { type FileView } from "$lib/scripts/types";

/** @type {import('./$types').PageLoad} */
export async function load({ fetch, params, url }) {
  const filePath = atob(url.searchParams.get("path")!);

  const viewData: FileView = await fetch(
    `/opsml/files/view?path=${filePath}`,
  ).then((res) => res.json());

  return viewData;
}
