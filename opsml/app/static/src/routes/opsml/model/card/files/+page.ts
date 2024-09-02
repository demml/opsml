import { RegistryName } from "$lib/scripts/types";
import { setupFileAttr } from "$lib/scripts/filesystem.js";

const opsmlRoot: string = `opsml-root:/${RegistryName.Model}`;

/** @type {import('./$types').PageLoad} */
export async function load({ fetch, params, url }) {
  const name = (url as URL).searchParams.get("name") as string | undefined;
  const repository = (url as URL).searchParams.get("repository") as
    | string
    | undefined;
  const version = (url as URL).searchParams.get("version") as
    | string
    | undefined;
  const subdir = (url as URL).searchParams.get("subdir") as string | undefined;
  const registry = "model";

  const basePath = `${opsmlRoot}/${repository}/${name}/v${version}`;

  return setupFileAttr(
    basePath,
    name!,
    repository!,
    version!,
    registry,
    subdir
  );
}
