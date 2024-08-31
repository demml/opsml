<script lang="ts">

  import { TabGroup, Tab } from '@skeletonlabs/skeleton';
  import Fa from 'svelte-fa'
  import { faTag, faFolderTree, faBolt, faToolbox, faChartSimple } from '@fortawesome/free-solid-svg-icons'

  import modelcard_circuit from '$lib/images/modelcard-circuit.svg'

  import { type Card, type CompareMetricPage } from "$lib/scripts/types";
  import atomOneLight from "svelte-highlight/styles/atom-one-light";
  import RunHomePage from './home/RunHomePage.svelte';
  import RunMetricPage from './metrics/RunMetricPage.svelte';
  import RunComparePage from './metrics/compare/RunComparePage.svelte';
  import { loadComparePageData } from './metrics/compare/util';
  import { onMount } from 'svelte';
  import { resetRunCardStore } from '$routes/store';

  /** @type {import('./$types').LayoutData} */
	export let data;

  let registry: string;
  $: registry = data.registry;

  let name: string;
  $: name = data.name;

  let repository: string;
  $: repository = data.repository;

  let card: Card;
  $: card = data.card;

  let tabSet: string;
  $: tabSet = data.tabSet;

  let url: URL;
  $: url = data.url;
  

  let comparePageData: CompareMetricPage | undefined;
  $: comparePageData = undefined;


  async function navigateToFolder(value: string) {


    if (value === 'compare') {
      
      if (!comparePageData) {
        comparePageData = await loadComparePageData(data, url);
      };

      //if (!$AppStore.compareMetricData) {
      //  AppStore.update((store) => {
      //    store.compareMetricData = comparePageData?.metricVizData;
      //    return store;
      //  });
      //}
    }

    tabSet = value;
    
  }

  onMount(() => {
    // reset runStore
    resetRunCardStore();
  });



</script>

<svelte:head>
  {@html atomOneLight}
</svelte:head>

<div class="flex flex-1 flex-col">

  <div class="pl-4 md:pl-20 pt-2 sm:pt-4 bg-slate-50 w-full border-b">
    <h1 class="flex flex-row flex-wrap items-center text-lg">
      <div class="group flex flex-none items-center">
        <a class="font-semibold text-gray-800 hover:text-secondary-500" href="/opsml/{registry}?repository={repository}">{repository}</a>
        <div class="mx-0.5 text-gray-800">/</div>
      </div>
      <div class="font-bold text-primary-500">{name}</div>
      <div class="pl-2">
        <a href="/opsml/{registry}/card?name={name}&repository={repository}&version={card.version}" class="badge h-7 border border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100">
          <Fa class="h-4" icon={faTag} color="#4b3978"/>
          <span class="text-primary-500">{card.version}</span>
        </a>
      </div>
    </h1>

    <div class="pt-1">
      <TabGroup 
        padding="px-3 py-2"
        border=""
        active='border-b-2 border-primary-500'
        >
          <Tab bind:group={tabSet} name="card" value="card" on:click={() => navigateToFolder("card")}>
            <div class="flex flex-row items-center">
              <img class="h-4" src={modelcard_circuit} alt="ModelCard Circuit" />
              <div class="font-semibold text-sm">Card</div>
            </div>
          </Tab>

          <Tab bind:group={tabSet} name="files" value="files" on:click={() => navigateToFolder("files")}>
            <div class="flex flex-row  items-center">
              <Fa class="h-4 mr-2" icon={faFolderTree} color="#4b3978"/>
              <div class="font-semibold text-sm">Files</div>
            </div>
          </Tab>
  
          <Tab bind:group={tabSet} name="metrics" value="metrics" on:click={() => navigateToFolder("metrics")}>
            <div class="flex flex-row  items-center">
              <Fa class="h-4 mr-2" icon={faBolt} color="#4b3978"/>
              <div class="font-semibold text-sm">Metrics</div>
            </div>
          </Tab>

          <Tab bind:group={tabSet} name="compare" value="compare" on:click={() => navigateToFolder("compare")}>
            <div class="flex flex-row  items-center">
              <Fa class="h-4 mr-2" icon={faBolt} color="#4b3978"/>
              <div class="font-semibold text-sm">Compare</div>
            </div>
          </Tab>

          <Tab bind:group={tabSet} name="graphs" value="graphs" on:click={() => navigateToFolder("graphs")}>
            <div class="flex flex-row  items-center">
              <Fa class="h-4 mr-2" icon={faChartSimple} color="#4b3978"/>
              <div class="font-semibold text-sm">Graphs</div>
            </div>
          </Tab>

   
          <Tab bind:group={tabSet} name="hardware" value="hardware" on:click={() => navigateToFolder("hardware")}>
            <div class="flex flex-row  items-center">
              <Fa class="h-4 mr-2" icon={faToolbox} color="#4b3978"/>
              <div class="font-semibold text-sm">Hardware</div>
            </div>
          </Tab>

        </TabGroup>

    </div>

  </div>
  {#if tabSet === "card"}
    <RunHomePage {data}/>

  {:else if tabSet === "metrics"}
    <RunMetricPage {data}/>

  {:else if tabSet === "compare"}
    {#if comparePageData}
      <RunComparePage data={comparePageData} />
    {/if}
  {/if}
</div>
