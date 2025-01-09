import { type FileSystemAttr, type FileSetup } from "$lib/scripts/types";
import { calculateTimeBetween, setupFiles } from "$lib/scripts/utils";

export async function setupFileAttr(
  basePath: string,
  name: string,
  repository: string,
  version: string,
  registry: string,
  subdir?: string
): Promise<FileSystemAttr> {
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
    baseRedirectPath: `/opsml/${registry}/card/files?name=${name}&repository=${repository}&version=${version}`,
  };
}
