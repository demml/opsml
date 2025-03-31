<script lang="ts">
  
  import CardsSearch from "$lib/components/card/CardsSearch.svelte";
  import type { PageProps } from './$types';
  import type { RegistryPageReturn } from "$lib/components/card/types";
  import type { BaseCard } from "$lib/components/home/types";
  import { Search } from "lucide-svelte";
  import { CircleDot } from 'lucide-svelte';
  import { List } from 'lucide-svelte';
  import VersionPill from "$lib/components/card/experiment/VersionPill.svelte";

  let { data }: PageProps = $props();

  let selectedMetrics: string[] = $state([]);
  let selectedParameters: string[] = $state([]);
  let selectedCardVersions: BaseCard[]  = $state([]);

  // search setup
  let currentTab = $state('metrics');
  let searchQuery = $state('');
  let availableEntities: string[] = $state(data.metricNames);
  let filteredEntities: string[] = $derived.by(() => {
    return availableEntities.filter((entity: string) => {
      return entity.toLowerCase().includes(searchQuery.toLowerCase());
    });
  });
  let availableCards: BaseCard[] = $state(data.cardVersions);


  async function selectMetric(metricName: string) {
    // if the metric is already selected, remove it
    if (selectedMetrics.includes(metricName)) {
      selectedMetrics = selectedMetrics.filter((metric: string) => metric !== metricName);
    } else {
      // otherwise, add it to the selected metrics
      selectedMetrics = [...selectedMetrics, metricName];
    }
  }

  async function selectParameter(parameter: string) {
    // if the parameter is already selected, remove it
    if (selectedParameters.includes(parameter)) {
      selectedParameters = selectedParameters.filter((param: string) => param !== parameter);
    } else {
      // otherwise, add it to the selected parameters
      selectedParameters = [...selectedParameters, parameter];
    }
  }

  async function selectCardVersion(selectedCard: BaseCard) {
    // if the card version is already selected, remove it
    if (selectedCardVersions.includes(selectedCard)) {
      selectedCardVersions = selectedCardVersions.filter((card: BaseCard) => card !== selectedCard);
    } else {
      // otherwise, add it to the selected card versions
      selectedCardVersions = [...selectedCardVersions, selectedCard];
    }
  }

  async function filterEntities() {
    // filter the entities based on the search query
    filteredEntities = availableEntities.filter((entity: string) => {
      return entity.toLowerCase().includes(searchQuery.toLowerCase());
    });
  }

  async function plotMetrics() {
    // handle the plot button click
    console.log('Plotting metrics:', selectedMetrics);
    console.log('Selected parameters:', selectedParameters);
    console.log('Selected card versions:', selectedCardVersions);
  }



  </script>
<div class="mx-auto w-11/12 pt-4 pb-10 flex justify-center">
  <div class="grid grid-cols-2 md:grid-cols-8 gap-4 w-full">

    <!-- Left Column-->
    <div class="col-span-1 md:col-span-2 bg-surface-50 p-4 flex flex-col rounded-base border-black border-2 shadow max-h-[calc(100vh-200px)] overflow-y-auto">
      <!-- Top Section -->
      <div class="mb-4 sticky top-0 bg-surface-50 z-10">
        <div class="flex flex-row justify-between pt-2 pb-3">
          <div class="flex flex-row">
            <div class="self-center" aria-label="Time Interval">
              <CircleDot color="#8059b6"/>
            </div>
            <header class="pl-2 text-primary-800 text-2xl self-center font-bold">Search {currentTab}</header>
          </div>
          <div class="flex flex-row">
            <button type="button" class="btn bg-primary-500 text-black shadow shadow-hover border-black border-2 self-center" onclick={plotMetrics}>Plot</button>
          </div>
        </div>
        <div class="flex flex-row gap-1 items-center">
          <div class="mr-1">
            <Search color="#5948a3" />
          </div>  
          <input
            class="input text-sm rounded-base bg-surface-50 text-black disabled:opacity-50 placeholder-surface-800 placeholder-text-sm focus-visible:ring-1 border-black border-2 h-1/3"
            type="text"
            bind:value={searchQuery}
            placeholder="Search..."
            oninput={filterEntities}
          />
        </div>
      </div>
      <!-- card versions -->
      <div class="flex-1">
        <div class="mb-4">
          <div class="flex flex-row items-center mb-1 border-b-2 border-black">
            <List color="#8059b6"/>
            <header class="pl-2 text-primary-900 text-lg font-bold">Items</header>
          </div>
          <div class="space-y-2 flex flex-wrap pl-2 pt-4 pb-4 gap-1 overflow-y-scroll">
            <!-- Iterate of available entities -->
            {#each filteredEntities as entity}
              {#if currentTab === 'metrics'}
                {#if selectedMetrics.includes(entity)}
                  <button class="chip bg-slate-100 border-primary-800 border-2 text-primary-800 border-1 lg:text-base" onclick={() => selectMetric(entity)}>{entity}</button>
                {:else}
                  <button class="chip text-black bg-primary-500 shadow-small shadow-hover-small border-black border-1 lg:text-base" onclick={() => selectMetric(entity)}>{entity}</button>
                {/if}
              {/if}
              {#if currentTab === 'parameters'}
                {#if selectedParameters.includes(entity)}
                  <button class="chip bg-slate-100 border-primary-800 border-2 text-primary-800 border-1" onclick={() => selectParameter(entity)}>{entity}</button>
                {:else}
                  <button class="chip text-black bg-primary-500 shadow-small shadow-hover-small border-black border-1" onclick={() => selectParameter(entity)}>{entity}</button>
                {/if}
              {/if}
            {/each}
          </div>
        </div>

        <div class="mb-4">
          <div class="flex flex-row items-center mb-1 border-b-2 border-black">
            <List color="#8059b6"/>
            <header class="pl-2 text-primary-900 text-lg font-bold">Previous Versions</header>
          </div>
          <h3 class="pl-2 text-primary-900 text-lg text-black">Select previous version to compare metrics</h3>
          <div class="flex flex-col space-y-1 pl-2 pt-4 pb-4 gap-1 overflow-auto">
            {#each availableCards as card}
              {#if selectedCardVersions.includes(card)}
                <VersionPill {card} active={true} setActive={selectCardVersion}/>
              {:else}
                <VersionPill {card} active={false} setActive={selectCardVersion}/>
              {/if}
            {/each}
          </div>
        </div>
      </div>

    </div>
    <div class="col-span-1 md:col-span-6 gap-4 w-full">
      <div class="bg-white p-4 border-2 border-black rounded-lg shadow h-[500px]">
      </div>
    </div>
  </div>
</div>