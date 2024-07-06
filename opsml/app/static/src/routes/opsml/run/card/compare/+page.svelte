<script lang="ts">

  import { type ModelMetadata , type Card, type RunCard, type Parameter, type Metric, type RunMetrics, type Graph } from "$lib/scripts/types";
  import { TabGroup, Tab } from '@skeletonlabs/skeleton';
  import Search from "$lib/Search.svelte";
  import Fa from 'svelte-fa'
  import { faCheck, faChartBar, faChartLine } from '@fortawesome/free-solid-svg-icons'
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
  let plotSet: string = "bar";

  let selectedMetrics: string[];
  $: selectedMetrics = [];

  let metricsToPlot: string[];
  $: metricsToPlot = [];

  let metricPlotSettings: Map<string, Graph>;
  $: metricPlotSettings = new Map<string, Graph>();

  let combined: boolean = false;
  $: combined = false;

  let separated: boolean = false;
  $: separated = false;

  let searchableMetrics: string[];
  $: searchableMetrics = data.searchableMetrics;


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


  async function plot() {

    // check combined and separated booleans
    if (!combined && !separated) {
      combined = true;
    }

    // check if selectedMetrics is empty
    if (selectedMetrics.length == 0) {
      alert("Please select metrics to plot");
      // clear plots
      // get div element
      let div = document.getElementById('combined') as HTMLElement;
      // clear div
      div.innerHTML = "";
      metricsToPlot = [];

      return;
    }

    // update metricsToPlot
    metricsToPlot = selectedMetrics.slice();
    // remove "select all" from selectedMetricsCopy
    metricsToPlot = metricsToPlot.filter((item) => item !== 'select all');


    if (combined) {

      const y: Map<string, number[]> = new Map<string, number[]>();
      const x: Map<string, number[]> = new Map<string, number[]>();


      if (plotSet === "line") {
        for (let metric of metricsToPlot) {

          // get metric from metrics
          let metricData = metrics[metric];
          y.set(metricData[0].name, []);
          x.set(metricData[0].name, []);


          for (let data of metricData) {
            y.get(metricData[0].name)!.push(data.value);
            x.get(metricData[0].name)!.push(data.step || 0);
          }
        }

      
        let graph: Graph = {
          name: "combined",
          x_label: "Step",
          y_label: "Value",
          x,
          y,
          graph_type: "line",
          graph_style: "combined",
        }
        buildLineChart(graph, (9 / 16 * 100) + '%');
      
      } else {
          for (let metric of metricsToPlot) {

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

          
          buildBarChart(graph,  (9 / 16 * 100) + '%');
        
            }
      return;

    } else {
      for (let metric of metricsToPlot) {

        if (metricPlotSettings.has(metric)) {
          // get graphType
          let graphType = metricPlotSettings.get(metric)!.graph_type;

          if (graphType == "line") {
            buildLineChart(metricPlotSettings.get(metric)!, undefined);
          } else {
            buildBarChart(metricPlotSettings.get(metric)!, undefined);
          }
        } else {
          // get metric from metrics

        if (plotSet === "line") {
          let metricData = metrics[metric];
          const y = new Map<string, number[]>();
          const x = new Map<string, number[]>();

          y.set(metricData[0].name, []);
          x.set(metricData[0].name, []);


          for (let data of metricData) {
            y.get(metricData[0].name)!.push(data.value);
            x.get(metricData[0].name)!.push(data.step || 0);
          }

          let graph: Graph = {
            name: metric,
            x_label: "Step",
            y_label: "Value",
            x,
            y,
            graph_type: "line",
            graph_style: "separate",
          }

          buildLineChart(graph, undefined);
          metricPlotSettings.set(metric, graph);


        } else {
          // get metric from metrics
        let metricData = metrics[metric];
        let graph: Graph = {
          name: metric,
          x_label: "Group",
          y_label: "Value",
          x: [0],
          y: new Map([[metricData[0].name, [metricData[metricData.length - 1].value]]]),
          graph_type: "bar",
          graph_style: "separate",
          }

        buildBarChart(graph, undefined);
        metricPlotSettings.set(metric, graph);
          }
        }
      }
      return;
     }
    }

  async function combine_plots() {
    combined = true;
    separated = false;
    try {
      plot();
    } catch (error) {
      combined = false;
    }
  }

  async function separate_plots() {
    combined = false;
    separated = true;
    try {
      plot();
    } catch (error) {
      separated = false;
    }
  }

</script>

<div class="flex min-h-screen">
  <div class="hidden md:block flex-initial w-1/5 pl-12 bg-surface-100 dark:bg-surface-600">
    

      <div class="flex flex-row flex-wrap gap-2 p-4 justify-between ">
       
        <TabGroup border="" active='border-b-2 border-primary-500'>
          <Tab bind:group={tabSet} name="repos" value="metrics">Metrics</Tab>
        </TabGroup>
        <button type="button" class="m-1 btn btn-sm bg-darkpurple text-white" on:click={() => plot()}>Show</button>

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
             
            >
              {#if selectedMetrics.includes(metric)}<span><Fa icon={faCheck} /></span>{/if}
              <span>{metric}</span>
            </button>
        
          {/each}

        {/if}

      </div>

      <div class="flex flex-row flex-wrap gap-2 p-2 justify-between ">
       
        <TabGroup border="" active='border-b-2 border-secondary-500'>
          <div><Tab bind:group={plotSet} name="set1" value="bar">Bar</Tab></div>
          <div><Tab bind:group={plotSet} name="set2" value="line">Line</Tab></div>
        </TabGroup>
      </div> 
 
    </div>
  
    <div class="flex-auto w-64 p-4 bg-white dark:bg-surface-900 pr-16">

      <div class="flex flex-row flex-wrap gap-2">
        <button type="button" class="m-1 btn btn-sm bg-darkpurple text-white" on:click={() => combine_plots()}>Combined</button>
        <button type="button" class="m-1 btn btn-sm bg-darkpurple text-white" on:click={() => separate_plots()}>Separate</button>
      </div>


      <div id="combined charts" class="{combined ? '' : 'hidden'} pt-4">
          <figure class="highcharts-figure w-128">
            <div class="flex flex-wrap gap-4">
              <div class="{combined ? '' : 'hidden'} w-3/4 max-w-screen-xl grow rounded-2xl bg-surface-50 border-2 border-primary-500 shadow-md hover:border-secondary-500">
                <div id='combined'></div>
              </div>
            </div>
          </figure>
      </div>

      <div id="separate" class="{separated ? '' : 'hidden'} pt-4">
          <figure class="highcharts-figure w-128">
            <div class="flex flex-wrap gap-4">
              {#each metricNames as metric}
                  <div class="{metricsToPlot.includes(metric) ? '' : 'hidden'} w-3/4 md:w-1/4 grow rounded-2xl bg-surface-50 border-2 border-primary-500 shadow-md hover:border-secondary-500">
                    <div id={metric}></div>
                    <div class="flex flex-row flex-wrap">
                      <button type="button" class="m-1 btn btn-sm bg-darkpurple text-white" on:click={() => render_single_chart(metrics[metric], "bar", "separated", undefined)}><Fa icon={faChartBar} /></button>
                      <button type="button" class="m-1 btn btn-sm bg-darkpurple text-white" on:click={() => render_single_chart(metrics[metric], "line", "separated", undefined)}><Fa icon={faChartLine} /></button>
                    </div>

                  </div>
              {/each}
            </div>
          </figure>
      </div>
      


    


    </div>
</div>
