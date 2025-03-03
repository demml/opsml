import { CommonPaths } from "$lib/scripts/types";
import { apiHandler } from "$lib/scripts/apiHandler";

interface repositories {
  repositories: string[];
}

async function getRepos(registry: string) {
  const repos = await apiHandler.get(
    `${CommonPaths.REPOSITORIES}?${new URLSearchParams({
      registry_type: registry,
    }).toString()}`
  );

  const response = (await repos.json()) as repositories;
  return response.repositories;
}

export { getRepos };
