interface repositories {
  repositories: string[];
}

async function getRepos(registry: string) {
  const repos = await fetch(
    `/opsml/cards/repositories?${
      new URLSearchParams({
        registry_type: registry,
      })}`,
  );

  const response: repositories = await repos.json();
  return response.repositories;
}

export { getRepos };
