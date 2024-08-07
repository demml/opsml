import {
  type metadataRequest,
  type ModelMetadata,
  type FileExists,
  type CardRequest,
  type CardResponse,
  RegistryName,
} from "$lib/scripts/types";

import { listCards } from "$lib/scripts/utils";

export const ssr = false;
const opsmlRoot: string = `opsml-root:/${RegistryName.Model}`;

/** @type {import('./$types').PageLoad} */
export async function load({ fetch, params, url }) {
  const name: string = url.searchParams.get("name")!;
  const repository: string = url.searchParams.get("repository")!;
  const version = url.searchParams.get("version");
  const registry = "model";

  return {
    name,
    repository,
    version,
    registry,
  };
}
