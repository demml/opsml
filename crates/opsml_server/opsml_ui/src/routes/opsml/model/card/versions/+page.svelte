<script lang="ts">
  import type { VersionPageResponse, RegistryStatsResponse } from "$lib/components/card/types";
  import { getRegistryPage, getVersionPage, } from "$lib/components/card/utils";
  import type { RegistryType } from "$lib/utils";
  import type { PageProps } from './$types';
  import { onMount } from "svelte";
  import { Settings } from 'lucide-svelte';
  import VersionPage from "$lib/components/card/VersionPage.svelte";
  import { ArrowLeft, ArrowRight } from 'lucide-svelte';

  let { data }: PageProps = $props();
  let currentPage = $state(1);
  let totalPages = $state(1);
  let artifactSearchQuery = $state('');

  getRegistryPage
  // registry-specific state
  let registryPage = $state<VersionPageResponse>(data.versionPage);
  let registryStats = $state<RegistryStatsResponse>(data.versionStats);

  const changePage = async function (page: number) {
    registryPage = await getVersionPage(data.registry, data.metadata.repository, data.metadata.name, page);
    currentPage = page;
  }

  onMount(() => {
      totalPages = Math.ceil(registryStats.stats.nbr_versions / 30);
  });

  </script>
  
  <div class="flex-1 mx-auto w-9/12 pb-10 flex justify-center overflow-auto px-4 pt-4">

    <div class="grid grid-cols-1 w-full">

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
            <span class="badge text-base text-primary-800 border-black border-1 shadow-small bg-surface-50">{registryStats.stats.nbr_repositories} spaces</span>
          </div>
        </div>
        <div class="pt-4 grid grid-cols-1 md:grid-cols-2 2xl:grid-cols-3 gap-4">
          {#each registryPage.summaries as summary}
            <VersionPage
              repository={summary.repository}
              name={summary.name}
              version={summary.version}
              updated_at={summary.created_at}
              registry={data.registry}
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
    
          {#if currentPage < totalPages}
            <button class="btn bg-surface-50 border-black border-2 shadow-small shadow-hover-small h-9" onclick={() => changePage(currentPage + 1)}>
              <ArrowRight color="#5948a3"/>
            </button>
          {/if}
        
        </div>
      </div>

    </div>
  
  </div>