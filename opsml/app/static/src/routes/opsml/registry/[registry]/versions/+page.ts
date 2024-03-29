import { type metadataRequest, type ModelMetadata } from "$lib/scripts/types";

/** @type {import('./$types').PageLoad} */
export async function load({ fetch, params, url }) {
  let name: string = url.searchParams.get("name")!;
  let repository: string = url.searchParams.get("repository")!;
  let version = url.searchParams.get("version");
  let registry = params.registry.replace(/s+$/, "");
  let path = params.registry;

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

  return {
    registry: registry,
    repository: repository,
    name: name,
    metadata: res,
    path: path,
  };
}

/** @type {import('./$types').EntryGenerator} */
export function entries() {
  return [{ registry: "data" }, { registry: "models" }];
}
