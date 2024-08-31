<script lang="ts">

  import { type PaginationSettings } from '@skeletonlabs/skeleton';
  import {
  type registryStats,
  type registryPage,
} from "$lib/scripts/types";
  import ArtifactSearch from '$lib/ArtifactSearch.svelte';
  import { RunPageStore } from '$routes/store';

  /** @type {import('./$types').PageData} */
	export let data;

  // reactive statements
  let artifactSearchTerm: string | undefined = undefined;

  let searchTerm: string | undefined;
  $: searchTerm = data.args.searchTerm;

  let repos: string[];
  $: repos = data.args.repos;

  let selectedRepo: string | undefined;
  $: selectedRepo = $RunPageStore.selectedRepo;

  let registryPage: registryPage;
  $: registryPage = $RunPageStore.registryPage;

  let registryStats: registryStats;
  $: registryStats = $RunPageStore.registryStats;

  let activePage: number = 0;
  let filteredRepos: string[] = [];
  let tabSet: string = "repos";

  let registry: string;
  $: registry = data.args.registry;

  let paginationSettings = {
    page: 0,
    limit: 30,
    size: $RunPageStore.registryStats.nbr_names,
    amounts: [],
  } satisfies PaginationSettings;

    

</script>

<ArtifactSearch 
  tabSet={tabSet} 
  searchTerm={searchTerm} 
  filteredRepos={filteredRepos} 
  paginationSettings={paginationSettings} 
  repos={repos} 
  selectedRepo={selectedRepo} 
  registryPage={registryPage} 
  registryStats={registryStats} 
  registry={registry} 
  artifactSearchTerm={artifactSearchTerm} 
  pageStore={RunPageStore}
  />