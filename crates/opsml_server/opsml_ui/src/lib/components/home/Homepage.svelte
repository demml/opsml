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
    <div class="flex flex-col pt-13">
      <div class="flex items-center justify-center border-2 border-black bg-slate-100 p-2">
        <div class="rounded-full bg-surface-200 border-black border-2 p-1 shadow-small">
          <BrainCircuit color="#8059b6" />
        </div>
        <div class="rounded-full bg-surface-200 border-black border-2 p-1 shadow-small">
          <Table color="#5fd68d" />
        </div>
        <div class="rounded-full bg-surface-200 border-black border-2 p-1 shadow-small">
          <h2 class="text-center font-heading text-black font-bold">Recent</h2>
        </div>
        <div class="rounded-full bg-surface-200 border-black border-2 p-1 shadow-small">
          <NotebookText color="#f9b25e" />
        </div>
        <div class="rounded-full bg-surface-200 border-black border-2 p-1 shadow-small">
          <FlaskConical color="#f54c54" />
        </div>
      </div>
    
      <div class="mx-auto w-10/12 pt-4 pb-10">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 mx-4 md:mx-8">
          <!-- First row on large screens: Models and Data -->
          <HomeCard 
            header="Models" 
            cards={cards.modelcards}
            headerColor="bg-primary-500" 
            headerTextColor="text-black" 
            iconColor="#8059b6"
            badgeColor="#8059b6"
          />
          <HomeCard 
            header="Data"
            cards={cards.datacards}
            headerColor="bg-primary-500"
            headerTextColor="text-black" 
            iconColor="#8059b6"
            badgeColor="#5fd68d"
          />
          
          <!-- Second row on large screens: Prompts and Experiments -->
          <HomeCard 
            header="Prompts" 
            cards={cards.promptcards}
            headerColor="bg-secondary-300" 
            headerTextColor="text-black" 
            iconColor="#5fd68d"
            badgeColor="#f9b25e"
          />
          <HomeCard 
            header="Experiments"
            cards={cards.experimentcards}
            headerColor="bg-secondary-300" 
            headerTextColor="text-black"
            iconColor="#5fd68d"
            badgeColor="#f54c54"
          />
        </div>
      </div>
    </div>
  {/await}

