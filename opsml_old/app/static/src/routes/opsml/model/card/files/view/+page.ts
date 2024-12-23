import { type FileView } from "$lib/scripts/types";
import { CommonPaths } from "$lib/scripts/types";
import { apiHandler } from "$lib/scripts/apiHandler";
import { RegistryName } from "$lib/scripts/types";

const opsmlRoot: string = `opsml-root:/${RegistryName.Model}`;

/** @type {import('./$types').PageLoad} */
export async function load({ url }) {
  const name = (url as URL).searchParams.get("name") as string | undefined;
  const repository = (url as URL).searchParams.get("repository") as
    | string
    | undefined;
  const version = (url as URL).searchParams.get("version") as
    | string
    | undefined;

  const path = (url as URL).searchParams.get("path");
  const filePath = atob(path!);

  const displayPath = filePath
    .replace(opsmlRoot, "")
    .split("/")
    .filter(Boolean);

  const viewData = (await apiHandler
    .get(
      `${CommonPaths.FILES_VIEW}?${new URLSearchParams({
        path: filePath,
      }).toString()}`
    )
    .then((res) => res.json())) as FileView;

  return {
    viewData: viewData,
    cardName: name,
    repository: repository,
    version: version,
    displayPath: displayPath,
  };
}
