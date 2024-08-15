<script lang="ts">

  import { type Card, type Metric, type RunMetrics, type Graph, type CompareMetricPage, type TableMetric, type ChartjsData, type RunCard } from "$lib/scripts/types";
  import { TabGroup, Tab } from '@skeletonlabs/skeleton';
  import Search from "$lib/Search.svelte";
  import Fa from 'svelte-fa'
  import { faCheck, faDownload, faMagnifyingGlassMinus, faArrowsRotate } from '@fortawesome/free-solid-svg-icons'
  import { buildBarChart, buildLineChart} from "$lib/scripts/charts";
  import { getRunMetrics, sortMetrics, metricsToTable, downloadMetricCSV } from "$lib/scripts/utils";
  import IndividualChart from "$lib/card/run/IndividualCharts.svelte";
  import { onMount } from "svelte";

  /** @type {import('./$types').LayoutData} */
  export let data: CompareMetricPage;

  let searchTerm: string | undefined;
  $: searchTerm = undefined;

  let filteredMetrics: string[] = [];
  let tabSet: string = "metrics";
  let plotSet: string = "bar";
  let compareMetrics = new Map<string, RunMetrics>();
  let tableMetrics: Map<string, TableMetric[]>;

  let card: RunCard;
  $: card = data.card;

  let metricNames: string[];
  $: metricNames = data.metricNames;

  let selectedMetrics: string[];
  $: selectedMetrics = [];

  let metricsToPlot: string[];
  $: metricsToPlot = [];

  let searchableMetrics: string[];
  $: searchableMetrics = data.searchableMetrics;

  let metrics: RunMetrics;
  $: metrics = data.metrics;

  let cards: Map<string, Card>;
  $: cards = data.cards;

  let cardsToCompare: string[];
  $: cardsToCompare = [];

  let metricVizData: ChartjsData = data.metricVizData;
  let show: boolean = true;

  export let isOpen = true;

  function toggleSidebar() {
    isOpen = !isOpen;
  }

  function resetZoom() {
    // reset zoom
    window.metricChart.resetZoom();
  }

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

    let currentMetrics: RunMetrics = Object.fromEntries(
    Object.entries(metrics).filter(([key]) => metricsToPlot.includes(key))
    );

    // reset
    compareMetrics = new Map<string, RunMetrics>();
    compareMetrics.set(card.uid, currentMetrics);

    if (cardsToCompare.length > 0) {
      for (let uid of cardsToCompare) {

        let cardMetrics = await getRunMetrics(uid, metricsToPlot)
        compareMetrics.set(uid, cardMetrics);
      }
    }

    console.log(compareMetrics);
  }

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


  onMount(() => {
    selectedMetrics = metricNames;
  });

  
    


</script>

<div class="flex min-h-screen">

  {#if isOpen}
  <div class="hidden md:block flex-initial w-1/4 pl-8 bg-surface-100 dark:bg-surface-600">
    
    <div class="flex flex-col">
      <div class="flex flex-row flex-wrap gap-2 py-4 justify-between ">
      
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

    </div>

    <div class="pt-2">
      <TabGroup border="" active='border-b-2 border-primary-500 text-sm'>
        <Tab bind:group={tabSet} name="repos" value="metrics">Compare Previous Runs</Tab>
      </TabGroup>
    </div>

      
    <div class="flex flex-col pt-2 overflow-scroll">
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


      <div class="px-2 text-darkpurple bg-primary-50 italic text-xs">select all</div> 
      </div>
      {#each [...cards.values()] as card}
        <div class="inline-flex items-center overflow-hidden rounded-lg border border-dashed border-darkpurple text-xs w-fit my-1">
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

  {#if show}
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

         <IndividualChart
          data={metricVizData.data}
          type={plotSet}
          options={metricVizData.options}
        />
  
      </div>
    </div>
  {/if}
</div>
  
