import { type registryPageReturn } from "$lib/scripts/types";
import { setupRegistryPage } from "$lib/scripts/utils";
import { ModelPageStore } from "$routes/store";
import { get } from "svelte/store";

export const ssr = false;

/** @type {import('./$types').PageLoad} */
export async function load({ url }) {
  const repository = (url as URL).searchParams.get("repository") as
    | string
    | undefined;

  const registry: string = "model";

  const page: registryPageReturn = await setupRegistryPage(registry);

  if (!get(ModelPageStore).selectedRepo) {
    ModelPageStore.update((store) => {
      store.selectedRepo = repository;
      store.registryStats = page.registryStats;
      store.registryPage = page.registryPage;
      return store;
    });
  }

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
