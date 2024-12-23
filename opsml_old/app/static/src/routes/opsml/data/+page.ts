import { type registryPageReturn } from "$lib/scripts/types";
import { setupRegistryPage } from "$lib/scripts/utils";
import { DataPageStore } from "$routes/store";
import { get } from "svelte/store";
import { checkAuthstore } from "$lib/scripts/auth/authManager";

export const ssr = false;

/** @type {import('./$types').PageLoad} */
export async function load({ url }) {
  await checkAuthstore();

  const repository = (url as URL).searchParams.get("repository") as
    | string
    | undefined;

  const registry: string = "data";

  const page: registryPageReturn = await setupRegistryPage(registry);

  if (!get(DataPageStore).selectedRepo) {
    DataPageStore.update((store) => {
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
