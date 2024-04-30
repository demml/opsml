import {
  type metadataRequest,
  type ModelMetadata,
  type FileExists,
  type Files,
  RegistryName,
} from "$lib/scripts/types";
import { calculateTimeBetween } from "$lib/scripts/utils";

const opsmlRoot: string = `opsml-root:/${RegistryName.Run}`;

/** @type {import('./$types').PageLoad} */
export async function load({ fetch, params, url }) {
  const name: string = url.searchParams.get("name")!;
  const repository: string = url.searchParams.get("repository")!;
  const version = url.searchParams.get("version");
  const subdir: string | null = url.searchParams.get("subdir");
  const registry = "run";

  const basePath = `${opsmlRoot}/${repository}/${name}/v${version}`;

  let urlPath = `/opsml/files/list/info?path=${basePath}`;
  let displayPath = [repository, name, `v${version}`];
  let prevPath: string = basePath;

  if (subdir !== null) {
    urlPath = `${urlPath}&subdir=${subdir}`;

    // split the subdir path
    displayPath = displayPath.concat(subdir.split("/"));

    const subPath = subdir.split("/");
    const prevDir = subPath.slice(0, subPath.length - 1).join("/");
    prevPath = `${basePath}/${prevDir}`;
  }

  const fileInfo: Files = await fetch(urlPath).then((res) => res.json());

  return {
    files: fileInfo,
    name,
    repository,
    version,
    registry,
    subdir,
    modifiedAt: calculateTimeBetween(fileInfo.mtime),
    basePath,
    displayPath,
    prevPath,
  };
}
