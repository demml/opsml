import { RegistryName, type FileSetup } from "$lib/scripts/types";
import { setupFileAttr } from "$lib/scripts/filesystem.js";

const opsmlRoot: string = `opsml-root:/${RegistryName.Model}`;

/** @type {import('./$types').PageLoad} */
export async function load({ fetch, params, url }) {
  const name: string = (url as URL).searchParams.get("name");
  const repository: string = (url as URL).searchParams.get("repository");
  const version = (url as URL).searchParams.get("version")!;
  const subdir: string | null = (url as URL).searchParams.get("subdir");
  const registry = "model";

  const basePath = `${opsmlRoot}/${repository}/${name}/v${version}`;

  return setupFileAttr(basePath, name, repository, version, registry, subdir);
}
