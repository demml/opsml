import {
  type metadataRequest,
  type ModelMetadata,
  type FileExists,
  RegistryName,
} from "$lib/scripts/types";

const opsmlRoot: string = `opsml-root:/${RegistryName.Model}`;

/** @type {import('./$types').PageLoad} */
export async function load({ fetch, params, url }) {
  let name: string = url.searchParams.get("name")!;
  let repository: string = url.searchParams.get("repository")!;
  let version = url.searchParams.get("version");
  let registry = "model";

  // get model metadata
  let metaAttr: metadataRequest = {
    name: name,
    repository: repository,
  };

  if (version) {
    metaAttr["version"] = version;
  }

  const res: ModelMetadata = await fetch("/opsml/models/metadata", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(metaAttr),
  }).then((res) => res.json());

  // check if markdown exists
  let markdownPath = `${opsmlRoot}/${res.model_repository}/${res.model_name}/README.md`;
  let markdown: FileExists = await fetch(
    `/opsml/files/exists?path=${markdownPath}`
  ).then((res) => res.json());

  return {
    registry: registry,
    repository: repository,
    name: name,
    metadata: res,
    hasReadme: markdown.exists,
  };
}
