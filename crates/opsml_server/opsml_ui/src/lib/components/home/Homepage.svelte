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

    <div class="mx-auto w-container max-w-full pt-20 pb-8 m500:pt-14 lg:pt-[100px] bg-primary-100">
      <h2 class="mb-10 text-center text-4xl font-heading m1300:text-3xl m700:text-2xl m500:text-xl text-black font-bold">Recent Cards</h2>
      <div class="relative grid grid-cols-1 gap-6 lg:grid-cols-2 md:mx-8 justify-self-center">
        <HomeCard 
          header="ModelCards" 
          cards={cards.modelcards}

          headerColor="bg-primary-500" 
          headerTextColor="text-black" 

          cardColor="bg-primary-500"
        />
        <HomeCard 
          header="DataCards"
          cards={cards.datacards}

          headerColor="bg-primary-500" 
          headerTextColor="text-black" 

          cardColor="bg-primary-500"
        />
      </div>
    </div>

    <div class="mx-auto w-container pt-4 max-w-full border-2 border-black bg-secondary-100 pb-8">
      <div class="relative grid grid-cols-1 gap-6 lg:grid-cols-2 md:mx-8 justify-self-center">
        <HomeCard 
          header="PromptCards" 
          cards={cards.modelcards}

          headerColor="bg-secondary-500" 
          headerTextColor="text-black" 

          cardColor="bg-secondary-500" 
        />
        <HomeCard 
          header="ExperimentCards"
          cards={cards.datacards}

          headerColor="bg-secondary-500" 
          headerTextColor="text-black"

          cardColor="bg-secondary-500" 
        />
      </div>
    </div>
  {/await}


