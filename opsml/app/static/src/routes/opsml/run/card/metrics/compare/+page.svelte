<script lang="ts">

  import { type Card, type RunMetrics, type CompareMetricPage, type TableMetric, type ChartjsData, type RunCard } from "$lib/scripts/types";
  import { TabGroup, Tab } from '@skeletonlabs/skeleton';
  import Search from "$lib/Search.svelte";
  import Fa from 'svelte-fa'
  import { faCheck, faDownload, faMagnifyingGlassMinus, faArrowsRotate } from '@fortawesome/free-solid-svg-icons'
  import { getRunMetrics, metricsToTable, downloadTableMetricsToCSV, createGroupMetricVizData } from "$lib/scripts/utils";
  import IndividualChart from "$lib/card/run/IndividualCharts.svelte";
  import { RunCardStore } from "$routes/store";


  /** @type {import('./$types').LayoutData} */
  export let data: CompareMetricPage;

  let searchTerm: string | undefined;
  $: searchTerm = undefined;

  let filteredMetrics: string[];
  $: filteredMetrics = $RunCardStore.FilteredMetrics;

  let tabSet: string = "metrics";

  let plotSet: string;
  $: plotSet = $RunCardStore.ComparePlotSet;

  let compareMetrics = new Map<string, RunMetrics>();
  
  let tableMetrics: Map<string, TableMetric[]>;
  $: tableMetrics = $RunCardStore.CompareTableMetrics;

  let card: RunCard;
  $: card = data.card;

  let metricNames: string[];
  $: metricNames = data.metricNames;

  let selectedMetrics: string[];
  $: selectedMetrics = $RunCardStore.CompareSelectedMetrics;

  let metricsToPlot: string[];
  $: metricsToPlot = $RunCardStore.CompareMetricsToPlot;

  let searchableMetrics: string[];
  $: searchableMetrics = data.searchableMetrics;

  let metrics: RunMetrics;
  $: metrics = data.metrics;

  let cards: Map<string, Card>;
  $: cards = data.cards;

  let cardsToCompare: string[];
  $: cardsToCompare = $RunCardStore.CompareCardsToCompare;

  let metricVizData: ChartjsData | undefined;
  $: metricVizData = $RunCardStore.CompareMetricData;

  let showTable: boolean;
  $: showTable = $RunCardStore.CompareShowTable;

  let isOpen = true;
  let cardSelectAll: boolean = false;

  let referenceMetrics: Map<string, number>;
  $: referenceMetrics = data.referenceMetrics;

  function toggleSidebar() {
    isOpen = !isOpen;
  }

  function resetZoom() {
    // reset zoom
    // @ts-ignore
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
    metricVizData = createGroupMetricVizData(compareMetrics, metricsToPlot, plotSet);
    tableMetrics = metricsToTable(compareMetrics, metricsToPlot);
    showTable = true;


    RunCardStore.update((store) => {
      store.CompareMetricData = metricVizData;
      store.ComparePlotSet = plotSet;
      store.CompareMetricsToPlot = metricsToPlot;
      store.CompareTableMetrics = tableMetrics;
      store.CompareSelectedMetrics = selectedMetrics;
      store.CompareCardsToCompare = cardsToCompare;
      store.CompareFilteredMetrics = filteredMetrics;
      store.CompareShowTable = showTable;
      return store;
    });
  }

  async function setComparedCards( cardName: string) {

    if (cardName == 'select all') {
      if (cardsToCompare.length > 0) {
        cardsToCompare = [];
        cardSelectAll = false;
      } else {
        for (let card of cards.values()) {
          cardsToCompare = [...cardsToCompare, card.uid];
        }
        cardSelectAll = true;
      }
      return;
    }
   
    if (cardsToCompare.includes(cardName)) {

      if (cardsToCompare.includes('select all')) {
        cardsToCompare = cardsToCompare.filter((item) => item !== 'select all');
      }
      cardsToCompare = cardsToCompare.filter((item) => item !== cardName);
    } else {
      cardsToCompare = [...cardsToCompare, cardName];
    }
  }

  function isNumber(value) {
    return typeof value === 'number';
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


  function downloadComparisonMetric(){
    if (tableMetrics.size == 0) {
      alert("No metrics to download. CSV download is only available after selecting runs to compare and refreshing.");
      return;
    }

    downloadTableMetricsToCSV(tableMetrics, referenceMetrics, card.uid);

  }

  
    


</script>

<div class="flex min-h-screen">

  {#if isOpen}
  <div class="hidden md:block flex-initial w-1/4 pl-8 bg-surface-100 dark:bg-surface-600">
    
    <div class="flex flex-col">
      <div class="flex flex-row flex-wrap gap-2 py-4 justify-between ">
      
        <TabGroup border="" active='border-b-2 border-primary-500'>
          <Tab bind:group={tabSet} name="repos" value="metrics">Metrics</Tab>
        </TabGroup>

        <div class="flex flex-row flex-wrap gap-2 justify-between pr-2">
      
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

          {#if cardSelectAll} 
          <input 
              class="checkbox" 
              type="checkbox" 
              checked 
              on:click={() => { setComparedCards("select all"); }}
            />
          {:else}
            <input 
            class="checkbox" 
            type="checkbox" 
            on:click={() => { setComparedCards("select all"); }}
          />

          {/if}
          </label>
        </div>

      <div class="px-2 text-darkpurple bg-primary-50 italic text-xs">select all</div> 
      </div>

      <div class="max-h-[700px]">
      {#each [...cards.values()] as card}
        <div class="inline-flex items-center overflow-scroll rounded-lg border border-dashed border-darkpurple text-xs w-fit my-1">
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

    <!-- place button in top right corner -->
    <div class="relative flex pt-3 pb-1 pr-2  items-center">
      <div class="flex-grow border-t border-gray-400"></div>
    </div> 

    <div class="flex flex-row flex-wrap gap-1 justify-between">
      <button type="button" class="m-1 btn btn-sm bg-darkpurple text-white text-xs" on:click={() => toggleSidebar() }>Hide</button>

      <div class="flex flex-row items-center">
        <button type="button" class="m-1 btn btn-sm bg-darkpurple text-white mr-2" on:click={() => downloadComparisonMetric() }>
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

    <div class="pt-2 pb-10 relative h-3/5 max-h-[512px] rounded-2xl bg-surface-50 border-2 border-primary-500 shadow-md hover:border-secondary-500">

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
          id="metricChart"
        />
      {:else}
        <div class="flex justify-center items-center h-full">
          <p class="text-gray-400">No metrics to plot</p>
        </div>
      {/if}
    </div>

    {#if showTable}
    <div id="table">
      <div class="mt-6">
        <div class="table-container border border-2 border-primary-500">
          <!-- Native Table Element -->
          <table class="table-compact table-hover text-xs text-center min-w-full">
            <thead class="bg-primary-200">
              <tr>
                <th class="text-sm text-center py-2">UID</th>
                <th class="text-sm text-center py-2">Comparison</th>
                <th class="text-sm text-center py-2">Name</th>
                <th class="text-sm text-center py-2">Value</th>
                <th class="text-sm text-center py-2">Step</th>
                <th class="text-sm text-center py-2">Result</th>
              </tr>
            </thead>
            <tbody>
              {#each tableMetrics as [key, value]}

                {#each value as row}

                    <tr class="{card.uid === key ? 'bg-primary-50' : 'even:bg-gray-100'} ">
                      <td class="text-sm">{key}</td>
                      {#if card.uid == key}
                        <td class="text-sm"><span class="badge variant-soft-primary">Current</span></td>
                      {:else}
                        <td class="text-sm"><span class="badge variant-soft-primary">Comparison</span></td>
                      {/if}
                      <td class="text-sm">{row.name}</td>
                      <td class="text-sm"><span class="badge variant-soft-primary">{row.value}</span></td>
                      <td class="text-sm">{row.step}</td>

                      {#if referenceMetrics.has(row.name)}
                        {#if isNumber(row.value)}
                          {@const referenceValue = referenceMetrics.get(row.name)}
                          {#if referenceValue !== undefined && row.value > referenceValue }
                            <td class="text-sm"><span class="badge variant-soft-success">Greater</span></td>
                          {:else if row.value === referenceMetrics.get(row.name)}
                            <td class="text-sm"><span class="badge variant-soft-primary">Equal</span></td>
                          {:else}
                            <td class="text-sm"><span class="badge variant-soft-error">Lesser</span></td>
                          {/if}
                        {:else}
                          <td class="text-sm"><span class="badge variant-soft-primary">N/A</span></td>
                        {/if}
                      {:else}
                        <td class="text-sm"><span class="badge variant-soft-primary">N/A</span></td>
                      {/if}
                    </tr>
                  
                {/each}

              {/each}
        
            </tbody>
          </table>
        </div>
      </div>
    </div>
    {/if}
  </div>
</div>
  
