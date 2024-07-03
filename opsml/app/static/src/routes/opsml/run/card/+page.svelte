<script lang="ts">

    import { type ModelMetadata , type Card, type RunCard, type Parameter, type RunMetrics, type Metric } from "$lib/scripts/types";
    import Fa from 'svelte-fa'
    import { faTag, faIdCard, faFolderOpen, faBrain, faFile, faLink } from '@fortawesome/free-solid-svg-icons'
    import icon from '$lib/images/opsml-green.ico'
    import { goto } from '$app/navigation';
    import atomOneLight from "svelte-highlight/styles/atom-one-light";
    import Markdown from "$lib/card/Markdown.svelte";
    import FileView from "$lib/card/FileView.svelte";
    import Datatable from '$lib/components/Datatable.svelte';

  
      /** @type {import('./$types').LayoutData} */
      export let data;
  
    let hasReadme: boolean;
    $: hasReadme = data.hasReadme;
  
    let readme: string;
    $: readme = data.readme;
  
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

    let tableMetrics: Metric[];
    $: tableMetrics = data.tableMetrics;
  
  
  </script>
  
  <svelte:head>
    {@html atomOneLight}
  </svelte:head>

  
  <div class="flex flex-wrap bg-white min-h-screen mb-8">
    <div class="w-full md:w-5/12 mr-5 py-5 border-r border-grey-100 pl-4 md:pl-20">
        <header class="mb-2 text-lg font-bold">Metadata</header>
  
        <!-- UID -->
        <div class="flex flex-row gap-1 items-center">

          <div class="w-8">
            <Fa class="h-12" icon={faIdCard} color="#04cd9b"/>
          </div>
          <div class="w-32 font-semibold text-gray-500">ID:</div>
          <div class="w-48 ">
            <div class="badge h-6 border text-primary-500 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100 overflow-auto">
              {card.uid}
            </div>
          </div>
        </div>
  
        <!-- name -->
        <div class="flex flex-row gap-1 items-center">
          <div class="w-8">
            <Fa class="h-12" icon={faIdCard} color="#04cd9b"/>
          </div>
          <div class="w-32 font-semibold text-gray-500">Name:</div>
          <div class="w-48 ">
            <div class="badge h-6 border text-primary-500 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100">
              {card.name}
            </div>
          </div>
        </div>
  
        <!-- version -->
        <div class="flex flex-row gap-1 items-center">
          <div class="w-8">
            <Fa class="h-12" icon={faIdCard} color="#04cd9b"/>
          </div>
          <div class="w-32 font-semibold text-gray-500">Version:</div>
          <div class="w-48 ">
            <div class="badge h-6 border text-primary-500 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100">
              {card.version}
            </div>
          </div>
        </div>
  
        <!-- repository -->
        <div class="flex flex-row gap-1 items-center">
          <div class="w-8">
            <Fa class="h-12" icon={faFolderOpen} color="#04cd9b"/>
          </div>
          <div class="w-32 font-semibold text-gray-500">Repository:</div>
  
          <div class="w-48 ">
            <div class="badge h-6 border text-primary-500 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100">
              {card.repository}
            </div>
          </div>
        </div>
  
        <!-- datacard uid -->
        {#if card.datacard_uids.length > 0}
        <div class="flex flex-row gap-1 items-center">
          <div class="w-8">
            <Fa class="h-12" icon={faBrain} color="#04cd9b"/>
          </div>
          <div class="w-32 font-semibold text-gray-500">DataCard:</div>
          <div class="w-48 lex flex-col">

              {#each card.datacard_uids as uid}
                <div>
                  <a href="/opsml/data/card?uid={uid}" class="badge h-6 border text-primary-500 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100 overflow-auto">
                    {uid}
                  </a>
                </div>
              {/each}
    
          </div>
        </div>
        {/if}

       <!-- modelcard uid -->
       {#if card.modelcard_uids.length > 0}
       <div class="flex flex-row gap-1 items-center">
         <div class="w-8">
           <Fa class="h-12" icon={faBrain} color="#04cd9b"/>
         </div>
         <div class="w-32 font-semibold text-gray-500">ModelCard:</div>
         <div class="w-48 lex flex-col">

             {#each card.modelcard_uids as uid}
               <div>
                 <a href="/opsml/model/card?uid={uid}" class="badge h-6 border text-primary-500 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100 overflow-auto">
                   {uid}
                 </a>
               </div>
             {/each}
   
         </div>
       </div>
       {/if}

  
      <!-- tags -->
      {#if Object.keys(card.tags).length > 0}
      <div class="border-t mt-2">
  
        <div class="flex flex-row gap-1 items-center">
          <div class="w-8">
            <Fa class="h-12" icon={faTag} color="#04cd9b"/>
          </div>
          <header class="my-1 text-gray-500 text-lg font-bold">Tags</header>
        </div>

        {#each Object.keys(card.tags) as key}
          <div class="flex flex-row gap-1 items-center">
            <div class="w-32 font-semibold text-gray-500">{key}</div>
            <div class="w-48 ">
              <div class="badge h-6 border text-primary-500 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100">
                {card.tags[key]}
              </div>
            </div>
          </div>
        {/each}

      </div>
      {/if}
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

