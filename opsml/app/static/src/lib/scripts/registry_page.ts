import { type registryStats, type registryPage } from "$lib/scripts/types";

// Function for searching general stats given a registry and search term
//
// Args:
//   registry: string - the registry to search
//   searchTerm: string - the search term to use
//
// Returns:
//   registryQuery - the general stats for the registry
async function getRegistryStats(
  registry: string,
  searchTerm: string | undefined
): Promise<registryStats> {
  const params = new URLSearchParams();
  params.append("registry_type", registry);
  if (searchTerm) {
    params.append("search_term", searchTerm);
  }

  const page_resp = await fetch(`/opsml/cards/registry/stats?${params}`);

  const response: registryStats = await page_resp.json();
  return response;
}

// Function for searching a registry page given a registry, sort_by, repository, name, and page
//
// Args:
//   registry: string - the registry to search
//   sort_by: string - the sort_by to use
//   repository: string - the repository to use
//   name: string - the name to use
//   page: number - the page to use
//
// Returns:
//   registryQuery - the page for the registry
async function getRegistryPage(
  registry: string,
  sort_by: string | undefined,
  repository: string | undefined,
  search_term: string | undefined,
  page: number | undefined
): Promise<registryPage> {
  // build request
  const params = new URLSearchParams();
  params.append("registry_type", registry);

  if (sort_by) {
    params.append("sort_by", sort_by);
  }
  if (repository) {
    params.append("repository", repository);
  }
  if (search_term) {
    params.append("search_term", search_term);
  }
  if (page) {
    params.append("page", page.toString());
  }

  const page_resp = await fetch(`/opsml/cards/registry/query/page?${params}`);

  const response: registryPage = await page_resp.json();
  return response;
}

export { getRegistryStats, getRegistryPage };
