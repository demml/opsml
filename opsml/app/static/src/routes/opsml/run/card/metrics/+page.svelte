<script lang="ts">

  import { type RunMetrics, type ChartjsData } from "$lib/scripts/types";
  import { TabGroup, Tab } from '@skeletonlabs/skeleton';
  import Search from "$lib/Search.svelte";
  import Fa from 'svelte-fa'
  import { faCheck, faChartBar, faChartLine } from '@fortawesome/free-solid-svg-icons'
  import IndividualChart from "$lib/card/run/IndividualCharts.svelte";
  import { onMount } from "svelte";
  import { createMetricVizData } from "$lib/scripts/utils";


  /** @type {import('./$types').LayoutData} */
  export let data;

  let metrics: RunMetrics;
  $: metrics = data.metrics;

  let metricNames: string[];
  $: metricNames = data.metricNames;

  let searchTerm: string | undefined;
  $: searchTerm = undefined;

  let filteredMetrics: string[] = [];
  let tabSet: string = "metrics";
  let plotSet: string = "bar";

  let selectedMetrics: string[];
  $: selectedMetrics = [];

  let metricsToPlot: string[];
  $: metricsToPlot = [];

  let combined: boolean = false;
  $: combined = false;

  let separated: boolean = false;
  $: separated = false;

  let searchableMetrics: string[];
  $: searchableMetrics = data.searchableMetrics;

  let metricVizData: Map<string, ChartjsData> = new Map();
  let metricTypes: Map<string, string> = new Map();

  export let isOpen = true;


  function toggleSidebar() {
    isOpen = !isOpen;
  }

  const searchMetrics = () => {	
		return filteredMetrics = searchableMetrics.filter(item => {
			let itemName = item.toLowerCase();
			return itemName.includes(searchTerm!.toLowerCase())
		})
	}

  async function setActiveMetrics( name: string) {

    if (name == 'select all') {
      if (selectedMetrics.length > 0) {
        selectedMetrics = [];
        combined = false;
        separated = false;
        
      } else {
        selectedMetrics = metricNames;
      }
      return;
    }

    if (selectedMetrics.includes(name)) {
      //check if select all is in selectedMetrics
      if (selectedMetrics.includes('select all')) {
        selectedMetrics = selectedMetrics.filter((item) => item !== 'select all');
      }
      
      selectedMetrics = selectedMetrics.filter((item) => item !== name);
    } else {
      selectedMetrics = [...selectedMetrics, name];
    }
  }


  async function renderIndividualCharts(){
    metricVizData = await createMetricVizData(metrics);
    separated = true;
  }
  
  onMount(async () => {
    // loop over metric keys
    Object.keys(metrics).forEach((key) => {
      // get metric data
      metricTypes.set(key, plotSet);
    });
    console.log(metricTypes);
  });

  async function render_single_chart(metric: string, type: string) {
    metricTypes.set(metric, type);
    metricVizData = await createMetricVizData(metrics);
  }

  async function separatePlots() {
    separated = true;
    combined = false;
    renderIndividualCharts();
  }

  async function combinePlots() {
    combined = true;
    separated = false;
    renderIndividualCharts();
  }

  //async function plotMetrics() {
//
  //// check combined and separated booleans
  //if (!combined && !separated) {
  //  combined = true;
  //}
//
  //// check if selectedMetrics is empty
  //if (selectedMetrics.length == 0) {
  //    alert("Please select metrics to plot");
  //    // clear plots
  //    // get div element
  //    let div = document.getElementById('combined') as HTMLElement;
  //    // clear div
  //    div.innerHTML = "";
  //    metricsToPlot = [];
//
  //    return;
  //  }
//
  //// update metricsToPlot
  //metricsToPlot = selectedMetrics.slice();
//
  //// remove "select all" from selectedMetricsCopy
  //metricsToPlot = metricsToPlot.filter((item) => item !== 'select all');
//
//}//
//
  //function combine_plots() {
  //  combined = true;
  //  separated = false;
//
  //  try {
  //    plotMetrics();
  //  } catch (error) {
  //    console.log(error);
  //  }
  //}
//
  //function separate_plots() {
  //  separated = true;
  //  combined = false;
//
  //  try {
  //    plotMetrics();
  //  } catch (error) {
  //    console.log(error);
  //  }
  //}

</script>

<div class="flex min-h-screen">


    {#if isOpen}
    <div class="hidden md:block flex-initial w-1/4 pl-8 bg-surface-100 dark:bg-surface-600">
      
      <div class="flex flex-row flex-wrap gap-1 p-2 justify-between">

        <TabGroup border="" active='border-b-2 border-primary-500'>
          <Tab bind:group={tabSet} name="repos" value="metrics">Metrics</Tab>
        </TabGroup>

        <div class="flex flex-row flex-wrap gap-2 justify-between">
       
          <TabGroup border="" active='border-b-2 border-secondary-500'>
            <div><Tab bind:group={plotSet} name="bar" value="bar">Bar</Tab></div>
            <div><Tab bind:group={plotSet} name="line" value="line">Line</Tab></div>
          </TabGroup>
        </div> 

      </div>  
      <div class="pt-2 pr-2">
        <Search bind:searchTerm on:input={searchMetrics} />
      </div>
      <div class="flex flex-wrap pt-4 pr-2 gap-1">

        {#if searchTerm && filteredMetrics.length == 0}
          <p class="text-gray-400">No metrics found</p>

        {:else if filteredMetrics.length > 0}
          {#each filteredMetrics as metric}
            
            <button
              class="chip hover:bg-primary-300 text-base {selectedMetrics.includes(metric) ? 'bg-primary-300' : 'variant-soft'}"
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
              class="chip text-sm hover:bg-primary-300 text-base {selectedMetrics.includes(metric) ? 'bg-primary-300' : 'variant-soft'}"
              on:click={() => { setActiveMetrics(metric); }}
             
            >
              {#if selectedMetrics.includes(metric)}<span><Fa icon={faCheck} /></span>{/if}
              <span>{metric}</span>
            </button>
        
          {/each}

        {/if}

      </div>

    <!-- place button in top right corner -->
    <div class="relative flex pt-3 pb-1 pr-2  items-center">
      <div class="flex-grow border-t border-gray-400"></div>
    </div> 

    <div class="flex flex-row flex-wrap gap-1 p-1 justify-start">
      <button type="button" class="chip bg-darkpurple text-white" on:click={() => toggleSidebar() }>Hide</button>
    </div>  
    </div>
    {:else}
      <div class="hidden md:block w-16 bg-surface-100 dark:bg-surface-600">
        <div class="flex flex-row flex-wrap gap-1 p-1 justify-start">
          <button type="button" class="chip bg-darkpurple text-white" on:click={() => toggleSidebar() }>Show</button>
        </div>
      </div>
    {/if}
  
    <div class="flex-auto w-64 p-4 bg-white dark:bg-surface-900 pr-16">

      <div class="flex flex-row flex-wrap gap-2">
        <button type="button" class="m-1 btn btn-sm bg-darkpurple text-white" on:click={() => combinePlots()}>Combine</button>
        <button type="button" class="m-1 btn btn-sm bg-darkpurple text-white" on:click={() => separatePlots()}>Separate</button>
      </div>


      <div id="combined charts" class="{(combined && selectedMetrics.length > 0)  ? '' : 'hidden'} pt-4">
          <figure class="w-128">
            <div class="flex flex-wrap gap-4">
              <div class="{combined ? '' : 'hidden'} w-3/4 max-w-screen-xl grow rounded-2xl bg-surface-50 border-2 border-primary-500 shadow-md hover:border-secondary-500">
                <canvas id="myChart"></canvas>
              </div>
            </div>
          </figure>
      </div>

      <div id="separate" class="{(separated && selectedMetrics.length > 0) ? '' : 'hidden'} pt-4 flex flex-wrap gap-4 min-h-screen">
        {#each metricNames as metric}
          {#if metric != 'select all'}
            <div class="{metricsToPlot.includes(metric) ? '' : 'hidden'} relative w-3/4 md:w-1/3 grow rounded-2xl bg-surface-50 border-2 border-primary-500 shadow-md hover:border-secondary-500">
              <IndividualChart
                name={metric}
                chartData={metricVizData.get(metric)?.data}
                options={metricVizData.get(metric)?.options}
                type={metricVizData.get(metric)?.type}
              />
              <div class="flex flex-row flex-wrap">
                <button type="button" class="m-1 btn btn-sm bg-darkpurple text-white" on:click={() => render_single_chart(metric, "bar")}><Fa icon={faChartBar} /></button>
                <button type="button" class="m-1 btn btn-sm bg-darkpurple text-white" on:click={() => render_single_chart(metric, "line")}><Fa icon={faChartLine} /></button>
              </div>
            </div>
          {/if}
        {/each}
      </div>
    </div>
</div>
