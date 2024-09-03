<script lang="ts">

  import { type RunMetrics, type ChartjsData, type Metric } from "$lib/scripts/types";
  import { TabGroup, Tab } from '@skeletonlabs/skeleton';
  import Search from "$lib/Search.svelte";
  import Fa from 'svelte-fa'
  import { faCheck, faDownload, faArrowsRotate, faMagnifyingGlassMinus } from '@fortawesome/free-solid-svg-icons'
  import IndividualChart from "$lib/card/run/IndividualCharts.svelte";
  import { onMount } from "svelte";
  import { createMetricVizData, downloadMetricCSV } from "$lib/scripts/utils";
  import { RunCardStore } from "$routes/store";
  import { get } from 'svelte/store';


  /** @type {import('./$types').PageData} */
  export let data;

  let metrics: RunMetrics;
  $: metrics = data.metrics;

  let metricNames: string[];
  $: metricNames = data.metricNames;

  let searchTerm: string | undefined;
  $: searchTerm = undefined;

  let filteredMetrics: string[] = [];
  let tabSet: string = "metrics";
  let plotSet: string = $RunCardStore.PlotSet;

  let selectedMetrics: string[];
  $: selectedMetrics = $RunCardStore.SelectedMetrics;

  let metricsToPlot: string[];
  $: metricsToPlot = $RunCardStore.MetricsToPlot;

  let searchableMetrics: string[];
  $: searchableMetrics = data.searchableMetrics;

  let metricVizData: ChartjsData | undefined;
  $: metricVizData = $RunCardStore.MetricData;

  let tableMetrics: Metric[];
  $: tableMetrics = $RunCardStore.TableMetrics;

  

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

  function render_chart(type: string) {
    plotSet = type;
  }

  function resetZoom() {
    // reset zoom
    // @ts-ignore
    window.metricChart.resetZoom();
  }

  onMount(() => {

    if (get(RunCardStore).SelectedMetrics.length === 0) {
      RunCardStore.update((store) => {
        store.SelectedMetrics = metricNames;
        return store;
      });
    } 
  });

  async function changePlotType(type: string) {
    plotSet = type;
    await refreshPlot();
  }


  async function refreshPlot() {
    if (selectedMetrics.length == 0) {
      alert("Please select metrics to plot");
      return;
    }

    // remove select all from selectedMetrics
    selectedMetrics = selectedMetrics.filter((item) => item !== 'select all');

    // get metrics to plot
    metricsToPlot = selectedMetrics.slice();

    // create metric viz data
    let newMetrics: RunMetrics = Object.fromEntries(
    Object.entries(metrics).filter(([key]) => metricsToPlot.includes(key))
  );

    metricVizData = createMetricVizData(newMetrics, plotSet);
    RunCardStore.update((store) => {
      store.MetricData = metricVizData;
      store.PlotSet = plotSet;
      store.MetricsToPlot = metricsToPlot;
      store.FilteredMetrics = filteredMetrics;
      store.SelectedMetrics = selectedMetrics;
      return store;
    });

  }


</script>

<div class="flex min-h-screen">

    {#if isOpen}
    <div class="hidden md:block flex w-1/4 pl-8 bg-surface-100 dark:bg-surface-600">
      
      <div class="flex flex-row flex-wrap gap-1 p-2 justify-between">

          <TabGroup border="" active='border-b-2 border-primary-500'>
            <Tab bind:group={tabSet} name="repos" value="metrics">Metrics</Tab>
          </TabGroup>

        <div class="flex flex-row flex-wrap gap-2 justify-between">
       
          <TabGroup border="" active='border-b-2 border-secondary-500'>
            <div><Tab bind:group={plotSet} name="bar" value="bar" on:click={() => changePlotType("bar") } >Bar</Tab></div>
            <div><Tab bind:group={plotSet} name="line" value="line" on:click={() => changePlotType("line") } >Line</Tab></div>
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
              class="chip text-xs hover:bg-primary-300 {selectedMetrics.includes(metric) ? 'bg-primary-300' : 'variant-soft'}"
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
              class="chip text-xs hover:bg-primary-300 {selectedMetrics.includes(metric) ? 'bg-primary-300' : 'variant-soft'}"
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

      <div class="flex flex-row flex-wrap gap-1 justify-between">
        <button type="button" class="m-1 btn btn-sm bg-darkpurple text-white text-xs" on:click={() => toggleSidebar() }>Hide</button>

        <div class="flex flex-row items-center">
          <button type="button" class="m-1 btn btn-sm bg-darkpurple text-white mr-2" on:click={() => downloadMetricCSV(metrics, "metrics") }>
            <Fa class="h-3" icon={faDownload}/>
            <header class="text-white text-xs">CSV</header>
          </button>
        </div>

      </div>  
    </div>
    {:else}
      <div class="hidden md:block w-16 bg-surface-100 dark:bg-surface-600">
        <div class="flex flex-row flex-wrap gap-1 p-1 justify-start">
          <button type="button" class="m-1 btn btn-sm bg-darkpurple text-white text-xs" on:click={() => toggleSidebar() }>Show</button>
        </div>
      </div>
    {/if}

    <div class="flex-col p-4 w-full bg-white dark:bg-surface-900 pr-16">

        <div class="pt-2 pb-10 relative h-3/5 rounded-2xl bg-surface-50 border-2 border-primary-500 shadow-md hover:border-secondary-500">

          <div class="flex justify-between">

            <div class="text-primary-500 text-lg font-bold pl-4 pt-1 pb-2">Metrics</div>

            <div class="flex justify-end">

              <button type="button" class="m-1 btn btn-sm bg-darkpurple text-white mr-2" on:click={() => resetZoom()}>
                <Fa class="h-3" icon={faMagnifyingGlassMinus}/>
                <header class="text-white text-xs">Reset Zoom</header>
              </button>

              <button type="button" class="m-1 btn btn-sm bg-darkpurple text-white mr-2" on:click={() => refreshPlot()}>
                <Fa class="h-3" icon={faArrowsRotate}/>
                <header class="text-white text-xs">Refresh</header>
              </button>
            </div>

          </div>  

        
          {#if metricVizData}
            <IndividualChart
              data={metricVizData.data}
              type={plotSet}
              options={metricVizData.options}
            />
          {:else}
            <div class="flex justify-center items-center h-3/5">
              <p class="text-gray-400">No metrics Found</p>
            </div>
          {/if}
       
        </div>
 
      


      <div id="table">
        <div class="mt-6">
          <div class="table-container border border-2 border-primary-500">
            <!-- Native Table Element -->
            <table class="table-compact table-hover text-xs text-center min-w-full">
              <thead class="bg-primary-200">
                <tr>
                  <th class="text-sm text-center py-2">Name</th>
                  <th class="text-sm text-center py-2">Value</th>
                  <th class="text-sm text-center py-2">Step</th>
                  <th class="text-sm text-center py-2">Timestamp</th>
                  <th class="text-sm text-center py-2">UID</th>
                </tr>
              </thead>
              <tbody>
                {#each tableMetrics as row, i}
                    <tr class="even:bg-gray-100">
                      <td class="text-sm">{row.name}</td>
                      <td class="text-sm"><span class="badge variant-soft-primary">{row.value}</span></td>
                      <td class="text-sm">{row.step}</td>
                      <td class="text-sm">{row.timestamp}</td>
                      <td class="text-sm">{row.run_uid}</td>
                    </tr>
                {/each}
          
              </tbody>
            </table>
          </div>
        </div>
      </div>

    </div>

    

</div>


