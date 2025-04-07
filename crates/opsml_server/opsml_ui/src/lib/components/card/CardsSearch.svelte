
<script lang="ts">
  import { onMount } from "svelte";
  import { getRegistryPage, getRegistryStats, getBgColor } from "./utils";
  import type { RegistryPageReturn, RegistryStatsResponse, QueryPageResponse} from "$lib/components/card/types";
  import  CardPage  from "$lib/components/card/CardPage.svelte";
  import  { RegistryType, delay } from "$lib/utils";
  import { Settings } from 'lucide-svelte';
  import { Search } from 'lucide-svelte';
  import { ArrowLeft, ArrowRight } from 'lucide-svelte';

  
  let { selectedSpace, page, selectedName } = $props<{
    selectedSpace: string | undefined;
    selectedName: string | undefined;
    page: RegistryPageReturn;
  }>();
 
  let currentPage = $state(1);
  let totalPages = $state(1);

  let searchQuery = $state('');
  let artifactSearchQuery = $state(selectedName || '');
  let activeSpace = $state<string | undefined>(selectedSpace);
  let filteredSpaces = $state<string[]>([]);
  let availableSpaces = page.spaces;

  // registry-specific state
  let registryType = $state<RegistryType>(page.registry_type);
  let registryPage = $state<QueryPageResponse>(page.registryPage);
  let registryStats = $state<RegistryStatsResponse>(page.registryStats);


  onMount(() => {
  
    filteredSpaces = page.spaces;
    totalPages = Math.ceil(registryStats.stats.nbr_names / 30);

  });

  async function setActiveRepo(space: string) {

    // handle click and declick
    if (activeSpace === space) {
      activeSpace = undefined;
    } else {
      activeSpace = space;
    }

    registryPage = await getRegistryPage(registryType, undefined, activeSpace, undefined, 1);
    registryStats = await getRegistryStats(registryType, activeSpace);
    currentPage = 1;
    totalPages = Math.ceil(registryStats.stats.nbr_names / 30);
  }

  const searchSpaces = () => {	
		return filteredSpaces = availableSpaces.filter((item: string) => {
			let itemName = item.toLowerCase();
			return itemName.includes(searchQuery!.toLowerCase())
		})
	}

  const searchPage = async function () {
  registryPage = await getRegistryPage(registryType, undefined, activeSpace, artifactSearchQuery, 1);
  registryStats = await getRegistryStats(registryType, artifactSearchQuery, activeSpace);
  currentPage = 1;
  totalPages = Math.ceil(registryStats.stats.nbr_names / 30);
  }

  const changePage = async function (page: number) {
    registryPage = await getRegistryPage(registryType, undefined, activeSpace, artifactSearchQuery, page);
    registryStats = await getRegistryStats(registryType, artifactSearchQuery, activeSpace);
    currentPage = page;
  }

</script>


<div class="grid grid-cols-1 md:grid-cols-6 gap-4 w-full">
  <!-- Left column -->
  <div class="col-span-1 md:col-span-2 bg-slate-100 p-4 flex flex-col rounded-base border-black border-2 shadow h-[400px]">
    <!-- Top Section -->
    <div class="mb-4">
      <h2 class="font-bold text-primary-800 text-xl pb-3">Search Spaces</h2>
      <div class="flex flex-row gap-1 items-center">
        <div class="mr-1">
          <Search color="#5948a3" />
        </div>  
        <input
          class="input text-sm rounded-base bg-surface-50 text-black disabled:opacity-50 placeholder-surface-800 placeholder-text-sm focus-visible:ring-1 border-black border-2 h-1/3"
          type="text"
          bind:value={searchQuery}
          placeholder="Search..."
          oninput={searchSpaces}
        />
      </div>
    </div>

    <!-- Bottom Section -->
    <div class="h-1/3">
      <div class="space-y-2 flex flex-wrap pl-2 pt-4 pb-4 gap-1 overflow-y-scroll">
        <!-- Add your tags or other content here -->
        {#if searchQuery && filteredSpaces.length == 0}
          <p class="text-black">No spaces found</p>
        {:else if filteredSpaces.length > 0}
          {#each filteredSpaces as space}

            {#if activeSpace === space}
              <button class="chip text-black bg-primary-300 border-black border-1 reverse-shadow-small reverse-shadow-hover-small lg:text-base" onclick={() => setActiveRepo(space)}>{space}</button>
            {:else}
              <button class="chip text-black border-black border-1 shadow-small shadow-hover-small bg-surface-50 lg:text-base" onclick={() => setActiveRepo(space)}>{space}</button>
            {/if}
          
          {/each}
        {/if}
      </div>
    </div>
  </div>

  <!-- Right column -->
  <div class="col-span-1 md:col-span-4 gap-1 p-4 flex flex-col rounded-base border-primary-500 border-2 shadow-primary bg-surface-50 h-auto">
    <!-- Add your items here -->
    <div class="flex flex-row items-center gap-2 pb-2">
      <div class="rounded-full bg-surface-200 border-black border-2 p-1 shadow-small">
        <Settings color="#40328b" />
      </div>
      <h2 class="font-bold text-primary-800 text-xl">Artifacts</h2>
    </div>
    <div class="flex flex-row flex-wrap gap-1 items-center">
      <div>
        <span class="badge text-base text-primary-800 border-black border-1 shadow-small bg-surface-50">{registryStats.stats.nbr_names} artifacts</span>
      </div>
      <div>
        <span class="badge text-base text-primary-800 border-black border-1 shadow-small bg-surface-50">{registryStats.stats.nbr_versions} versions</span>
      </div>
      <div>
        <span class="badge text-base text-primary-800 border-black border-1 shadow-small bg-surface-50">{registryStats.stats.nbr_spaces} spaces</span>
      </div>
      <div class="ml-1 w-full md:w-auto lg:flex-1">
        <input
          class="input w-full text-sm rounded-base bg-surface-50 text-black disabled:opacity-50 placeholder-surface-800 placeholder-text-sm focus-visible:ring-1 border-black border-2 h-9"
          type="text"
          bind:value={artifactSearchQuery}
          placeholder="Search artifacts"
          onkeydown={delay(searchPage, 1000)}
        />
      </div>
    </div>
    <div class="pt-4 grid grid-cols-1 md:grid-cols-2 2xl:grid-cols-3 gap-4">
      {#each registryPage.summaries as summary}
        <CardPage
          space={summary.space}
          name={summary.name}
          version={summary.version}
          nbr_versions={summary.versions}
          updated_at={summary.updated_at}
          registry={registryType}
          bgColor={"bg-primary-400"}
        />
      {/each}
    </div>

    <div class="flex justify-center pt-4 gap-2">

      {#if currentPage > 1}
        <button class="btn bg-surface-50 border-black border-2 shadow-small shadow-hover-small h-9" onclick={() => changePage(currentPage - 1)}>
          <ArrowLeft color="#5948a3"/>
        </button>
      {/if}
      
      <div class="flex bg-surface-50 border-black border-2 text-center items-center rounded-base px-2 shadow-small h-9">
        <span class="text-primary-800 mr-1">{currentPage}</span>
        <span class="text-primary-400">of {totalPages}</span>
      </div>

      {#if currentPage < totalPages }
        <button class="btn bg-surface-50 border-black border-2 shadow-small shadow-hover-small h-9" onclick={() => changePage(currentPage + 1)}>
          <ArrowRight color="#5948a3"/>
        </button>
      {/if}
    
    </div>
  </div>
</div>
