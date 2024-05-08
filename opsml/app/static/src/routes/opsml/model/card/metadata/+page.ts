import {
  type metadataRequest,
  type ModelMetadata,
  RegistryName,
} from "$lib/scripts/types";

const opsmlRoot: string = `opsml-root:/${RegistryName.Model}`;

/** @type {import('./$types').PageLoad} */
export async function load({ fetch, params, url }) {
  const name: string = url.searchParams.get("name")!;
  const repository: string = url.searchParams.get("repository")!;
  const version: string = url.searchParams.get("version")!;

  // get model metadata
  const metaAttr: metadataRequest = {
    name,
    repository,
    version,
  };

  const res: ModelMetadata = await fetch("/opsml/models/metadata", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(metaAttr),
  }).then((res) => res.json());

  return {
    metadata: res,
  };
}
