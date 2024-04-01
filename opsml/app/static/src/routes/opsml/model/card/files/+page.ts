import {
  type metadataRequest,
  type ModelMetadata,
  type FileExists,
  type Files,
  RegistryName,
} from "$lib/scripts/types";
import { calculateTimeBetween } from "$lib/scripts/utils";

const opsmlRoot: string = `opsml-root:/${RegistryName.Model}`;

/** @type {import('./$types').PageLoad} */
export async function load({ fetch, params, url }) {
  let name: string = url.searchParams.get("name")!;
  let repository: string = url.searchParams.get("repository")!;
  let version = url.searchParams.get("version");
  let subdir: string | undefined = url.searchParams.get("subdir");
  let registry = "model";

  let filePath = `${opsmlRoot}/${repository}/${name}/v${version}`;

  if (subdir) {
    urlPath = `/opsml/files/list/info?path=${filePath}&subdir=${subdir}`;
  } else {
    urlPath = `/opsml/files/list/info?path=${filePath}`;
  }

  console.log(urlPath);

  let fileInfo: Files = await fetch(urlPath).then((res) => res.json());

  return {
    files: fileInfo,
    name,
    repository,
    version,
    registry,
    subdir,
    modifiedAt: calculateTimeBetween(fileInfo.mtime),
    basePath: `${opsmlRoot}/${repository}/${name}/v${version}`,
  };
}
