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
    <div class="flex flex-col">
    
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

