<script lang="ts">

import { TabGroup, Tab } from '@skeletonlabs/skeleton';
import { Paginator, type PaginationSettings } from '@skeletonlabs/skeleton';
import Search from "$lib/Search.svelte";
import {
  type registryStats,
  type registryPage,
} from "$lib/scripts/types";
import {
  getRegistryPage,
  getRegistryStats,
} from "$lib/scripts/registry_page";
import Fa from 'svelte-fa'
import { faCheck } from '@fortawesome/free-solid-svg-icons'
import PageCard from "$lib/PageCard.svelte";
import { delay } from "$lib/scripts/utils";



export let tabSet: string;
export let searchTerm: string | undefined;
export let filteredRepos: string[];
export let paginationSettings: PaginationSettings;
export let repos: string[];
export let selectedRepo: string | undefined;
export let registryPage: registryPage;
export let registryStats: registryStats;
export let registry: string;
export let artifactSearchTerm: string | undefined;


const searchRepos = () => {	
		return filteredRepos = repos.filter(item => {
			let itemName = item.toLowerCase();
			return itemName.includes(searchTerm!.toLowerCase())
		})
	}

async function setActiveRepo( name: string) {

    if (selectedRepo === name) {
      selectedRepo = undefined;
    } else {
      selectedRepo = name;
    }

    registryPage = await getRegistryPage(registry, undefined, selectedRepo, undefined, 0);
    registryStats = await getRegistryStats(registry, selectedRepo);

    paginationSettings.page = 0;
    paginationSettings.size = registryStats.nbr_names;
    }

async function onPageChange(e: CustomEvent) {
  let page = e.detail;

  registryPage = await getRegistryPage(registry, undefined, selectedRepo, searchTerm, page);
  paginationSettings.page = page;

}

const searchPage = async function () {

  registryPage = await getRegistryPage(registry, undefined, selectedRepo, artifactSearchTerm, 0);
  registryStats = await getRegistryStats(registry, artifactSearchTerm);
  paginationSettings.page = 0;
  paginationSettings.size = registryStats.nbr_names;


}


</script>

<div class="flex min-h-screen">
  <div class="hidden md:block flex-initial w-1/4 pl-6 bg-gray-50">
    <div class="p-4">
      <TabGroup 
      border=""
      active='border-b-2 border-primary-500'
      >
        <Tab bind:group={tabSet} name="repos" value="repos">Repositories</Tab>

      </TabGroup>
      <div class="pt-4">
        <Search bind:searchTerm on:input={searchRepos} />
      </div>
      <div class="flex flex-wrap pt-4 gap-1">

        {#if searchTerm && filteredRepos.length == 0}
          <p class="text-gray-400">No repositories found</p>

        {:else if filteredRepos.length > 0}
          {#each filteredRepos as repo}
           
            <button
              class="chip text-primary-500 hover:bg-primary-300 {selectedRepo === repo ? 'bg-primary-300' : 'bg-white'} border border-1 border-gray-200 shadow-sm"
              on:click={() => { setActiveRepo(repo); }}
              on:keypress
            >
              {#if selectedRepo === repo}<span><Fa icon={faCheck} /></span>{/if}
              <span>{repo}</span>
            </button>

          {/each}

        {:else}
          {#each repos as repo}

            <button
              class="chip text-primary-500 hover:bg-primary-300 {selectedRepo === repo ? 'bg-primary-300' : 'bg-white'} shadow-sm"
              on:click={() => { setActiveRepo(repo); }}
              on:keypress
            >
              {#if selectedRepo === repo}<span><Fa icon={faCheck} /></span>{/if}
              <span>{repo}</span>
            </button>
        
          {/each}

        {/if}

      </div>
    </div>
  </div>
  <div class="flex-auto w-64 p-4 bg-white dark:bg-surface-900 pr-16">
    <div class="flex flex-row items-center text-lg font-bold">
      <h1>Artifacts</h1>
    </div>
    
    <div class="flex flex-row">
      <div>
        <span class="badge variant-filled">{registryStats.nbr_names} artifacts</span>
      </div>
      <div class="pl-3">
        <span class="badge variant-filled">{registryStats.nbr_versions} versions</span>
      </div>
      <div class="pl-3">
        <span class="badge variant-filled">{registryStats.nbr_repos} repos</span>
      </div>
      <div class="pl-3 md:w-1/2">
        <Search bind:searchTerm={artifactSearchTerm} on:keydown={delay(searchPage, 1000)} />
      </div>

    </div>
    <div class="pt-8 grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
      {#each registryPage.page as item}
        <PageCard 
          repository={item[0]}
          name={item[1]}
          nbr_versions={item[2]}
          updated_at={item[3]}
          registry={registry}
        />
      {/each}
    </div>

    <div class="pt-8 flex items-center">
   
      <div class="flex-1 mb-12 w-64 content-center">
        <Paginator
          bind:settings={paginationSettings}
          showFirstLastButtons="{true}"
          showPreviousNextButtons="{true}"
          justify="justify-center"
          on:page={onPageChange}
        />
      </div>
    </div>
  </div>
</div>