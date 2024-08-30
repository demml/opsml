import { type registryPageReturn } from "$lib/scripts/types";
import { setupRegistryPage } from "$lib/scripts/utils";
import { AppStore } from "$routes/store";
import { get } from "svelte/store";

export const ssr = false;

/** @type {import('./$types').PageLoad} */
export async function load({ fetch, params, url }) {
  const repository = (url as URL).searchParams.get("repository") as
    | string
    | undefined;

  const registry: string = "run";

  const page: registryPageReturn = await setupRegistryPage(registry);

  console.log("search store");
  console.log(get(AppStore).runStore.homepage);

  if (!get(AppStore).runStore.homepage.selectedRepo) {
    AppStore.update((store) => {
      store.runStore.homepage.selectedRepo = repository;
      store.runStore.homepage.registryStats = page.registryStats;
      store.runStore.homepage.registryPage = page.registryPage;
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
