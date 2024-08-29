<script lang="ts">

  import { type Card, type RunCard, type Parameter, type RunMetrics, type Metric } from "$lib/scripts/types";
  import atomOneLight from "svelte-highlight/styles/atom-one-light";
  import Datatable from '$lib/components/Datatable.svelte';
  import Metadata from "$lib/card/run/Metadata.svelte";


  /** @type {import('./$types').LayoutData} */
  export let data;


  let card: Card;
  $: card = data.card;

  let metadata: RunCard;
  $: metadata = data.metadata;

  let metricNames: string[];
  $: metricNames = data.metricNames;

  let parameters: Parameter[];
  $: parameters = data.parameters;

  let tableMetrics: Metric[];
  $: tableMetrics = data.tableMetrics;

  
  </script>
  
  <svelte:head>
    {@html atomOneLight}
  </svelte:head>

  <div class="flex flex-wrap bg-white min-h-screen mb-8">

    <div class="w-full md:w-2/5 mt-4 ml-4 pl-2 md:ml-12">
      <div class="p-4">
        <Metadata 
          metadata={metadata} 
          card={card} 
        />
      </div>
    </div>

  {#if tableMetrics.length > 0 || parameters.length > 0}

    <div class="flex flex-col w-full md:w-6/12 mt-5">

      {#if metricNames.length > 0}
        <div class="pl-4 pr-4">
          <Datatable 
            data={tableMetrics}
            forMetric={true}
          />
        </div>
      {/if}

      {#if parameters.length > 0}
        <div class="pl-4 pr-4">
          <Datatable 
            data={parameters}
            forMetric={false}
            label="Parameters"
          />
        </div>
      {/if}

    </div>

  {:else}
    <div class="flex flex-col w-full md:w-5/12 mt-5">
      <div class="pl-4 pr-4">
        <div class="text-lg font-bold mt-6">No metrics or parameters found</div>
      </div>
    </div>
  {/if}
</div>

