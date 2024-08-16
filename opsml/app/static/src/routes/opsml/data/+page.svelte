<script lang="ts">
  import { onMount } from 'svelte';
  import {
  getRegistryPage,
  getRegistryStats,
} from "$lib/scripts/registry_page";
  import { type PaginationSettings } from '@skeletonlabs/skeleton';
  import {
  type registryStats,
  type registryPage,
} from "$lib/scripts/types";
  import ArtifactSearch from '$lib/ArtifactSearch.svelte';

  /** @type {import('./$types').PageData} */
	export let data;

  // reactive statements
  let artifactSearchTerm: string | undefined = undefined;

  let repos: string[];
  $: repos = data.args.repos;

  let searchTerm: string | undefined;
  $: searchTerm = data.args.searchTerm;

  let selectedRepo: string | undefined;
  $: selectedRepo = data.args.selectedRepo;

  let registryPage: registryPage;
  $: registryPage = data.args.registryPage;

  let registryStats: registryStats;
  $: registryStats = data.args.registryStats;

  let activePage: number = 0;
  let filteredRepos: string[] = [];
  let tabSet: string = "repos";

  let registry: string;
  $: registry = data.args.registry;

  let paginationSettings = {
    page: 0,
    limit: 30,
    size: data.args.registryStats.nbr_names,
    amounts: [],
  } satisfies PaginationSettings;


  onMount(async () => {
    if (selectedRepo) {
      registryPage = await getRegistryPage(registry, undefined, selectedRepo, searchTerm, 0);
      registryStats = await getRegistryStats(registry, selectedRepo);
      
      paginationSettings.page = 0;
      paginationSettings.size = registryStats.nbr_names;
    } 
    
  });



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
  />




