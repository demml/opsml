import { type registryPageReturn } from "$lib/scripts/types";
import { setupRegistryPage } from "$lib/scripts/utils";

export const ssr = false;

/** @type {import('./$types').PageLoad} */
export async function load({ fetch, params, url }) {
  let repository: string | undefined;
  const providedRepository: string | null = url.searchParams.get("repository");

  if (providedRepository === null) {
    repository = undefined;
  } else {
    repository = providedRepository;
  }

  const registry: string = "run";

  let page: registryPageReturn = await setupRegistryPage(registry);

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
