import { RegistryName, type FileSetup } from "$lib/scripts/types";
import { calculateTimeBetween, setupFiles } from "$lib/scripts/utils";

const opsmlRoot: string = `opsml-root:/${RegistryName.Data}`;

/** @type {import('./$types').PageLoad} */
export async function load({ fetch, params, url }) {
  const name: string = (url as URL).searchParams.get("name");
  const repository: string = (url as URL).searchParams.get("repository");
  const version = (url as URL).searchParams.get("version");
  const subdir: string | null = (url as URL).searchParams.get("subdir");
  const registry = "data";

  const basePath = `${opsmlRoot}/${repository}/${name}/v${version}`;

  const setup: FileSetup = await setupFiles(
    basePath,
    repository,
    name,
    version,
    subdir
  );

  return {
    files: setup.fileInfo,
    name,
    repository,
    version,
    registry,
    subdir,
    modifiedAt: calculateTimeBetween(setup.fileInfo.mtime),
    basePath,
    displayPath: setup.displayPath,
    prevPath: setup.prevPath,
  };
}
