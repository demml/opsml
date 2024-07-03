<script lang="ts">

  import { type ModelMetadata , type Card, type RunCard, type Parameter, type Metric } from "$lib/scripts/types";
  import { TabGroup, Tab } from '@skeletonlabs/skeleton';
  import Search from "$lib/Search.svelte";
  import Fa from 'svelte-fa'
  import { faCheck } from '@fortawesome/free-solid-svg-icons'

    /** @type {import('./$types').LayoutData} */
    export let data;

    let card: Card;
    $: card = data.card;

    let metadata: RunCard;
    $: metadata = data.metadata;

    let metrics: Metric[];
    $: metrics = data.metrics;

    let metricNames: string[];
    $: metricNames = data.metricNames;

    let parameters: Parameter[];
    $: parameters = data.parameters;

    let searchTerm: string | undefined;
    $: searchTerm = undefined;

    let filteredMetrics: string[] = [];
    let tabSet: string = "metrics";

    let selectedMetrics: string[];
    $: selectedMetrics = [];

    let chartOptions: { [key: string]: string };
    $: chartOptions = {};

    const searchMetrics = () => {	
		return filteredMetrics = metricNames.filter(item => {
			let itemName = item.toLowerCase();
			return itemName.includes(searchTerm!.toLowerCase())
		})
	}

  async function setActiveMetrics( name: string) {

    if (selectedMetrics.includes(name)) {
      selectedMetrics = selectedMetrics.filter((item) => item !== name);
    } else {
      selectedMetrics = [...selectedMetrics, name];
    }


  }

  async function plot() {

    // print selected metrics
    console.log(selectedMetrics);
    
  }

</script>

<div class="flex min-h-screen">
  <div class="hidden md:block flex-initial w-1/4 pl-16 bg-surface-100 dark:bg-surface-600">
    <div class="p-4">

      <div class="flex justify-between">
       
        <TabGroup border="" active='border-b-2 border-primary-500'>
          <Tab bind:group={tabSet} name="repos" value="metrics">Metrics</Tab>
        </TabGroup>
        <button type="button" class="m-4 btn btn-sm bg-darkpurple text-white" on:click={() => plot()}>Plot Metrics</button>

      </div>  
      <div class="pt-4">
        <Search bind:searchTerm on:input={searchMetrics} />
      </div>
      <div class="flex flex-wrap pt-4 gap-1">

        {#if searchTerm && filteredMetrics.length == 0}
          <p class="text-gray-400">No metrics found</p>

        {:else if filteredMetrics.length > 0}
          {#each filteredMetrics as metric}
            
            <button
              class="chip hover:bg-primary-300 {selectedMetrics.includes(metric) ? 'bg-primary-300' : 'variant-soft'}"
              on:click={() => { setActiveMetrics(metric); }}
              on:keypress
            >
              {#if selectedMetrics.includes(metric)}<span><Fa icon={faCheck} /></span>{/if}
              <span>{metric}</span>
            </button>

          {/each}

        {:else}
          {#each metricNames as metric}

            <button
              class="chip hover:bg-primary-300 {selectedMetrics.includes(metric) ? 'bg-primary-300' : 'variant-soft'}"
              on:click={() => { setActiveMetrics(metric); }}
              on:keypress
            >
              {#if selectedMetrics.includes(metric)}<span><Fa icon={faCheck} /></span>{/if}
              <span>{metric}</span>
            </button>
        
          {/each}

        {/if}

      </div>
    </div>
    <div>
    </div>
  </div>
</div>