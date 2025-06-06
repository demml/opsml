<script lang="ts">
  
  import type { PageProps } from './$types';
  import { onMount } from "svelte";
  import type { SpaceStats, SpaceStatsResponse } from "$lib/components/space/types";
  import { ArrowLeft, ArrowRight, Search, Settings } from 'lucide-svelte';
  import  { delay } from "$lib/utils";
  import CreateSpaceModal from "$lib/components/space/CreateSpaceModal.svelte";
  import SpacePage from "$lib/components/space/SpacePage.svelte";

  let { data }: PageProps = $props();
  let spaces: SpaceStatsResponse = data.spaces;

  let currentPage = $state(1);
  let totalPages = $state(1);

  let searchQuery = $state('');
  let filteredSpaces = $state<SpaceStats[]>([]);
  let availableSpaces = spaces.stats;

  const searchSpaces = () => {
    // filter based on item.space
    filteredSpaces = availableSpaces.filter((item: SpaceStats) => {
      let itemName = item.space.toLowerCase();
      return itemName.includes(searchQuery!.toLowerCase())
    });

    totalPages = Math.ceil(filteredSpaces.length / 30);
  }

  onMount(() => {
    // get first 30 spaces
    filteredSpaces = spaces.stats.slice(0, 30);
    totalPages = Math.ceil(spaces.stats.length / 30);
  });


  const changePage = async function (page: number) {
    // change page (slice based on page number)
    if (page < 1 || page > totalPages) return;

    const start = (page - 1) * 30;
    const end = start + 30;
    filteredSpaces = spaces.stats.slice(start, end);

    currentPage = page;
  }



</script>
<div class="flex-1 mx-auto w-9/12 pt-20 pt-[100px] justify-center px-4 pb-10">
  <div class="gap-1 p-4 flex flex-col rounded-base border-primary-500 border-2 shadow-primary bg-surface-50  w-full h-auto">

    <div class="flex flex-row items-center gap-2 pb-2">
      <div class="rounded-full bg-surface-200 border-black border-2 p-1 shadow-small">
        <Settings color="#40328b" />
      </div>
      <h2 class="font-bold text-primary-800 text-xl">Spaces</h2>
    </div>

    <div class="flex flex-col md:flex-row justify-between pb-2 items-start gap-3 md:gap-1 w-full ">
      <div class="w-full md:w-2/3">
          <input
            class="input w-full text-sm rounded-base bg-surface-50 text-black disabled:opacity-50 placeholder-surface-800 placeholder-text-sm focus-visible:ring-1 border-black border-2 h-9"
            type="text"
            bind:value={searchQuery}
            placeholder="Search spaces..."
            onkeydown={delay(searchSpaces, 1000)}
          />
      </div>
      <div class="w-full md:w-auto">
        <CreateSpaceModal/>
      </div>
    </div>

    {#if filteredSpaces.length > 0}
      <div class="pt-4 grid grid-cols-1 md:grid-cols-2 2xl:grid-cols-4 gap-4 justify-items-center">
        {#each filteredSpaces as record}
          <div class="flex justify-center w-full">
            <SpacePage {record} />
          </div>
        {/each}
      </div>

    {:else}
      <div class="flex flex-col gap-2 mt-2 items-center justify-center">
        <p class="text-primary-800 text-lg">No spaces found</p>
        <p class="text-gray-500">Register cards to see spaces appear here</p>
      </div>
    {/if}

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