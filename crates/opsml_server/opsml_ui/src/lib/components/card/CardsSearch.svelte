
<script lang="ts">
  import { onMount } from "svelte";
  import { getRegistryPage, getRegistryStats } from "./utils";
  import type { RegistryPageReturn, RegistryStatsResponse, QueryPageResponse} from "$lib/components/card/types";
  import  { RegistryType, delay } from "$lib/utils";
  import { Settings } from 'lucide-svelte';

  


  let { selectedSpace, page } = $props<{
    selectedSpace: string | null;
    page: RegistryPageReturn;
  }>();
 
  let searchQuery = $state('');
  let artifactSearchQuery = $state('');
  let activeSpace = $state<string | undefined>(undefined);
  let filteredSpaces = $state<string[]>([]);
  let availableSpaces = page.spaces;

  // registry-specific state
  let registryType = $state<RegistryType>(page.registry_type);
  let registryPage = $state<QueryPageResponse>(page.registryPage);
  let registryStats = $state<RegistryStatsResponse>(page.registryStats);


  onMount(() => {
    filteredSpaces = page.spaces;

    if (selectedSpace) {
      activeSpace = selectedSpace;
      console.log("selectedSpace", selectedSpace);
    }

  });

  async function setActiveRepo(space: string) {

    // handle click and declick
    if (activeSpace === space) {
      activeSpace = undefined;
    } else {
      activeSpace = space;
    }

    registryPage = await getRegistryPage(registryType, undefined, activeSpace, undefined, 0);
    registryStats = await getRegistryStats(registryType,activeSpace);
  }

  const searchSpaces = () => {	
		return filteredSpaces = availableSpaces.filter((item: string) => {
			let itemName = item.toLowerCase();
			return itemName.includes(searchQuery!.toLowerCase())
		})
	}

  const searchPage = async function () {
  registryPage = await getRegistryPage(registryType, undefined, activeSpace, artifactSearchQuery, 0);
  registryStats = await getRegistryStats(registryType, artifactSearchQuery);
  }

</script>



<div class="mx-auto w-11/12 min-h-screen pt-20 pb-10 m500:pt-14 lg:pt-[100px] flex justify-center">
  <div class="grid grid-cols-1 md:grid-cols-6 gap-4 w-full">
    <!-- Left column -->
    <div class="col-span-1 md:col-span-2 bg-surface-200 p-4 flex flex-col rounded-base border-black border-2 shadow-small">
      <!-- Top Section -->
      <div class="mb-4">
        <h2 class="font-bold text-primary-500 text-xl mb-1">Search Spaces</h2>
          <input
            class="input text-sm rounded-base bg-surface-50 text-black disabled:opacity-50 placeholder-surface-800 placeholder-text-sm focus-visible:ring-2 focus-visible:ring-primary-800"
            type="text"
            bind:value={searchQuery}
            placeholder="Search..."
            oninput={searchSpaces}
          />
      </div>

      <!-- Bottom Section -->
      <div class="space-y-2 flex flex-wrap pt-4 gap-1">
        <!-- Add your tags or other content here -->
        {#if searchQuery && filteredSpaces.length == 0}
          <p>No repositories found</p>
        {:else if filteredSpaces.length > 0}
          {#each filteredSpaces as space}

            {#if activeSpace === space}
              <button class="chip text-black bg-secondary-400 border-black border-1 reverse-shadow-small reverse-shadow-hover-small" onclick={() => setActiveRepo(space)}>{space}</button>
            {:else}
              <button class="chip text-black border-black border-1 shadow-small shadow-hover-small" onclick={() => setActiveRepo(space)}>{space}</button>
            {/if}
          
          {/each}
        {/if}
      </div>
    </div>

    <!-- Right column -->
    <div class="col-span-1 md:col-span-4 gap-1 bg-surface-50 p-4 flex flex-col rounded-base border-black border-2 shadow-small">
      <!-- Add your items here -->
      <div class="flex flex-row gap-1 items-center">
        <div class="ml-2">
          <Settings color="#37b98e" />
        </div>
        <h2 class="font-bold text-black text-xl">Artifacts</h2>
      </div>
      <div class="flex flex-row gap-1 items-center">
        <div>
          <span class="badge text-primary-600 border-black border-1 shadow-small">{registryStats.stats.nbr_names} artifacts</span>
        </div>
        <div>
          <span class="badge text-primary-600 border-black border-1 shadow-small">{registryStats.stats.nbr_versions} versions</span>
        </div>
        <div>
          <span class="badge text-primary-600 border-black border-1 shadow-small">{registryStats.stats.nbr_repositories} spaces</span>
        </div>
        <div class="ml-1 md:w-full">
          <input
            class="input text-sm rounded-base bg-surface-50 text-black disabled:opacity-50 placeholder-surface-800 placeholder-text-sm focus-visible:ring-2 focus-visible:ring-primary-800"
            type="text"
            bind:value={artifactSearchQuery}
            placeholder="Search artifacts"
            onkeydown={delay(searchPage, 1000)}
          />
        </div>
      </div>
    </div>
  </div>
</div>