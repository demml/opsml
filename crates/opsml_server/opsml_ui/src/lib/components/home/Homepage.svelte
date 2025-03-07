<script lang="ts">
  import type { RecentCards } from "$lib/components/home/utils";
  import HomeCard from "$lib/components/home/HomeCard.svelte";

  let { cards } = $props<{
     cards: RecentCards;
  }>();

  
</script>


<!--<div class="inset-0 flex w-full px-5 flex-col items-center justify-center bg-white bg-[linear-gradient(to_right,#80808033_1px,transparent_1px),linear-gradient(to_bottom,#80808033_1px,transparent_1px)] bg-[size:70px_70px]">-->
  {#await cards}
    <div></div>
    {:then cards}
    <div class="mx-auto w-container max-w-full py-20 m500:py-14 lg:py-[100px]">
      <h2 class="mb-10 text-center text-4xl font-heading m1300:text-3xl m700:text-2xl m500:text-xl text-black font-bold">Recent Cards</h2>
      <div class="relative grid grid-cols-1 gap-6 lg:grid-cols-2 md:mx-8 justify-self-center">
        <HomeCard header="ModelCards" headerColor="text-primary-800" cardColor="bg-primary-400" cards={cards.modelcards}/>
        <HomeCard header="DataCards" headerColor="text-secondary-800" cardColor="bg-secondary-400" cards={cards.datacards}/>
        <HomeCard header="ExperimentCards" headerColor="text-tertiary-800" cardColor="bg-tertiary-400" cards={cards.experimentcards}/>
        <HomeCard header="PromptCards" headerColor="text-error-800" cardColor="bg-error-400" cards={cards.datacards}/>
      </div>
    </div>
  {/await}


