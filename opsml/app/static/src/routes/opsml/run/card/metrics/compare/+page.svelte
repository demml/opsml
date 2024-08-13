<script lang="ts">

  import { type ModelMetadata , type Card, type RunCard, type Parameter, type Metric, type RunMetrics, type Graph, CardRegistries, type CardRequest, type CardResponse, type CompareMetricPage, CommonPaths, type Metrics, type TableMetric } from "$lib/scripts/types";
  import { listCards } from "$lib/scripts/utils";
  import { TabGroup, Tab } from '@skeletonlabs/skeleton';
  import Search from "$lib/Search.svelte";
  import Fa from 'svelte-fa'
  import { faCheck, faChartBar, faChartLine } from '@fortawesome/free-solid-svg-icons'
  import { buildBarChart, buildLineChart} from "$lib/scripts/charts";
  import { keys } from "highcharts";
  import { apiHandler } from "$lib/scripts/apiHandler";
  import { getRunMetrics, sortMetrics, metricsToTable } from "$lib/scripts/utils";



  /** @type {import('./$types').LayoutData} */
  export let data: CompareMetricPage;

  let searchTerm: string | undefined;
  $: searchTerm = undefined;

  let filteredMetrics: string[] = [];
  let tabSet: string = "metrics";
  let plotSet: string = "bar";
  let compareMetrics = new Map<string, RunMetrics>();
  let tableMetrics: Map<string, TableMetric[]>;

  let metricNames: string[];
  $: metricNames = data.metricNames;

  let selectedMetrics: string[];
  $: selectedMetrics = [];

  let metricsToPlot: string[];
  $: metricsToPlot = [];

  let metricPlotSettings: Map<string, Graph>;
  $: metricPlotSettings = new Map<string, Graph>();

  let plot: boolean = false;
  $: plot = false;

  let searchableMetrics: string[];
  $: searchableMetrics = data.searchableMetrics;

  let metrics: RunMetrics;
  $: metrics = data.metrics;

  let cards: Map<string, Card>;
  $: cards = data.cards;

  let cardsToCompare: string[];
  $: cardsToCompare = [];

  async function setComparedCards( cardName: string) {

    if (cardName == 'select_all') {
      if (cardsToCompare.length > 0) {
        cardsToCompare = [];
      } else {
        for (let card of cards.values()) {
          cardsToCompare = [...cardsToCompare, card.uid];
        }
      }
      return;
    }
   
    if (cardsToCompare.includes(cardName)) {

      if (cardsToCompare.includes('select_all')) {
        cardsToCompare = cardsToCompare.filter((item) => item !== 'select_all');
      }
      cardsToCompare = cardsToCompare.filter((item) => item !== cardName);
    } else {
      cardsToCompare = [...cardsToCompare, cardName];
    }
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
        plot = false;
        
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

  function render_single_chart(
    metrics: Metric[],
    type: string,
    style: string,
    height: string | undefined
  ) {
    // get metric name from first in list
    const metricName: string = metrics[0].name;

    // create x and y maps for metricName
    const y: Map<string, number[]> = new Map();
    const x: Map<string, number[]> = new Map();

    y.set(metricName, []);
    x.set(metricName, []);

    for (let metric of metrics) {
      const metricName = metric.name;
      y.get(metricName)!.push(metric.value);
      x.get(metricName)!.push(metric.step || 0);
    }

    let graph: Graph = {
      name: metricName,
      x_label: "Step",
      y_label: "Value",
      x,
      y,
      graph_style: style,
      graph_type: type,
    };

    if (type === "bar") {
      buildBarChart(graph, height);
    } else if (type === "line") {
      buildLineChart(graph, height);
    }

    metricPlotSettings.set(metricName, graph);
  }


  async function plot_metrics() {
  

    // check if selectedMetrics is empty
    if (selectedMetrics.length == 0) {
      alert("Please select metrics to plot");
      return;
    }
    // get select metric for all cards in cardsToCompare

    if (cardsToCompare.length == 0)
      {
        return;
      }


    // update metricsToPlot
    metricsToPlot = selectedMetrics.slice();
    
    // remove select all from metricsToPlot
    metricsToPlot = metricsToPlot.filter((item) => item !== 'select all');
    let compareMetrics = new Map<string, RunMetrics>();

    // reset compareMetrics
    compareMetrics = new Map<string, RunMetrics>();
    for (let card of cardsToCompare) {
      let cardMetrics: RunMetrics = sortMetrics(await getRunMetrics(card, metricsToPlot));
      compareMetrics.set(card, cardMetrics);
    }

    //parse for table

    // get metrics for each card
    //plot = true;
    tableMetrics = metricsToTable(compareMetrics, metricsToPlot);
    plot = true;
    return;
    }

  
    


</script>

<div class="flex min-h-screen">
  <div class="hidden md:block flex-initial w-1/4 pl-8 bg-surface-100 dark:bg-surface-600">
    
      <div class="flex flex-col">
        <div class="flex flex-row flex-wrap gap-2 py-4 justify-between ">
        
          <TabGroup border="" active='border-b-2 border-primary-500'>
            <Tab bind:group={tabSet} name="repos" value="metrics">Metrics</Tab>
          </TabGroup>

          <div class="flex flex-row flex-wrap gap-2 justify-between">
       
            <TabGroup border="" active='border-b-2 border-secondary-500'>
              <div><Tab bind:group={plotSet} name="set1" value="bar">Bar</Tab></div>
              <div><Tab bind:group={plotSet} name="set2" value="line">Line</Tab></div>
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
                class="chip hover:bg-primary-300 text-sm {selectedMetrics.includes(metric) ? 'bg-primary-300' : 'variant-soft'}"
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
                class="chip hover:bg-primary-300 text-sm {selectedMetrics.includes(metric) ? 'bg-primary-300' : 'variant-soft'}"
                on:click={() => { setActiveMetrics(metric); }}
              
              >
                {#if selectedMetrics.includes(metric)}<span><Fa icon={faCheck} /></span>{/if}
                <span>{metric}</span>
              </button>
          
            {/each}

          {/if}

        </div>
  
      </div>

      <div class="pt-2">
        <TabGroup border="" active='border-b-2 border-primary-500'>
          <Tab bind:group={tabSet} name="repos" value="metrics">Compare Previous Runs</Tab>
        </TabGroup>
      </div>

      
      <div class="flex flex-col pt-2">
        <div class="inline-flex items-center overflow-hidden text-sm w-fit my-1">
          <div>
            <label class="flex items-center p-1 ">
            <input 
                class="checkbox" 
                type="checkbox" 
                on:click={() => { setComparedCards("select_all"); }}
                
              />
            </label>
          </div>


        <div class="px-2 text-darkpurple bg-primary-50 italic">select all</div> 
        </div>
        {#each [...cards.values()] as card}
          <div class="inline-flex items-center overflow-hidden rounded-lg border border-dashed border-darkpurple text-sm w-fit my-1">
            <div>
              <label class="flex items-center p-1 ">
                
                {#if cardsToCompare.includes(card.uid)}
                <input 
                  class="checkbox" 
                  type="checkbox" 
                  checked
                  on:click={() => { setComparedCards(card.uid); }}
                
                />
                {:else}
                <input 
                  class="checkbox" 
                  type="checkbox" 
                  on:click={() => { setComparedCards(card.uid); }}
                
                />
                {/if}
              
              </label>
            </div>
            <div class="border-r border-darkpurple px-2 text-darkpurple bg-primary-50 italic">{card.name}</div> 
            <div class="flex px-1.5 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100 text-darkpurple">
              {card.date}
            </div>
          </div>

        {/each}
       
      </div>

    </div>
  
    <div class="flex-auto w-64 p-4 bg-white dark:bg-surface-900 pr-16">

      <div class="flex flex-row flex-wrap gap-2">
        <button type="button" class="m-1 btn btn-sm bg-darkpurple text-white" on:click={() => plot_metrics()}>Plot</button>
      </div>


      <div id="compare charts" class="{(plot && selectedMetrics.length > 0) ? '' : 'hidden'} pt-4">
          <figure class="highcharts-figure w-128">
            <div class="flex flex-wrap gap-4">
              <div class="{plot ? '' : 'hidden'} w-3/4 max-w-screen-xl grow rounded-2xl bg-surface-50 border-2 border-primary-500 shadow-md hover:border-secondary-500">
                <div id='compare_metrics'></div>
              </div>
            </div>
          </figure>
      </div>



      {#if plot}
        <div class="mt-2">
          <div class="table-container border border-2 border-primary-500">
            <!-- Native Table Element -->
            <table class="table-compact table-compact table-hover text-xs text-center min-w-full">
              <thead class="bg-surface-200">
                <tr>
                  <th class="text-sm text-center py-2">Name</th>
                  {#each metricsToPlot as row}
                    <th class="text-sm text-center py-2">{row}</th>
                  {/each}
                </tr>
              </thead>
              <tbody>
                {#each tableMetrics as row}
               
                <tr class="text-xs">
                    <td>{row[0]}</td>
                    {#each row[1] as cell}
                      <td><span class="badge variant-soft-primary">{cell.value}</span></td>
                    {/each}
                </tr>
                {/each}
         
              </tbody>
            </table>
          </div>
        </div>
      {/if}
    </div>
</div>
