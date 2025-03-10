export const prerender = true;
export const ssr = false;
import { opsmlClient } from "$lib/components/api/client.svelte";
import { RegistryType } from "$lib/utils";
import { getCardMetadata } from "$lib/components/card/utils";

// @ts-ignore
import type { LayoutServerLoad } from "./$types";

// @ts-ignore
export const load: LayoutServerLoad = async ({ url }) => {
  await opsmlClient.validateAuth(true);

  const name = (url as URL).searchParams.get("name") as string;
  const repository = (url as URL).searchParams.get("repository") as string;
  const version = (url as URL).searchParams.get("version") as string;
  const registry = RegistryType.Model;

  let metadata = getCardMetadata(name, repository, version, registry);

  console.log(metadata);

  return {};
};
