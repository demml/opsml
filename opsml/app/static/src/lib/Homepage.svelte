<script lang="ts">
  import logo from "$lib/images/opsml-logo.png";
  import modelcard from "$lib/images/modelcard-circuit.svg";
  import type { RecentCards } from "$lib/scripts/homepage";
  import HomeSpan from "$lib/Homepage_span.svelte";
  import Card from "$lib/Card.svelte";

  export let cards: RecentCards;

</script>

<div id="active-page">

  <div class="container mx-auto mb-4 pt-12 sm:mb-4 sm:pt-20">
    <div class="mb-10 flex items-center justify-center gap-2 text-xl font-bold sm:mb-8">
        <div class="mr-2 h-px flex-1 translate-y-px bg-gradient-to-l from-primary-500 to-white"></div>
          Recent <img src={logo} class="w-12" alt=""> Assets
        <div class="ml-2 h-px flex-1 translate-y-px bg-gradient-to-r from-primary-500 to-white"></div>
    </div>

    <div class="relative grid grid-cols-1 gap-6 lg:grid-cols-3">

      <HomeSpan header="ModelCards" >
        {#await cards}
          <div>Loading...</div>
        {:then cards}
          {#each cards.modelcards as modelcard}
            <Card
              hoverColor="hover:text-primary-500 dark:hover:text-primary-500"
              hoverBorderColor="hover:border-primary-500"
              repository= {modelcard.repository}
              name= {modelcard.name}
              version= {modelcard.version}
              timestamp= {modelcard.timestamp}
              svgClass="flex-none w-3 mr-0.5 fill-primary-600 dark:fill-primary-200"
              registry= "model"
            />
          {/each}
        {/await}
      </HomeSpan>

      <HomeSpan header="DataCards" >
        {#await cards}
          <div>Loading...</div>
        {:then cards}
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
        {/await}
      </HomeSpan>

      <HomeSpan header="RunCards" >
        {#await cards}
          <div>Loading...</div>
        {:then cards}
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
        {/await}
      </HomeSpan>

    </div>
  </div>

</div>
