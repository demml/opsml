import {
  type registryStats,
  type registryPage,
  type repositories,
  CommonPaths,
  type registryPageReturn,
} from "$lib/scripts/types";
import { setupRegistryPage } from "$lib/scripts/utils";

export const ssr = false;

/** @type {import('./$types').PageLoad} */
export async function load({ fetch, params, url }) {
  let repository: string | undefined;
  const providedRepository: string | null = (url as URL).searchParams.get(
    "repository"
  );

  if (providedRepository === null) {
    repository = undefined;
  } else {
    repository = providedRepository;
  }

  const registry: string = "model";

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
