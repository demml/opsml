<script lang="ts">
  import type { RecentCards } from "$lib/components/home/utils";
  import HomeCard from "$lib/components/home/HomeCard.svelte";
  import { FlaskConical, Table, BrainCircuit, NotebookText } from 'lucide-svelte';

  let { cards } = $props<{
     cards: RecentCards;
  }>();

  
</script>


<!--<div class="inset-0 flex w-full px-5 flex-col items-center justify-center bg-white bg-[linear-gradient(to_right,#80808033_1px,transparent_1px),linear-gradient(to_bottom,#80808033_1px,transparent_1px)] bg-[size:70px_70px]">-->
  {#await cards}
    <div></div>
    {:then cards}
    <div class="flex flex-col pt-18">
      <div class="flex items-center justify-center border-2 border-black bg-slate-100 p-2">
        <div class="rounded-full bg-surface-200 border-black border-2 p-1 shadow-small">
          <BrainCircuit color="#8059b6" />
        </div>
        <div class="rounded-full bg-surface-200 border-black border-2 p-1 shadow-small">
          <Table color="#5fd68d" />
        </div>
        <div class="rounded-full bg-surface-200 border-black border-2 p-1 shadow-small">
          <h2 class="text-center text-xl font-heading m1300:text-xl m700:text-xl m500:text-xl text-black font-bold">Recent</h2>
        </div>
        <div class="rounded-full bg-surface-200 border-black border-2 p-1 shadow-small">
          <NotebookText color="#f9b25e" />
        </div>
        <div class="rounded-full bg-surface-200 border-black border-2 p-1 shadow-small">
          <FlaskConical color="#f54c54" />
        </div>
      </div>
    
      <div class="mx-auto w-container grid grid-cols-1 2xl:grid-cols-2">
        <div class="max-w-full pt-4 pb-10">
          <div class="relative grid grid-cols-1 gap-6 lg:grid-cols-2 md:mx-8 justify-self-center">
            <HomeCard 
              header="Models" 
              cards={cards.modelcards}
              headerColor="bg-primary-500" 
              headerTextColor="text-black" 
              iconColor="#8059b6"
            />
            <HomeCard 
              header="Data"
              cards={cards.datacards}
              headerColor="bg-primary-500"
              headerTextColor="text-black" 
              iconColor="#8059b6"
            />
          </div>
        </div>
        <div class="max-w-full pt-4 pb-10">
          <div class="relative grid grid-cols-1 gap-6 lg:grid-cols-2 md:mx-8 justify-self-center">
            <HomeCard 
              header="Prompts" 
              cards={cards.promptcards}
              headerColor="bg-secondary-300" 
              headerTextColor="text-black" 
              iconColor="#5fd68d"
            />
            <HomeCard 
              header="Experiments"
              cards={cards.experimentcards}
              headerColor="bg-secondary-300" 
              headerTextColor="text-black"
              iconColor="#5fd68d"
            />
          </div>
        </div>
      </div>
    </div>
  {/await}

