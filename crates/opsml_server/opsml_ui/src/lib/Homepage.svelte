<script lang="ts">
  import logo from "$lib/images/opsml-logo.png";
  import type { RecentCards } from "$lib/scripts/homepage";
  import HomeSpan from "$lib/Homepage_span.svelte";
  import Card from "$lib/Card.svelte";

  export let cards: RecentCards;

</script>

<div class="min-h-screen bg-gradient-to-b from-surface-500 via-secondary-200 via-70% to-white" id="active-page">

  <div class="container mx-auto mb-4 pt-12 sm:mb-4 sm:pt-20">
    <div class="mb-10 flex items-center justify-center gap-2 text-xl font-bold sm:mb-8 text-primary-500">
        <div class="mr-2 h-px flex-1 translate-y-px bg-gradient-to-l from-primary-500 to-white"></div>
          <div class="text-slate-100">Recent </div><img src={logo} class="w-20" alt=""> <div class="text-slate-100"> Assets</div>
        <div class="ml-2 h-px flex-1 translate-y-px bg-gradient-to-r from-primary-500 to-white"></div>
    </div>

     {#await cards}
      <div></div>
      {:then cards}

        <div class="relative grid grid-cols-1 gap-6 lg:grid-cols-3">
          <HomeSpan header="ModelCards" >
            {#if cards.modelcards.length > 0}
              {#each cards.modelcards as modelcard}
                <Card
                  hoverColor="hover:text-primary-500 hover:bg-slate-100"
                  hoverBorderColor="hover:border-primary-500"
                  repository= {modelcard.repository}
                  name= {modelcard.name}
                  version= {modelcard.version}
                  timestamp= {modelcard.timestamp}
                  svgClass="flex-none w-3 mr-0.5 fill-primary-600 dark:fill-primary-200"
                  registry= "model"
                />
              {/each}
            {:else}
              <div class="col-span-full text-center text-lg font-bold text-primary-500">No recent assets</div>
            {/if}
          </HomeSpan>
          
          <HomeSpan header="DataCards" >
            {#if cards.datacards.length > 0}
              {#each cards.datacards as datacard}
                <Card
                  hoverColor=hover:text-secondary-600
                  hoverBorderColor="hover:border-secondary-600"
                  svgClass="flex-none w-3 mr-0.5 fill-secondary-600"
                  repository= {datacard.repository}
                  name= {datacard.name}
                  version= {datacard.version}
                  timestamp= {datacard.timestamp}
                  registry= "data"
                />
              {/each}
            {:else}
              <div class="col-span-full text-center text-lg font-bold text-primary-500">No recent assets</div>
            {/if}
          </HomeSpan>

          <HomeSpan header="RunCards" >
            {#if cards.runcards.length > 0}
              {#each cards.runcards as runcard}
                <Card
                  hoverColor=hover:text-error-600
                  hoverBorderColor="hover:border-error-600"
                  svgClass="flex-none w-3 mr-0.5 fill-error-600"
                  repository= {runcard.repository}
                  name= {runcard.name}
                  version= {runcard.version}
                  timestamp= {runcard.timestamp}
                  registry= "run"
                />
              {/each}
            {:else}
              <div class="col-span-full text-center text-lg font-bold text-primary-500">No recent assets</div>
            {/if}
          </HomeSpan>
        </div>
      {/await}
  </div>
</div>
