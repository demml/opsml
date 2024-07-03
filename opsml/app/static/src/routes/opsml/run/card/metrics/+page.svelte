<script lang="ts">

  import { type ModelMetadata , type Card, type RunCard, type Parameter, type Metric, type RunMetrics, type Graph } from "$lib/scripts/types";
  import { TabGroup, Tab } from '@skeletonlabs/skeleton';
  import Search from "$lib/Search.svelte";
  import Fa from 'svelte-fa'
  import { faCheck } from '@fortawesome/free-solid-svg-icons'
  import { buildBarChart, buildLineChart} from "$lib/scripts/charts";

    /** @type {import('./$types').LayoutData} */
    export let data;

    let card: Card;
    $: card = data.card;

    let metadata: RunCard;
    $: metadata = data.metadata;

    let metrics: RunMetrics;
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

    let plots: string[];
    $: plots = [];

    let combined: boolean = true;
    $: combined = true;

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

    // iterate over selected metrics
    if (combined) {
      
      const y: Map<string, number[]> = new Map<string, number[]>();
      for (let metric of selectedMetrics) {

        // get metric from metrics
        let metricData = metrics[metric];
        y.set(metricData[0].name, [metricData[metricData.length - 1].value]);
    }
    let graph: Graph = {
          name: "combined",
          x_label: "Group",
          y_label: "Value",
          x: [0],
          y,
          graph_type: "bar",
          graph_style: "combined",
        }

    
    buildBarChart(graph);
    console.log(plots);
    plots.push("combined");

    }
    
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
  
    <div class="flex-auto w-64 p-4 bg-white dark:bg-surface-900 pr-16">

      <div class="flex flex-row flex-wrap gap-2">
        <button type="button" class="m-1 btn btn-sm bg-darkpurple text-white" on:click={() => plot()}>Combined</button>
        <button type="button" class="m-1 btn btn-sm bg-darkpurple text-white" on:click={() => plot()}>Separate</button>
      </div>

      {#if combined}
      <div class="pt-4 grid grid-cols-1 gap-4">
        <figure class="highcharts-figure w-128">
            
              <div id='combined'></div>
            
        </figure>
      </div>
      {/if}
    </div>
  

</div>
