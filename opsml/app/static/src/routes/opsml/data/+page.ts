import {
  type registryStats,
  type registryPage,
  type repositories,
  CommonPaths,
} from "$lib/scripts/types";
import { apiHandler } from "$lib/scripts/apiHandler";

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

  const registry: string = "data";

  let repos: repositories = await apiHandler
    .get(
      CommonPaths.REPOSITORIES +
        "?" +
        new URLSearchParams({
          registry_type: registry,
        }).toString()
    )
    .then((res) => res.json());

  let stats: registryStats = await apiHandler
    .get(
      CommonPaths.REGISTRY_STATS +
        "?" +
        new URLSearchParams({
          registry_type: registry,
        }).toString()
    )
    .then((res) => res.json());

  let page = await apiHandler
    .get(
      CommonPaths.QUERY_PAGE +
        "?" +
        new URLSearchParams({
          registry_type: registry,
          page: "0",
        }).toString()
    )
    .then((res) => res.json());

  return {
    args: {
      searchTerm: undefined,
      repos: repos.repositories,
      registry,
      selectedRepo: repository,
      registryStats: stats,
      registryPage: page,
    },
  };
}
