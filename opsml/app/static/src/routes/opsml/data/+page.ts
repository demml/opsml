import { type registryPageReturn } from "$lib/scripts/types";
import { setupRegistryPage } from "$lib/scripts/utils";

export const ssr = false;

/** @type {import('./$types').PageLoad} */
export async function load({ url }) {
  const repository = (url as URL).searchParams.get("repository") as
    | string
    | undefined;

  const registry: string = "data";

  const page: registryPageReturn = await setupRegistryPage(registry);

  return {
    args: {
      searchTerm: undefined,
      repos: page.repos,
      registry,
      selectedRepo: repository,
      registryStats: page.registryStats,
      registryPage: page.registryPage,
    },
  };
}
