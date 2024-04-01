import {
  type metadataRequest,
  type ModelMetadata,
  type FileExists,
  type Files,
  RegistryName,
} from "$lib/scripts/types";

const opsmlRoot: string = `opsml-root:/${RegistryName.Model}`;

/** @type {import('./$types').PageLoad} */
export async function load({ fetch, params, url }) {
  let name: string = url.searchParams.get("name")!;
  let repository: string = url.searchParams.get("repository")!;
  let version = url.searchParams.get("version");
  let registry = "model";

  // get file directory
  console.log(
    `/opsml/files/list/info?path=${opsmlRoot}/${repository}/${name}/v${version}`
  );

  let fileInfo: Files = fetch(
    `/opsml/files/list/info?path=${opsmlRoot}/${repository}/${name}/v${version}`
  ).then((res) => res.json());

  return { files: fileInfo };
}
