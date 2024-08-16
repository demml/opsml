import { type Files, type FileSetup, RegistryName } from "$lib/scripts/types";
import { calculateTimeBetween, setupFiles } from "$lib/scripts/utils";

const opsmlRoot: string = `opsml-root:/${RegistryName.Run}`;

/** @type {import('./$types').PageLoad} */
export async function load({ fetch, params, url }) {
  const name: string = url.searchParams.get("name")!;
  const repository: string = url.searchParams.get("repository")!;
  const version = url.searchParams.get("version");
  const subdir: string | null = url.searchParams.get("subdir");
  const registry = "run";

  const basePath = `${opsmlRoot}/${repository}/${name}/v${version}`;

  let setup: FileSetup = await setupFiles(
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
